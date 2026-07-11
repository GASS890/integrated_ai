GROWTH_RULES = {
    "interests": {
        "amount": 0.02,
        "keywords": {
            "AI開発": [
                "AI開発",
                "ローカルAI",
                "LLM",
                "プロンプト",
                "Prompt",
                "人格AI",
            ],
            "Python": [
                "Python",
                "py_compile",
                ".py",
            ],
            "FastAPI": [
                "FastAPI",
                "uvicorn",
                "エンドポイント",
            ],
            "音声AI": [
                "TTS",
                "音声AI",
                "Piper",
                "VOICEVOX",
                "Style-Bert",
            ],
        },
    },
    "preferences": {
        "amount": 0.03,
        "keywords": {
            "PowerShell形式": [
                "PowerShellで",
                "powershellで",
                "PowerShell形式",
                "実行できる形式",
            ],
            "手順を細かく": [
                "一つずつ",
                "1つずつ",
                "順番に",
                "手順を",
            ],
            "コード全文": [
                "全文",
                "そのまま貼り付け",
                "コピペ",
            ],
            "バージョン管理": [
                "git commit",
                "git push",
                "git tag",
                "バージョン",
            ],
        },
    },
    "knowledge_level": {
        "amount": 0.01,
        "keywords": {
            "AI": [
                "Embedding",
                "Prompt Router",
                "RuntimeState",
                "LLM",
            ],
            "Python": [
                "dataclass",
                "BaseModel",
                "import",
                "def ",
            ],
            "Git": [
                "git add",
                "git commit",
                "git push",
                "git tag",
            ],
            "FastAPI": [
                "@app.get",
                "@app.post",
                "FastAPI",
                "uvicorn",
            ],
        },
    },
    "conversation_style": {
        "amount": 0.02,
        "keywords": {
            "詳細さ": [
                "詳しく",
                "詳細に",
                "細かく",
            ],
            "構造化": [
                "整理して",
                "項目ごと",
                "順番に",
            ],
            "理由付き説明": [
                "理由",
                "なぜ",
                "根拠",
            ],
        },
    },
}


IGNORE_EXACT_TEXTS = {
    "はい",
    "いいえ",
    "了解",
    "お願いします",
    "ありがとう",
    "次",
}


IGNORE_PREFIXES = (
    "こんにちは",
    "こんばんは",
    "おはよう",
)


MIN_TEXT_LENGTH = 4
MAX_UPDATES_PER_MESSAGE = 8
