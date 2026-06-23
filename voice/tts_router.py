import os

from voice.voicevox_client import synthesize_voice as synthesize_voicevox
from voice.piper_client import synthesize_piper, is_piper_ready
from voice.piper_plus_client import synthesize_piper_plus, is_piper_plus_ready


DEFAULT_TTS_BACKEND = os.getenv("TTS_BACKEND", "voicevox").lower()


def get_tts_status() -> dict:
    return {
        "default_backend": DEFAULT_TTS_BACKEND,
        "piper_ready": is_piper_ready(),
        "piper_plus_ready": is_piper_plus_ready(),
        "piper_model": os.getenv("PIPER_MODEL", "models/piper/default.onnx"),
        "piper_plus_model": os.getenv("PIPER_PLUS_MODEL", "tools/piper-plus/src/python_run/tsukuyomi-chan-6lang-fp16.onnx"),
        "role_plan": {
            "speaker": "耳と口。将来はPiper Plus/TTSと音声再生を担当",
            "smartphone": "脳・人格・短期記憶・UI",
            "pc": "長期記憶・Embedding検索・重い処理・音声学習",
            "cloud": "バックアップ・同期",
        },
    }


def synthesize_voice(text: str, speaker: int = 1, backend: str | None = None) -> bytes:
    selected = (backend or DEFAULT_TTS_BACKEND or "voicevox").lower()

    if selected == "piper_plus":
        return synthesize_piper_plus(text, speaker=speaker)

    if selected == "piper":
        return synthesize_piper(text, speaker=speaker)

    if selected == "voicevox":
        return synthesize_voicevox(text, speaker=speaker)

    if selected == "auto":
        if is_piper_plus_ready():
            return synthesize_piper_plus(text, speaker=speaker)
        if is_piper_ready():
            return synthesize_piper(text, speaker=speaker)
        return synthesize_voicevox(text, speaker=speaker)

    raise ValueError(f"Unknown TTS backend: {selected}")
