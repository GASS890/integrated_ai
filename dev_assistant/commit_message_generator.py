from __future__ import annotations


def generate_commit_message(purpose: str) -> str:
    normalized = purpose.lower()

    if _contains_any(normalized, ["fix", "修正", "エラー", "失敗", "不具合"]):
        prefix = "fix"
    elif _contains_any(normalized, ["refactor", "整理", "分離", "改善"]):
        prefix = "refactor"
    elif _contains_any(normalized, ["docs", "document", "アーカイブ", "ドキュメント"]):
        prefix = "docs"
    elif _contains_any(normalized, ["test", "テスト", "確認"]):
        prefix = "test"
    else:
        prefix = "feat"

    summary = _normalize_summary(purpose)

    return f"{prefix}: {summary}"


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _normalize_summary(text: str) -> str:
    text = text.strip()

    if not text:
        return "apply approved patch"

    text = text.replace("\n", " ").replace("\r", " ")

    while "  " in text:
        text = text.replace("  ", " ")

    if len(text) > 72:
        text = text[:72].rstrip()

    return text