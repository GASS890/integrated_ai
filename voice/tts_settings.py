import json
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
TTS_SETTINGS_PATH = BASE_DIR / "tts_settings.json"

DEFAULT_SETTINGS = {
    "backend": "piper_plus",
    "fallback_backend": "voicevox",
    "speaker": 1,
    "auto_fallback": True,
}


def load_tts_settings() -> dict:
    if not TTS_SETTINGS_PATH.exists():
        save_tts_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)

    try:
        with open(TTS_SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return dict(DEFAULT_SETTINGS)

    merged = dict(DEFAULT_SETTINGS)
    merged.update(data or {})
    return merged


def save_tts_settings(settings: dict) -> dict:
    merged = dict(DEFAULT_SETTINGS)
    merged.update(settings or {})

    with open(TTS_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    return merged


def get_default_tts_backend() -> str:
    return os.getenv("TTS_BACKEND", load_tts_settings().get("backend", "voicevox")).lower()
