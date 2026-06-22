# llm_client.py

from llm.router import chat, stream
from llm.models import OPTIONS


def call_chat(messages, model, options=None, timeout=120):
    return chat(
        messages=messages,
        model=model,
        options=options,
        timeout=timeout,
    )


def stream_chat(messages, model, options=None, timeout=120):
    for delta in stream(
        messages=messages,
        model=model,
        options=options,
        timeout=timeout,
    ):
        yield delta

# =========================================================
# LLM backend router entry points
# =========================================================
def call_chat_routed(messages, backend_name: str = "ollama", model: str | None = None, temperature: float = 0.7):
    from llm.models import LLMRequest
    from llm.router import chat

    req = LLMRequest(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=False,
    )
    return chat(req, backend_name=backend_name).text


def stream_chat_routed(messages, backend_name: str = "ollama", model: str | None = None, temperature: float = 0.7):
    from llm.models import LLMRequest
    from llm.router import stream_chat

    req = LLMRequest(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=True,
    )
    return stream_chat(req, backend_name=backend_name)

