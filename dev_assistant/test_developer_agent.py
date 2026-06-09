from dev_assistant.developer_agent import ask_developer_agent
from dev_assistant.dev_mode import DevMode


result = ask_developer_agent(
    instruction=(
        "v0.20としてOpenAI backendを安定化したい。"
        "最初に変更すべき1か所だけ提案してください。"
    ),
    mode=DevMode.FEATURE,
)

print(result)