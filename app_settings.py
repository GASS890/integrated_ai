import json
from pathlib import Path


SETTINGS_FILE = Path("app_settings.json")


DEFAULT_SETTINGS = {
    "use_developer_agent": False,
    "auto_git_commit": False,
    "auto_git_push": False,
}

def is_auto_git_commit_enabled() -> bool:
    settings = load_app_settings()
    return bool(settings.get("auto_git_commit", False))


def set_auto_git_commit_enabled(enabled: bool) -> dict:
    settings = load_app_settings()
    settings["auto_git_commit"] = bool(enabled)
    save_app_settings(settings)
    return settings

def load_app_settings() -> dict:
    if not SETTINGS_FILE.exists():
        save_app_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)
        return settings

    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_app_settings(settings: dict) -> None:
    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def is_developer_agent_enabled() -> bool:
    settings = load_app_settings()
    return bool(settings.get("use_developer_agent", False))


def set_developer_agent_enabled(enabled: bool) -> dict:
    settings = load_app_settings()
    settings["use_developer_agent"] = bool(enabled)
    save_app_settings(settings)
    return settings


def is_auto_git_push_enabled() -> bool:
    settings = load_app_settings()
    return bool(settings.get("auto_git_push", False))


def set_auto_git_push_enabled(enabled: bool) -> dict:
    settings = load_app_settings()
    settings["auto_git_push"] = bool(enabled)
    save_app_settings(settings)
    return settings