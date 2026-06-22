from .base import BaseLLMBackend
from .models import LLMRequest, LLMResponse

class ClaudeBackend(BaseLLMBackend):
    name = "claude"

    def chat(self, req: LLMRequest) -> LLMResponse:
        raise NotImplementedError("Claude backend is not wired yet.")

    def stream_chat(self, req: LLMRequest):
        raise NotImplementedError("Claude stream backend is not wired yet.")
