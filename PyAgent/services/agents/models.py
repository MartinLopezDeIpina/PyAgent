from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field, conlist
from typing import Literal, List

class ToolCallAction(BaseMessage):
    type: str = "tool_call"
    content: str
    tool_name: str
    tool_args: dict

    @classmethod
    def __create__(cls, content: str, tool_name: str, tool_args: dict) -> "ToolCallAction":
        return cls(
            content=content,
            tool_name=tool_name,
            tool_args=tool_args
        )

class Action(BaseModel):
    action: str = Field(title="Action", description="Action to perform")
    args: dict = Field(title="Arguments", description="Arguments for the action")

class SimpleSchemaArgs(BaseModel):
    @classmethod
    def get_simple_schema(cls) -> dict:
        schema = cls.model_json_schema()["properties"]
        for name, value in schema.items():
            value.pop("title")
        return schema

LibraryNames = Literal["pandas", "numpy", "re", "operator", "itertools", "random", "math", "collections", "functools", "sklearn", "datetime", "scipy"]

class StackoverflowQuery(SimpleSchemaArgs):
    query: str = Field(description="Query to search in Stackoverflow for similar results.")

class LibraryDocsRAG(SimpleSchemaArgs):
    library_name: str = Field(description="Name of the library.")
    query: str = Field(description="Query that represents the reason to use the library.")

class LibraryDocsInfo(SimpleSchemaArgs):
    library_name: str = Field(description="Name of the library.")
    explanation: str = Field(description="Explanation of where to apply this library in the code.")
    docs: List[str] = Field(description="List of useful docs to use.")

class ProblemSolvingSteps(SimpleSchemaArgs):
    steps: conlist(str, min_length=1, max_length=5) = Field(description="List of steps in order to solve the coding problem")
    libraries_to_use: List[LibraryNames] = Field(description="Names of the libraries to use.")
    library_docs: List[LibraryDocsInfo] = Field(description="Documentation of libraries to use.", default = None)


