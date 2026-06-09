from project_reader import build_context
from openai_advisor import ask_chatgpt_advisor


context = build_context(
    [
        "llm_client.py",
        "llm/router.py",
    ]
)

result = ask_chatgpt_advisor(
    instruction=(
        "v0.20としてOpenAI API接続を安定化したいです。"
        "現状コードを見て、最初に変更すべき1か所だけ提案してください。"
    ),
    context=context,
)

print(result)