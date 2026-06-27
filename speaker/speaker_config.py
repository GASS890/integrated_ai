import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SPEAKER_CONFIG_PATH = BASE_DIR / "speaker_settings.json"

DEFAULT_SPEAKER_CONFIG = {
    "mode": "local",
    "device_role": "speaker",
    "tts_backend": "piper_plus",
    "auto_play": False,
    "auto_enqueue_ai_response": True,
    "output_dir": "outputs/tts",
    "future_remote_url": "",
}


def load_speaker_config() -> dict:
    if not SPEAKER_CONFIG_PATH.exists():
        save_speaker_config(DEFAULT_SPEAKER_CONFIG)
        return dict(DEFAULT_SPEAKER_CONFIG)

    try:
        data = json.loads(SPEAKER_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return dict(DEFAULT_SPEAKER_CONFIG)

    merged = dict(DEFAULT_SPEAKER_CONFIG)
    merged.update(data or {})
    return merged


def save_speaker_config(config: dict) -> dict:
    merged = dict(DEFAULT_SPEAKER_CONFIG)
    merged.update(config or {})
    SPEAKER_CONFIG_PATH.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return merged
