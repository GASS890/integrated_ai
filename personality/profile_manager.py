import json
from pathlib import Path

PROFILE_DIR = Path(__file__).resolve().parent / "profiles"
ACTIVE_PROFILE_PATH = Path(__file__).resolve().parent / "active_profile.json"


def get_active_profile_id() -> str:
    if not ACTIVE_PROFILE_PATH.exists():
        set_active_profile_id("default")
        return "default"

    try:
        with open(ACTIVE_PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return "default"

    return data.get("active_profile_id", "default")


def set_active_profile_id(profile_id: str) -> dict:
    data = {"active_profile_id": profile_id}

    with open(ACTIVE_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def get_profile_path(profile_id: str | None = None) -> Path:
    profile_id = profile_id or get_active_profile_id()
    return PROFILE_DIR / f"{profile_id}.json"


def load_profile_data(profile_id: str | None = None) -> dict:
    path = get_profile_path(profile_id)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile_data(profile_id: str, data: dict) -> dict:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    data["profile_id"] = profile_id

    with open(get_profile_path(profile_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def list_profile_ids() -> list[str]:
    if not PROFILE_DIR.exists():
        return []

    return sorted(path.stem for path in PROFILE_DIR.glob("*.json"))
