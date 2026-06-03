# llm/ollama_backend.py

import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
session = requests.Session()

from llm_client import (
    call_ollama_chat,
    stream_ollama_chat,
)


def chat(messages, model, options):
    return call_ollama_chat(
        messages,
        model=model,
        options=options,
    )


def stream(messages, model, options):
    return stream_ollama_chat(
        messages,
        model=model,
        options=options,
    )

def chat(messages, model, options=None, timeout=120):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": options or {},
    }

    r = session.post(
        OLLAMA_URL,
        json=payload,
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "")


def stream(messages, model, options=None, timeout=120):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": options or {},
    }

    with session.post(
        OLLAMA_URL,
        json=payload,
        stream=True,
        timeout=timeout,
    ) as r:
        r.raise_for_status()

        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue

            try:
                data = json.loads(line)
            except Exception:
                continue

            if data.get("done"):
                break

            content = data.get("message", {}).get("content", "")
            if content:
                yield content
