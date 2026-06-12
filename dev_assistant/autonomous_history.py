from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTONOMOUS_HISTORY_PATH = (
    PROJECT_ROOT
    / "dev_assistant"
    / "autonomous_history.json"
)


def load_autonomous_history() -> list[dict[str, Any]]:
    if not AUTONOMOUS_HISTORY_PATH.exists():
        return []

    try:
        data = json.loads(
            AUTONOMOUS_HISTORY_PATH.read_text(
                encoding="utf-8",
            )
        )
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    return data


def save_autonomous_history(
    goal: str,
    selected_strategy: str,
    related_files: list[str],
    target_file: str | None = None,
    purpose: str | None = None,
) -> None:
    history = load_autonomous_history()

    history.append(
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "goal": goal,
            "selected_strategy": selected_strategy,
            "related_files": related_files,
            "target_file": target_file or "",
            "purpose": purpose or "",
        }
    )

    AUTONOMOUS_HISTORY_PATH.write_text(
        json.dumps(
            history,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def get_recent_autonomous_history(
    limit: int = 5,
) -> list[dict[str, Any]]:
    history = load_autonomous_history()

    if limit <= 0:
        return []

    return history[-limit:]


def render_recent_autonomous_history(
    limit: int = 5,
) -> str:
    items = get_recent_autonomous_history(limit=limit)

    if not items:
        return "No autonomous development history."

    lines: list[str] = []

    for item in items:
        created_at = item.get("created_at", "unknown")
        goal = item.get("goal", "")
        target_file = item.get("target_file", "")
        purpose = item.get("purpose", "")

        lines.append(
            "- "
            f"{created_at} | "
            f"goal={goal} | "
            f"target_file={target_file} | "
            f"purpose={purpose}"
        )

    return "\n".join(lines)

def get_autonomous_history_report(
    limit: int = 10,
) -> str:
    return render_recent_autonomous_history(
        limit=limit
    )

def is_similar_autonomous_work(
    goal: str,
    target_file: str | None = None,
    purpose: str | None = None,
    limit: int = 10,
) -> bool:
    recent_items = get_recent_autonomous_history(limit=limit)

    goal_text = goal.strip().lower()
    target_text = (target_file or "").strip().lower()
    purpose_text = (purpose or "").strip().lower()

    for item in recent_items:
        past_goal = str(item.get("goal", "")).strip().lower()
        past_target = str(item.get("target_file", "")).strip().lower()
        past_purpose = str(item.get("purpose", "")).strip().lower()

        if target_text and target_text == past_target:
            return True

        if purpose_text and _has_text_overlap(
            purpose_text,
            past_purpose,
        ):
            return True

        if goal_text and _has_text_overlap(
            goal_text,
            past_goal,
        ):
            return True

    return False


def _has_text_overlap(
    current: str,
    past: str,
) -> bool:
    if not current or not past:
        return False

    current_tokens = _tokenize_text(current)
    past_tokens = _tokenize_text(past)

    if not current_tokens or not past_tokens:
        return False

    overlap = current_tokens & past_tokens

    return len(overlap) >= 3


def _tokenize_text(text: str) -> set[str]:
    separators = [
        " ",
        "　",
        "\n",
        "\r",
        "\t",
        ",",
        "、",
        ".",
        "。",
        ":",
        "：",
        "|",
        "/",
        "\\",
        "-",
        "_",
    ]

    normalized = text

    for separator in separators:
        normalized = normalized.replace(separator, " ")

    return {
        token
        for token in normalized.split()
        if len(token) >= 2
    }