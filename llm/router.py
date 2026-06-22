from .models import LLMRequest, LLMResponse
from .ollama_backend import OllamaBackend
from .openai_backend import OpenAIBackend
from .claude_backend import ClaudeBackend

_BACKENDS = {
    "ollama": OllamaBackend(),
    "openai": OpenAIBackend(),
    "claude": ClaudeBackend(),
}


def load_default_backend() -> str:
    try:
        import json
        from pathlib import Path

        p = Path("config/llm_backend.json")
        if not p.exists():
            return "ollama"

        data = json.loads(p.read_text(encoding="utf-8-sig"))
        backend = data.get("default_backend", "ollama")
        return backend if backend in _BACKENDS else "ollama"
    except Exception:
        return "ollama"

def get_backend(name: str = "ollama"):
    if name not in _BACKENDS:
        raise ValueError(f"Unknown LLM backend: {name}")
    return _BACKENDS[name]

def chat(req: LLMRequest, backend_name: str | None = None) -> LLMResponse:
    backend_name = backend_name or load_default_backend()
    return get_backend(backend_name).chat(req)

def stream_chat(req: LLMRequest, backend_name: str | None = None):
    backend_name = backend_name or load_default_backend()
    return get_backend(backend_name).stream_chat(req)
