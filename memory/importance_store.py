import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from memory.importance_engine import (
    calculate_memory_importance,
)


IMPORTANCE_MEMORY_PATH = (
    Path(__file__).resolve().parent
    / "importance_memories.json"
)


def _load_items() -> list[dict]:
    if not IMPORTANCE_MEMORY_PATH.exists():
        return []

    try:
        with open(
            IMPORTANCE_MEMORY_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    return data


def _save_items(
    items: list[dict],
) -> list[dict]:
    with open(
        IMPORTANCE_MEMORY_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            items,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return items



def _normalize_memory_text(text: str) -> str:
    return " ".join(
        str(text or "").strip().lower().split()
    )


def add_importance_memory(
    text: str,
    source: str = "conversation",
    explicit: bool = False,
    metadata: dict | None = None,
) -> dict:
    evaluation = calculate_memory_importance(
        text=text,
        explicit=explicit,
        source=source,
    )

    normalized_text = _normalize_memory_text(text)
    items = _load_items()

    for existing in items:
        if (
            _normalize_memory_text(
                existing.get("text", "")
            )
            == normalized_text
        ):
            duplicate = dict(existing)
            duplicate["duplicate"] = True
            return duplicate

    item = {
        "memory_id": uuid4().hex,
        "text": str(text or "").strip(),
        "importance": evaluation["importance"],
        "importance_reasons": evaluation["reasons"],
        "source": source,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "metadata": metadata or {},
    }

    items.append(item)
    _save_items(items)

    return item


def list_importance_memories(
    minimum_importance: float = 0.0,
    limit: int = 50,
) -> list[dict]:
    items = [
        item
        for item in _load_items()
        if float(
            item.get("importance", 0.0)
        ) >= minimum_importance
    ]

    items.sort(
        key=lambda item: (
            float(item.get("importance", 0.0)),
            item.get("created_at", ""),
        ),
        reverse=True,
    )

    return items[:max(1, int(limit))]


def build_important_memory_text(
    minimum_importance: float = 0.6,
    limit: int = 10,
) -> str:
    items = list_importance_memories(
        minimum_importance=minimum_importance,
        limit=limit,
    )

    if not items:
        return ""

    return "\n".join(
        (
            f"- [{item.get('importance', 0.0):.2f}] "
            f"{item.get('text', '')}"
        )
        for item in items
    )
