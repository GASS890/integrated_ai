from .base import BaseLLMBackend
from .models import LLMRequest, LLMResponse

class OllamaBackend(BaseLLMBackend):
    name = "ollama"

    def chat(self, req: LLMRequest) -> LLMResponse:
        from llm_client import call_chat
        text = call_chat(req.messages)
        return LLMResponse(text=text, backend=self.name, model=req.model)

    def stream_chat(self, req: LLMRequest):
        from llm_client import stream_chat
        return stream_chat(req.messages)
