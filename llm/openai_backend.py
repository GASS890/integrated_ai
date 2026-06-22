import os

from .base import BaseLLMBackend
from .models import LLMRequest, LLMResponse


class OpenAIBackend(BaseLLMBackend):
    name = "openai"

    def is_configured(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))

    def chat(self, req: LLMRequest) -> LLMResponse:
        if not self.is_configured():
            raise RuntimeError("OPENAI_API_KEY が未設定です。")

        raise NotImplementedError("OpenAI backend API call is not wired yet.")

    def stream_chat(self, req: LLMRequest):
        if not self.is_configured():
            raise RuntimeError("OPENAI_API_KEY が未設定です。")

        raise NotImplementedError("OpenAI stream backend API call is not wired yet.")
