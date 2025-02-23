from typing import List, TypedDict

from langgraph.graph import START, StateGraph

from client import MCPClient
from services.agents.colab_llm import CustomColabLLM
from services.agents.react_agent import AnalyzerAgent
from services.agents.tools import ToolManager

mcp_client = MCPClient()
tool_manager = ToolManager(mcp_client)

class State(TypedDict):
    problem_definition: str
    steps: List[str]
    libraries_to_use: List[str]
    library_docs: List[str]


def analyzer_agent(state: State):
    llm = CustomColabLLM(colab_url="url_todo")
    agent = AnalyzerAgent(llm, tool_manager)
    result = agent.run(state["problem_definition"])

    return {"result": result}

def print_result(state: State):
    result = state["result"]
    print(result)
    return state


if __name__ == '__main__':
    state = {
        "problem_definition": "Get the average values from two numpy arrays `old_set` and `new_set`",
        "steps": [],
        "libraries_to_use": [],
        "library_docs": [],
        "result": None
    }

    graph_builder = StateGraph(State)

    graph_builder.add_node(analyzer_agent)
    graph_builder.add_node(print_result)

    graph_builder.add_edge(START, "analyzer_agent")
    graph_builder.add_edge("analyzer_agent", "print_result")



