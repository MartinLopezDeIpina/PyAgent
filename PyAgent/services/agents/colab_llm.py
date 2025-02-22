import json
import requests
from typing import Optional, Any, List
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from pydantic import Field
from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import LLMResult
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage, ToolCall, BaseMessage

from services.agents.validation_utils import format_messages_into_json


class CustomColabLLM(BaseChatModel):
    colab_url: str = Field(..., description="URL of the colab 'API'")

    def _llm_type(self) -> str:
        return "custom_colab_llm"

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
        params = {
            "messages": json.dumps(json_messages)
        }
        response = requests.get(self.colab_url, params=params).json()
        if response["content"]:
            response = AIMessage(content=response["content"])

        return response
