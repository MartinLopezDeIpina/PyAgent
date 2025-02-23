from doctest import debug

from langchain_core.language_models import BaseChatModel
from pydantic import Field
from typing import Optional, Any, Sequence, List, Literal
import requests
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage, ToolCall, BaseMessage
from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import LLMResult
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.tools import tool, Tool, StructuredTool
import json

from models import ToolCallAction
from services.agents.tools import ToolManager
from validation_utils import AgentValidator

initial_prompt_template_str="""{general_instructions}

Solve the question answering task with interleaving Think, Action, Observation steps. The action represents the called tool, and the observation represents the tool's output. You task is to identify the next action based on the observation and the thinking process.

You have {num_tools} possible actions, always think about the best option, only choose one option, answer with the ANSWER tool when you are sure of the result: 
{tools_info}

Your response must contain the action to perform after the thinking process. The action must be in the following json format, inside de \\boxed{{}}, even if the action is the final answer. Remember to use exactly de specified tool schema: 
    \\boxed{{"action": "name_of_the_action_to_perform", "args": {{//required args}}}}

For example, for the action "ANSWER" with the argument "value" with value "000.000", the json would be:
    \\boxed{{"action": "ANSWER", "args": {{"value": "000.000"}}}}

The question is: {question}
Begin!"""

class ReactAgent:
    def create_initial_message(self):
        tools_info = "\n".join([
                                   f"{i + 1}. {tool.name.upper()}: {tool.description}"
                                   for i, tool in enumerate(self.tools)])

        initial_message_template = HumanMessagePromptTemplate.from_template(initial_prompt_template_str)
        initial_message = initial_message_template.format(
            general_instructions=self.general_instructions,
            tools_info=tools_info,
            num_tools=len(self.tools),
            question=self.question
        )

        return initial_message

    def __init__(
            self,
            llm: BaseChatModel,
            general_instructions: str,
            tools: List[StructuredTool],
            max_messages: int = 7
    ):
        self.llm = llm.bind_tools(tools)
        self.general_instructions = general_instructions,
        self.tools = tools
        self.finished = False
        self.messages = []
        self.validator = AgentValidator()
        self.max_messages = max_messages

    def is_finished(self):
        return self.finished

    async def run(self, question: str, reset=True):
        self.question = question

        if reset:
            self.messages = []
            self.messages.append(self.create_initial_message())
            self.validation_errors = 0

            self.finished = False

        while not self.is_finished():
            await self.step()

        return self.messages

    def forward(self)-> List[BaseMessage]:
        action = None
        self.validator.reset_attempts()

        while not action:
            print("Forwarding message")
            response = self.llm.invoke(self.messages)
            print(f"Response: {response}")

            action = self.validator.validate_response(response, self.tools)

        new_messages = []

        new_messages.append(response)
        if action.action.lower() == "answer" or action.action.lower() == "error":
            self.finished = True
            message = AIMessage(f"{action.args['value']}")
            new_messages.append(message)
        else:
            tool = self.validator.get_tool_by_name(self.tools, action.action)
            tool_args = action.args
            message = ToolCallAction(
                tool_name = tool.name,
                tool_args = tool_args
            )
            new_messages.append(message)

        return new_messages

    async def step(self):
        new_messages = self.forward()
        print(f"New messages: {new_messages}")
        self.messages.extend(new_messages)

        if len(self.messages) > self.max_messages:
            self.finished = True

        if type(self.messages[-1]) == ToolCallAction:
            tool_response = await self.execute_tool(self.messages[-1])
            self.messages.append(ToolMessage(content=tool_response, tool_call_id=len(self.messages)))

    async def execute_tool(self, tool_call: ToolCallAction) -> Any:
        try:
            tool = None
            for t in self.tools:
                if t.name == tool_call.tool_name:
                    tool = t
                    break

            result = await tool.invoke(input=tool_call.tool_args)
            value = result.content[0].text

            return value

        except Exception as e:
            return f"Error ejecutando la herramienta: {str(e)}"


class AnalyzerAgent(ReactAgent):
    def __init__(self, llm: BaseChatModel, tool_manager: ToolManager):
        tool_names = ["library_docs_rag", "create_problem_solving_steps"]
        tools = tool_manager.get_tool_instances(tool_names)

        general_instructions = """You are a planner agent, your task is to create a step-by-step list to solve a python problem.
        You need to choose which of the possible python libraries to use in order to solve the problem, if it is not necessary then do not choose any library.
        After selecting the libraries, you must call the tool to make a rag in the library's documentation. The rag operation will generate a couple of documents, from which you will need to select the useful ones and include their description in the final plan.
        
        To sum up: 
            - Define the steps to solve the problem in natural language.
            - Choose the libraries (if any) to use. 
            - Retrieve the libraries docs.
            - Decide what classes / functions are useful
            - Call the final answer with the steps, useful docs and explanation.
        """
        super().__init__(llm=llm, tools=tools, general_instructions=general_instructions)
