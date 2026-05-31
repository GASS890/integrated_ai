from openai import OpenAI

client = OpenAI(
    api_key="sk-xxxxxxxx"
)

def chat(messages, model="gpt-4.1-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content