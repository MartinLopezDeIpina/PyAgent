from services.agents.react_agent import ReactAgent

general_instructions = """You are a python coding analyer, your task is to generate a step-by-step short guide on how to solve the provided problem. 
You must answer with a list of 1-5 steps.
If the solution requires a specific library, you must search for the library's documentation with the provided tool.
"""

class AnalyzerAgent(ReactAgent):
    def __init__(
            self,
            llm: BaseChatModel,
    ):

        super().__init__(llm, general_instructions, tools)

    async def step(self):
        pass