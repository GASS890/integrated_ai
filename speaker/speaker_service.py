from pathlib import Path
import uuid
import os

from voice.tts_router import synthesize_voice, get_tts_status
from speaker.speaker_config import load_speaker_config, save_speaker_config
from speaker.speaker_state import (
    get_speaker_state,
    update_speaker_success,
    update_speaker_error,
)


BASE_DIR = Path(__file__).resolve().parent.parent


def get_speaker_status() -> dict:
    return {
        "config": load_speaker_config(),
        "state": get_speaker_state(),
        "tts": get_tts_status(),
        "role_plan": {
            "speaker": "耳と口。将来は別端末化し、マイク・ウェイクワード・TTS・再生を担当。",
            "smartphone": "脳・人格・短期記憶・UI。",
            "pc": "長期記憶・Embedding検索・重い処理・音声学習。",
            "cloud": "バックアップ・同期。",
        },
    }


def update_speaker_config(config: dict) -> dict:
    return save_speaker_config(config or {})


def speaker_say(text: str, backend: str | None = None) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("text is empty")

    config = load_speaker_config()

    if config.get("mode") == "remote":
        raise NotImplementedError("remote speaker mode is reserved for future implementation")

    output_dir = BASE_DIR / str(config.get("output_dir", "outputs/tts"))
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"speaker_{uuid.uuid4().hex[:12]}.wav"
    selected_backend = backend or config.get("tts_backend") or None

    try:
        wav = synthesize_voice(text, backend=selected_backend)
        output_file.write_bytes(wav)

        update_speaker_success(text, str(output_file))

        return {
            "status": "ok",
            "mode": config.get("mode", "local"),
            "backend": selected_backend,
            "output_file": str(output_file),
            "bytes": len(wav),
            "auto_play": bool(config.get("auto_play", False)),
        }

    except Exception as e:
        update_speaker_error(text, str(e))
        raise
