import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat(messages, model="gpt-4.1-mini", temperature=0.1):
    res = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return res.choices[0].message.content