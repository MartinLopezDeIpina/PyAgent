from typing import  List, Literal

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import tool, Tool
from pydantic import ValidationError
import json
import re
from models import Action

class AgentValidator:
    def __init__(self, max_validation_errors: int = 3):
        self.validation_errors = 0
        self.max_validation_errors = max_validation_errors

    def reset_attempts(self):
        self.validation_errors = 0

    def extract_boxed_content(self, response:str) -> dict or None:
        pattern = r'\\boxed\{(.*?\}+)}'
        try:
            match = re.search(self, pattern, response, re.DOTALL)
            return match.group(1)
        except Exception as e:
            print(f"Error in re.search, no match for boxed")
            raise e


    def parse_response(self, response: dict):
        boxed_response = self.extract_boxed_content(response)

        boxed_response = f"{{{boxed_response}}}"
        try:
            json_response = json.loads(boxed_response)
            return json_response
        except Exception as e:
            print(f"Error parsing json")
            raise e

    def get_tool_by_name(self, available_tools: List[Tool], tool_name: str):
        for tool in available_tools:
            if tool.name == tool_name.lower():
                return tool
        raise ValueError(f"Tool {tool_name} not found")


    """
    Returns None if a validation exception was raised
    Returns Error action if too many validation exceptions were raised
    """
    def validate_response(self, response: BaseMessage, available_tools: List[Tool]):
        try:
            parsed_response = self.parse_response(response.content)
            validated_action = Action.model_validate(parsed_response)
            tool = self.get_tool_by_name(available_tools, validated_action.action)
            tool.args_schema.model_validate(validated_action.args)
            return validated_action

        except Exception as e:
            print(f"Validation error: {e}")
            self.validation_errors += 1

            if self.validation_errors > self.max_validation_errors:
                error_message = Action(action="error", args={"error": "Too many validation errors"})
                return error_message

            return None

def format_messages_into_json(messages):
    json_messages = []
    for message in messages:
        # los tool calls se guardan como diccionarios
        if type(message) == dict:
            json_messages.append(message)
        else:
            json_messages.append(message.model_dump())
    return json_messages
