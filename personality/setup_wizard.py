import json
from pathlib import Path

from personality.profile_manager import save_profile_data, set_active_profile_id
from personality.setup_manager import mark_setup_complete
from personality.runtime_manager import reset_runtime_state

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def load_setup_template(template_id: str = "default_profile") -> dict:
    path = TEMPLATE_DIR / f"{template_id}.json"

    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_default_setup_template() -> dict:
    return load_setup_template("default_profile")


def apply_initial_setup(profile_data: dict | None = None) -> dict:
    data = profile_data or get_default_setup_template()
    profile_id = data.get("profile_id", "default")

    save_profile_data(profile_id, data)
    set_active_profile_id(profile_id)
    reset_runtime_state()
    mark_setup_complete(profile_id)

    return data
