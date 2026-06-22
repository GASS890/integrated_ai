# llm_client.py
import requests

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:7b"

OPTIONS = {
    "chat": {
        "temperature": 0.7,
    },
    "fast_chat": {
        "temperature": 0.7,
    },
    "smart_chat": {
        "temperature": 0.7,
    },
    "format": {
        "temperature": 0.2,
    },
    "title": {
        "temperature": 0.2,
    },
}


def call_chat(messages, model=None, options=None, timeout=120):
    model = model or DEFAULT_MODEL
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if options:
        payload["options"] = options

    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json=payload,
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "")


def stream_chat(messages, model=None, options=None, timeout=120):
    model = model or DEFAULT_MODEL
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if options:
        payload["options"] = options

    with requests.post(
        f"{OLLAMA_URL}/api/chat",
        json=payload,
        timeout=timeout,
        stream=True,
    ) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                import json
                data = json.loads(line)
                delta = data.get("message", {}).get("content", "")
                if delta:
                    yield delta
            except Exception:
                continue


# =========================================================
# LLM backend router entry points
# =========================================================
def call_chat_routed(messages, backend_name: str = "ollama", model: str | None = None, temperature: float = 0.7, options=None):
    from llm.models import LLMRequest
    from llm.router import chat

    req = LLMRequest(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=False,
    )

    if backend_name == "ollama":
        return call_chat(messages, model=model, options=options or {"temperature": temperature})

    return chat(req, backend_name=backend_name).text


def stream_chat_routed(messages, backend_name: str = "ollama", model: str | None = None, temperature: float = 0.7, options=None):
    from llm.models import LLMRequest
    from llm.router import stream_chat as routed_stream_chat

    req = LLMRequest(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=True,
    )

    if backend_name == "ollama":
        return stream_chat(messages, model=model, options=options or {"temperature": temperature})

    return routed_stream_chat(req, backend_name=backend_name)
