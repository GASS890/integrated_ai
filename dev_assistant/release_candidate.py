from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEW_HISTORY_PATH = PROJECT_ROOT / "dev_assistant" / "review_history.json"


def generate_release_candidate_report() -> str:
    status = _run_git_command(["git", "status", "--short"])
    recent_log = _run_git_command(
        ["git", "log", "--oneline", "-8"]
    )
    latest_reviews = _load_latest_reviews(limit=3)

    risk = _estimate_risk(
        status=status,
        latest_reviews=latest_reviews,
    )

    recommendation = (
        "READY FOR RELEASE"
        if risk == "LOW"
        else "NEEDS CHECK"
    )

    return (
        "Release Candidate Report\n\n"
        f"Status:\n{recommendation}\n\n"
        f"Risk:\n{risk}\n\n"
        "Git status:\n"
        f"{status or 'clean'}\n\n"
        "Recent commits:\n"
        f"{recent_log or 'no commits'}\n\n"
        "Latest review summaries:\n"
        f"{latest_reviews or 'no review history'}"
    )


def _run_git_command(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode != 0:
            return result.stderr.strip()

        return result.stdout.strip()

    except Exception as e:
        return f"{type(e).__name__}: {e}"


def _load_latest_reviews(limit: int = 3) -> str:
    if not REVIEW_HISTORY_PATH.exists():
        return ""

    try:
        history = json.loads(
            REVIEW_HISTORY_PATH.read_text(encoding="utf-8")
        )
    except Exception:
        return ""

    if not isinstance(history, list):
        return ""

    items = history[-limit:]

    rendered = []
    for item in items:
        created_at = item.get("created_at", "unknown")
        review = item.get("review", "")

        rendered.append(
            f"- {created_at}: {_first_line(review)}"
        )

    return "\n".join(rendered)


def _first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()

    return "empty review"


def _estimate_risk(
    status: str,
    latest_reviews: str,
) -> str:
    if status.strip():
        return "MEDIUM"

    normalized = latest_reviews.replace(" ", "")

    if "問題あり" in normalized:
        return "HIGH"

    if "要確認" in normalized:
        return "MEDIUM"

    return "LOW"