import json
import requests
from typing import Optional, Any, List, Sequence, Union, Dict, Type, Callable
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from pydantic import Field
from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import LLMResult
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage, ToolCall, BaseMessage

from services.agents.chat_parsers import ChatParser, DeepSeekLlamaDistilledToolTunnedChatParser
from services.agents.validation_utils import format_messages_into_json


class CustomColabLLM(BaseChatModel):
    colab_url: str
    tools: Sequence[Union[Dict[str, Any], Type, Callable, BaseTool]] = None
    parser: ChatParser = DeepSeekLlamaDistilledToolTunnedChatParser()

    def _llm_type(self) -> str:
        return "custom_colab_llm"

    def bind_tools(self, tools: Sequence[Union[Dict[str, Any], Type, Callable, BaseTool]], **kwargs: Any):
        self.tools = tools
        return self

    # Necesario sobreescribir, no usarlo
    def _generate(
            self,
            prompts: list[str],
            stop: Optional[list[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> LLMResult:
        pass

    def invoke(self, messages: List[BaseMessage], **kwargs) -> dict:
        json_messages = format_messages_into_json(messages)
        raw_string = self.parser.apply_chat_template(json_messages, tools=self.tools)
        params = {
            "content": raw_string,
        }
        response = requests.get(self.colab_url, params=params).json()
        if response["content"]:
            response = AIMessage(content=response["content"])

        return response


