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

class LibraryDocs(SimpleSchemaArgs):
    library_name: str = Field(description="Name of the library.")


class ProblemSolvingSteps(SimpleSchemaArgs):
    steps: conlist(str, min_length=1, max_length=5) = Field(description="List of steps in order to solve the coding problem")
    library_docs:


