from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from dev_assistant.git_tools import get_git_diff
from dev_assistant.openai_advisor import ask_chatgpt_advisor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEW_HISTORY_PATH = PROJECT_ROOT / "dev_assistant" / "review_history.json"

def review_current_diff() -> str:
    diff = get_git_diff()

    if not diff.strip():
        return "レビュー対象の差分はありません。"

    return review_diff(diff)


def review_diff(diff: str) -> str:
    instruction = (
        "以下の git diff をレビューしてください。\n\n"
        "確認観点:\n"
        "- 明らかな構文エラーがないか\n"
        "- 既存機能を壊す変更がないか\n"
        "- 例外処理が不十分ではないか\n"
        "- セキュリティ上危険な変更がないか\n"
        "- APIキーや個人情報を保存・出力していないか\n"
        "- 変更規模が目的に対して過剰ではないか\n\n"
        "出力形式:\n"
        "1. 判定: 問題なし / 要確認 / 問題あり\n"
        "2. 主な指摘\n"
        "3. 修正が必要な場合の提案\n\n"
        "断定できない場合は、推測ではなく「要確認」としてください。"
    )

    context = (
        "===== GIT DIFF =====\n"
        f"{diff}"
    )

    review = ask_chatgpt_advisor(
        instruction=instruction,
        context=context,
    )

    save_review_history(diff=diff, review=review)

    return review

def save_review_history(diff: str, review: str) -> None:
    history = []

    if REVIEW_HISTORY_PATH.exists():
        try:
            history = json.loads(REVIEW_HISTORY_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            history = []

    history.append(
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "diff": diff,
            "review": review,
        }
    )

    REVIEW_HISTORY_PATH.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def is_review_approved(review: str) -> bool:
    normalized = review.replace(" ", "").replace("　", "")

    if "判定:問題なし" in normalized:
        return True

    if "1.判定:問題なし" in normalized:
        return True

    return False