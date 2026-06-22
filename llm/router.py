from .models import LLMRequest, LLMResponse
from .ollama_backend import OllamaBackend
from .openai_backend import OpenAIBackend
from .claude_backend import ClaudeBackend

_BACKENDS = {
    "ollama": OllamaBackend(),
    "openai": OpenAIBackend(),
    "claude": ClaudeBackend(),
}

def get_backend(name: str = "ollama"):
    if name not in _BACKENDS:
        raise ValueError(f"Unknown LLM backend: {name}")
    return _BACKENDS[name]

def chat(req: LLMRequest, backend_name: str = "ollama") -> LLMResponse:
    return get_backend(backend_name).chat(req)

def stream_chat(req: LLMRequest, backend_name: str = "ollama"):
    return get_backend(backend_name).stream_chat(req)
