import os

from voice.piper_client import is_piper_ready
from voice.piper_plus_client import is_piper_plus_ready
from voice.tts_settings import load_tts_settings, get_default_tts_backend


AVAILABLE_BACKENDS = ["voicevox", "piper", "piper_plus", "auto"]


def get_available_tts_backends() -> dict:
    return {
        "available_backends": AVAILABLE_BACKENDS,
        "recommended": "piper_plus",
        "fallback": "voicevox",
        "notes": {
            "voicevox": "既存PC用。フォールバック用。",
            "piper": "通常Piper用。将来互換用。",
            "piper_plus": "現在の主力TTS。スピーカー側の口を想定。",
            "auto": "Piper Plus > Piper > VOICEVOX の順で自動選択。",
        },
    }


def get_tts_status() -> dict:
    settings = load_tts_settings()

    return {
        "default_backend": get_default_tts_backend(),
        "settings": settings,
        "available_backends": AVAILABLE_BACKENDS,
        "backends": {
            "voicevox": {
                "ready": True,
                "role": "fallback",
            },
            "piper": {
                "ready": is_piper_ready(),
                "role": "compat",
                "model": os.getenv("PIPER_MODEL", "models/piper/default.onnx"),
            },
            "piper_plus": {
                "ready": is_piper_plus_ready(),
                "role": "primary",
                "model": os.getenv(
                    "PIPER_PLUS_MODEL",
                    "tools/piper-plus/src/python_run/tsukuyomi-chan-6lang-fp16.onnx",
                ),
            },
        },
        "role_plan": {
            "speaker": "耳と口。Piper Plus/TTSと音声再生を担当",
            "camera": "目。人・物・表情・姿勢・部屋状況を認識",
            "smartphone": "脳・人格・短期記憶・UI",
            "pc": "長期記憶・Embedding検索・重い処理・音声学習",
            "cloud": "バックアップ・同期",
        },
    }
