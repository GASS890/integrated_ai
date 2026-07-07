import json
from pathlib import Path

SETUP_STATUS_PATH = (
    Path(__file__).resolve().parent
    / "setup_status.json"
)


DEFAULT_SETUP_STATUS = {
    "setup_complete": False,
    "active_profile_id": "default",
    "setup_version": "v0.51.00"
}


def load_setup_status() -> dict:
    if not SETUP_STATUS_PATH.exists():
        save_setup_status(DEFAULT_SETUP_STATUS)
        return dict(DEFAULT_SETUP_STATUS)

    try:
        with open(SETUP_STATUS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return dict(DEFAULT_SETUP_STATUS)

    merged = dict(DEFAULT_SETUP_STATUS)
    merged.update(data or {})
    return merged


def save_setup_status(status: dict) -> dict:
    merged = dict(DEFAULT_SETUP_STATUS)
    merged.update(status or {})

    with open(SETUP_STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    return merged


def is_setup_complete() -> bool:
    return bool(load_setup_status().get("setup_complete", False))


def mark_setup_complete(profile_id: str = "default") -> dict:
    return save_setup_status({
        "setup_complete": True,
        "active_profile_id": profile_id,
    })


def reset_setup_status() -> dict:
    return save_setup_status(DEFAULT_SETUP_STATUS)
