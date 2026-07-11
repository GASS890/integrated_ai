IMPORTANT_KEYWORDS = {
    "preference": [
        "好き",
        "嫌い",
        "好む",
        "苦手",
        "希望",
        "毎回",
        "今後",
    ],
    "identity": [
        "私は",
        "自分は",
        "名前",
        "仕事",
        "職業",
        "年齢",
        "住んで",
    ],
    "project": [
        "開発",
        "プロジェクト",
        "作成中",
        "実装",
        "目標",
        "方針",
    ],
    "instruction": [
        "覚えて",
        "忘れないで",
        "次から",
        "必ず",
        "しないで",
    ],
}


TEMPORARY_KEYWORDS = [
    "今日は暑い",
    "今日は寒い",
    "眠い",
    "疲れた",
    "今だけ",
    "一時的",
]


def _contains_any(
    text: str,
    keywords: list[str],
) -> bool:
    lowered = text.lower()

    return any(
        keyword.lower() in lowered
        for keyword in keywords
    )


def calculate_memory_importance(
    text: str,
    explicit: bool = False,
    source: str = "conversation",
) -> dict:
    content = str(text or "").strip()

    if not content:
        return {
            "importance": 0.0,
            "reasons": ["empty_text"],
        }

    score = 0.25
    reasons = []

    if explicit:
        score += 0.45
        reasons.append("explicit_memory_request")

    for category, keywords in IMPORTANT_KEYWORDS.items():
        if _contains_any(content, keywords):
            score += 0.12
            reasons.append(category)

    if source == "profile":
        score += 0.15
        reasons.append("profile_source")

    if source == "setup":
        score += 0.12
        reasons.append("setup_source")

    if _contains_any(content, TEMPORARY_KEYWORDS):
        score -= 0.18
        reasons.append("temporary_information")

    if len(content) >= 80:
        score += 0.05
        reasons.append("detailed_content")

    score = round(
        max(0.0, min(1.0, score)),
        4,
    )

    return {
        "importance": score,
        "reasons": reasons,
    }
