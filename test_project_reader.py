from dev_assistant.project_reader import build_context
from dev_assistant.openai_advisor import ask_chatgpt_advisor

context = build_context(
    [
        "main.py",
    ]
)

result = ask_chatgpt_advisor(
    instruction=(
        "このファイルをレビューしてください。"
        "改善点を3つ挙げてください。"
    ),
    context=context,
)

print(result)