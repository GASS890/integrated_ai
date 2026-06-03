# llm/router.py

import os
from . import ollama_backend
from . import openai_backend
from llm.ollama_backend import (
    chat as ollama_chat,
    stream as ollama_stream,
)


def chat(messages, model, options):
    return ollama_chat(
        messages,
        model,
        options,
    )


def stream(messages, model, options):
    return ollama_stream(
        messages,
        model,
        options,
    )

def current_backend() -> str:
    return os.getenv("LLM_BACKEND", "ollama").lower()


def chat(messages, model, options=None, timeout=120):
    backend = current_backend()

    if backend == "openai":
        print("[LLM] backend=openai")
        return openai_backend.chat(messages, model, options, timeout)

    print("[LLM] backend=ollama")
    return ollama_backend.chat(messages, model, options, timeout)


def stream(messages, model, options=None, timeout=120):
    backend = current_backend()

    if backend == "openai":
        print("[LLM] backend=openai stream")
        for delta in openai_backend.stream(messages, model, options, timeout):
            print("[stream delta]", repr(delta[:20]))
            yield delta
        return

    print("[LLM] backend=ollama stream")
    for delta in ollama_backend.stream(messages, model, options, timeout):
        print("[stream delta]", repr(delta[:20]))
        yield delta