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