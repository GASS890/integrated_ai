import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
STORE_PATH = BASE_DIR / "personality_learning" / "personality_learning_results.json"


DEFAULT_STORE = {
    "version": 1,
    "updated_at": "",
    "items": [],
}


def load_learning_store() -> dict:
    if not STORE_PATH.exists():
        save_learning_store(DEFAULT_STORE)
        return dict(DEFAULT_STORE)

    try:
        data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = dict(DEFAULT_STORE)

    merged = dict(DEFAULT_STORE)
    merged.update(data or {})

    if not isinstance(merged.get("items"), list):
        merged["items"] = []

    return merged


def save_learning_store(store: dict) -> dict:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = dict(DEFAULT_STORE)
    data.update(store or {})
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")

    STORE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return data


def add_learning_result(
    title: str,
    summary: str,
    category: str = "tone",
    strength: str = "medium",
    source: str = "manual",
    notes: list[str] | None = None,
) -> dict:
    store = load_learning_store()

    item = {
        "id": "plr_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "title": title,
        "summary": summary,
        "category": category,
        "strength": strength,
        "source": source,
        "notes": notes or [],
    }

    store["items"].append(item)
    save_learning_store(store)

    return item


def list_learning_results() -> list[dict]:
    return load_learning_store().get("items", [])


def get_latest_learning_result() -> dict | None:
    items = list_learning_results()
    if not items:
        return None
    return items[-1]


def build_learning_results_prompt(limit: int = 5) -> str:
    items = list_learning_results()[-limit:]

    if not items:
        return ""

    lines = ["【人格学習結果】"]

    for item in items:
        lines.append(
            f"- {item.get('title')}: {item.get('summary')} "
            f"(category={item.get('category')}, strength={item.get('strength')})"
        )

    return "\n".join(lines)
