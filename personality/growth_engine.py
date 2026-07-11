from personality.user_model_manager import update_score


INTEREST_KEYWORDS = {
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
        "API",
    ],
    "音声AI": [
        "TTS",
        "音声AI",
        "Piper",
        "VOICEVOX",
        "Style-Bert",
    ],
}

PREFERENCE_KEYWORDS = {
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
        "タグ",
        "バージョン",
    ],
}

STYLE_KEYWORDS = {
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
}

KNOWLEDGE_KEYWORDS = {
    "AI": [
        "LLM",
        "Embedding",
        "Prompt Router",
        "RuntimeState",
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
}


def _contains_any(
    text: str,
    keywords: list[str],
) -> bool:
    lowered = text.lower()

    return any(
        keyword.lower() in lowered
        for keyword in keywords
    )


def _apply_keyword_updates(
    text: str,
    category: str,
    mapping: dict[str, list[str]],
    amount: float,
) -> list[dict]:
    updates = []

    for key, keywords in mapping.items():
        if not _contains_any(text, keywords):
            continue

        updates.append(
            update_score(
                category=category,
                key=key,
                amount=amount,
            )
        )

    return updates


def observe_user_text(
    user_text: str,
) -> dict:
    text = str(user_text or "").strip()

    if not text:
        return {
            "observed": False,
            "reason": "empty_text",
            "updates": [],
        }

    updates = []

    updates.extend(
        _apply_keyword_updates(
            text=text,
            category="interests",
            mapping=INTEREST_KEYWORDS,
            amount=0.02,
        )
    )

    updates.extend(
        _apply_keyword_updates(
            text=text,
            category="preferences",
            mapping=PREFERENCE_KEYWORDS,
            amount=0.03,
        )
    )

    updates.extend(
        _apply_keyword_updates(
            text=text,
            category="conversation_style",
            mapping=STYLE_KEYWORDS,
            amount=0.02,
        )
    )

    updates.extend(
        _apply_keyword_updates(
            text=text,
            category="knowledge_level",
            mapping=KNOWLEDGE_KEYWORDS,
            amount=0.01,
        )
    )

    return {
        "observed": True,
        "text_length": len(text),
        "updates": updates,
    }
