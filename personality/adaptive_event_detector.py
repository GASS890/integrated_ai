SUCCESS_KEYWORDS = [
    "成功",
    "完了",
    "直りました",
    "動きました",
    "できました",
    "問題ありません",
    "正常",
]

ERROR_KEYWORDS = [
    "エラー",
    "失敗",
    "動かない",
    "接続できません",
    "例外",
    "SyntaxError",
    "ImportError",
    "Traceback",
]

DEVELOPMENT_KEYWORDS = [
    "実装",
    "開発",
    "コード",
    "Python",
    "FastAPI",
    "API",
    "Prompt",
    "プロンプト",
    "Memory",
    "記憶",
    "Git",
    "PowerShell",
]

PRAISE_KEYWORDS = [
    "ありがとう",
    "助かりました",
    "素晴らしい",
    "良いですね",
    "完璧",
    "すごい",
]

CASUAL_KEYWORDS = [
    "雑談",
    "こんにちは",
    "こんばんは",
    "おはよう",
    "元気",
]

CURIOSITY_KEYWORDS = [
    "なぜ",
    "どうして",
    "仕組み",
    "教えて",
    "とは",
    "どんな",
]


def _contains_any(
    text: str,
    keywords: list[str],
) -> bool:
    lowered = str(text or "").lower()

    return any(
        keyword.lower() in lowered
        for keyword in keywords
    )


def detect_emotion_event(
    user_text: str = "",
    assistant_text: str = "",
    error_occurred: bool = False,
    success: bool = False,
) -> dict:
    combined = "\n".join(
        value
        for value in (
            str(user_text or "").strip(),
            str(assistant_text or "").strip(),
        )
        if value
    )

    if error_occurred:
        return {
            "event": "error",
            "intensity": 0.12,
            "reason": "error_flag",
        }

    if success:
        return {
            "event": "success",
            "intensity": 0.10,
            "reason": "success_flag",
        }

    if _contains_any(combined, ERROR_KEYWORDS):
        return {
            "event": "error",
            "intensity": 0.08,
            "reason": "error_keyword",
        }

    if _contains_any(combined, SUCCESS_KEYWORDS):
        return {
            "event": "success",
            "intensity": 0.08,
            "reason": "success_keyword",
        }

    if _contains_any(combined, PRAISE_KEYWORDS):
        return {
            "event": "praise",
            "intensity": 0.06,
            "reason": "praise_keyword",
        }

    if _contains_any(combined, DEVELOPMENT_KEYWORDS):
        return {
            "event": "development",
            "intensity": 0.05,
            "reason": "development_keyword",
        }

    if _contains_any(combined, CURIOSITY_KEYWORDS):
        return {
            "event": "curiosity",
            "intensity": 0.04,
            "reason": "curiosity_keyword",
        }

    if _contains_any(combined, CASUAL_KEYWORDS):
        return {
            "event": "casual",
            "intensity": 0.04,
            "reason": "casual_keyword",
        }

    return {
        "event": None,
        "intensity": 0.0,
        "reason": "no_event",
    }
