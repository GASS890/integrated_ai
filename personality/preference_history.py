import json
from datetime import datetime, timezone
from pathlib import Path

from personality.user_model_manager import (
    load_user_model,
    user_model_to_dict,
)


PREFERENCE_HISTORY_PATH = (
    Path(__file__).resolve().parent
    / "preference_history.json"
)


def _load_history() -> list[dict]:
    if not PREFERENCE_HISTORY_PATH.exists():
        return []

    try:
        with open(
            PREFERENCE_HISTORY_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception:
        return []

    return data if isinstance(data, list) else []


def _save_history(
    history: list[dict],
) -> list[dict]:
    with open(
        PREFERENCE_HISTORY_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return history


def record_user_model_snapshot(
    reason: str = "manual",
) -> dict:
    model = load_user_model()

    snapshot = {
        "recorded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "reason": reason,
        "model": user_model_to_dict(model),
    }

    history = _load_history()
    history.append(snapshot)

    history = history[-200:]
    _save_history(history)

    return snapshot


def calculate_preference_trends(
    category: str = "preferences",
    window: int = 10,
) -> dict:
    history = _load_history()

    snapshots = history[-max(2, int(window)):]

    if len(snapshots) < 2:
        return {}

    first = (
        snapshots[0]
        .get("model", {})
        .get(category, {})
    )

    last = (
        snapshots[-1]
        .get("model", {})
        .get(category, {})
    )

    keys = set(first) | set(last)
    trends = {}

    for key in keys:
        before = float(first.get(key, 0.0))
        after = float(last.get(key, 0.0))

        trends[key] = {
            "before": round(before, 4),
            "after": round(after, 4),
            "change": round(after - before, 4),
        }

    return trends


def build_long_term_preference_prompt() -> str:
    trends = calculate_preference_trends()

    if not trends:
        return (
            "【長期的な好みの傾向】\n"
            "- まだ十分な履歴がありません"
        )

    lines = [
        "【長期的な好みの傾向】",
    ]

    for key, trend in sorted(
        trends.items(),
        key=lambda item: abs(
            item[1]["change"]
        ),
        reverse=True,
    ):
        change = trend["change"]

        if abs(change) < 0.03:
            continue

        direction = (
            "強まっている"
            if change > 0
            else "弱まっている"
        )

        lines.append(
            f"- {key}: {direction} "
            f"({trend['before']:.2f} → "
            f"{trend['after']:.2f})"
        )

    if len(lines) == 1:
        lines.append(
            "- 現在のところ大きな変化はありません"
        )

    return "\n".join(lines)
