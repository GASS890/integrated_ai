import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REFLECTION_PATH = (
    Path(__file__).resolve().parent
    / "conversation_reflections.json"
)


TOPIC_KEYWORDS = {
    "AI開発": [
        "AI",
        "LLM",
        "Prompt",
        "プロンプト",
        "人格",
    ],
    "記憶": [
        "Memory",
        "記憶",
        "Embedding",
    ],
    "音声": [
        "TTS",
        "Piper",
        "VOICEVOX",
        "音声",
    ],
    "Web/API": [
        "FastAPI",
        "API",
        "エンドポイント",
        "HTTP",
    ],
    "Python": [
        "Python",
        "def ",
        "import ",
        ".py",
    ],
    "Git": [
        "git ",
        "commit",
        "push",
        "tag",
    ],
}


PREFERENCE_SIGNALS = {
    "PowerShell形式": [
        "PowerShell",
        "powershell",
    ],
    "段階的な手順": [
        "一つずつ",
        "順番に",
        "手順",
    ],
    "詳しい説明": [
        "詳しく",
        "詳細",
        "細かく",
    ],
}


def _load_reflections() -> list[dict]:
    if not REFLECTION_PATH.exists():
        return []

    try:
        with open(
            REFLECTION_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception:
        return []

    return data if isinstance(data, list) else []


def _save_reflections(
    reflections: list[dict],
) -> list[dict]:
    with open(
        REFLECTION_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            reflections,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return reflections


def _count_matches(
    text: str,
    mapping: dict[str, list[str]],
) -> dict[str, int]:
    lowered = text.lower()
    result = {}

    for key, keywords in mapping.items():
        count = sum(
            lowered.count(keyword.lower())
            for keyword in keywords
        )

        if count > 0:
            result[key] = count

    return result


def create_conversation_reflection(
    messages: list[dict],
    session_id: str = "",
) -> dict:
    user_texts = []

    for message in messages or []:
        if not isinstance(message, dict):
            continue

        if message.get("role") != "user":
            continue

        content = str(
            message.get("content") or ""
        ).strip()

        if content:
            user_texts.append(content)

    combined = "\n".join(user_texts)

    topics = _count_matches(
        combined,
        TOPIC_KEYWORDS,
    )

    preferences = _count_matches(
        combined,
        PREFERENCE_SIGNALS,
    )

    topic_counter = Counter(topics)
    preference_counter = Counter(preferences)

    reflection = {
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "session_id": session_id,
        "user_message_count": len(user_texts),
        "topics": dict(
            topic_counter.most_common()
        ),
        "preference_signals": dict(
            preference_counter.most_common()
        ),
        "summary": _build_summary(
            topics=topics,
            preferences=preferences,
        ),
    }

    reflections = _load_reflections()
    reflections.append(reflection)
    reflections = reflections[-100:]

    _save_reflections(reflections)

    return reflection


def _build_summary(
    topics: dict[str, int],
    preferences: dict[str, int],
) -> str:
    parts = []

    if topics:
        main_topics = sorted(
            topics,
            key=topics.get,
            reverse=True,
        )[:3]

        parts.append(
            "主な話題: "
            + "、".join(main_topics)
        )

    if preferences:
        main_preferences = sorted(
            preferences,
            key=preferences.get,
            reverse=True,
        )[:3]

        parts.append(
            "確認された回答希望: "
            + "、".join(main_preferences)
        )

    if not parts:
        return "明確な長期傾向は検出されませんでした。"

    return " / ".join(parts)


def get_latest_reflection() -> dict:
    reflections = _load_reflections()

    if not reflections:
        return {}

    return reflections[-1]


def build_reflection_prompt() -> str:
    reflection = get_latest_reflection()

    if not reflection:
        return ""

    return (
        "【直近の会話振り返り】\n"
        f"- {reflection.get('summary', '')}\n"
        "- この振り返りは補助情報として扱い、"
        "現在の質問を最優先する"
    )
