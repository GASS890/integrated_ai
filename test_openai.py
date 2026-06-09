from dev_assistant.openai_advisor import ask_chatgpt_advisor

result = ask_chatgpt_advisor(
    instruction="FastAPIのメリットを3つ教えて",
    context=""
)

print(result)