import os

from voice.voicevox_client import synthesize_voice as synthesize_voicevox
from voice.piper_client import synthesize_piper, is_piper_ready


DEFAULT_TTS_BACKEND = os.getenv("TTS_BACKEND", "voicevox").lower()


def get_tts_status() -> dict:
    return {
        "default_backend": DEFAULT_TTS_BACKEND,
        "piper_ready": is_piper_ready(),
        "piper_model": os.getenv("PIPER_MODEL", "models/piper/default.onnx"),
        "role_plan": {
            "speaker": "耳と口。将来はPiper/TTSと音声再生を担当",
            "smartphone": "脳・人格・短期記憶・UI",
            "pc": "長期記憶・Embedding検索・重い処理",
            "cloud": "バックアップ・同期",
        },
    }


def synthesize_voice(text: str, speaker: int = 1, backend: str | None = None) -> bytes:
    selected = (backend or DEFAULT_TTS_BACKEND or "voicevox").lower()

    if selected == "piper":
        return synthesize_piper(text, speaker=speaker)

    if selected == "voicevox":
        return synthesize_voicevox(text, speaker=speaker)

    if selected == "auto":
        if is_piper_ready():
            return synthesize_piper(text, speaker=speaker)
        return synthesize_voicevox(text, speaker=speaker)

    raise ValueError(f"Unknown TTS backend: {selected}")
