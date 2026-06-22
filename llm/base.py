from .models import LLMRequest, LLMResponse

class BaseLLMBackend:
    name = "base"

    def chat(self, req: LLMRequest) -> LLMResponse:
        raise NotImplementedError

    def stream_chat(self, req: LLMRequest):
        raise NotImplementedError
