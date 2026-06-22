from .base import BaseLLMBackend
from .models import LLMRequest, LLMResponse

class OpenAIBackend(BaseLLMBackend):
    name = "openai"

    def chat(self, req: LLMRequest) -> LLMResponse:
        raise NotImplementedError("OpenAI backend is not wired yet.")

    def stream_chat(self, req: LLMRequest):
        raise NotImplementedError("OpenAI stream backend is not wired yet.")
