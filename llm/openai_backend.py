# llm/openai_backend.py

import os
from openai import OpenAI
from .models import OPENAI_MODEL_FAST, OPENAI_MODEL_SMART

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def to_openai_model(model: str | None) -> str:
    if model == "qwen2.5:14b":
        return OPENAI_MODEL_SMART
    return OPENAI_MODEL_FAST


def max_tokens_from_options(options: dict | None) -> int:
    if not options:
        return 512
    return int(options.get("num_predict", 512))


def chat(messages, model, options=None, timeout=120):
    response = client.chat.completions.create(
        model=to_openai_model(model),
        messages=messages,
        temperature=(options or {}).get("temperature", 0.5),
        top_p=(options or {}).get("top_p", 0.9),
        max_tokens=max_tokens_from_options(options),
        timeout=timeout,
    )

    return response.choices[0].message.content or ""


def stream(messages, model, options=None, timeout=120):
    response_stream = client.chat.completions.create(
        model=to_openai_model(model),
        messages=messages,
        temperature=(options or {}).get("temperature", 0.5),
        top_p=(options or {}).get("top_p", 0.9),
        max_tokens=max_tokens_from_options(options),
        stream=True,
        timeout=timeout,
    )

    for chunk in response_stream:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta.content
        if delta:
            yield delta