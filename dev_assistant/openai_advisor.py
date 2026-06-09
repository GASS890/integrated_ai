import os
from openai import OpenAI


_client = None


def get_openai_client():
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY が設定されていません。"
            )

        _client = OpenAI(api_key=api_key)

    return _client


def ask_chatgpt_advisor(
    instruction: str,
    context: str,
    model: str = "gpt-4.1-mini",
) -> str:
    client = get_openai_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはPython/FastAPIアプリの開発補助AIです。"
                    "目的は、ローカルAIが安全にコード変更できるように、最小単位の変更案を作ることです。"
                    "回答は必ず次の形式にしてください。"
                    "1. 変更対象ファイル"
                    "2. 変更目的"
                    "3. 変更前コード"
                    "4. 変更後コード"
                    "5. 動作確認コマンド"
                    "6. 注意点"
                    "一度に複数箇所を変更しないでください。"
                    "import整理やdocstring追加のような見た目だけの改善は、依頼がない限り提案しないでください。"
                    "機能追加・バグ修正・設計変更に関係する変更だけを提案してください。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "依頼内容:\n"
                    f"{instruction}\n\n"
                    "現在のコード情報:\n"
                    f"{context}"
                ),
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or ""