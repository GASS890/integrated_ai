from voice.voicevox_client import synthesize_voice as synthesize_voicevox
from voice.piper_client import synthesize_piper, is_piper_ready
from voice.piper_plus_client import synthesize_piper_plus, is_piper_plus_ready
from voice.tts_settings import load_tts_settings, save_tts_settings, get_default_tts_backend
from voice.tts_status import get_tts_status, get_available_tts_backends


def update_tts_settings(settings: dict) -> dict:
    backend = (settings or {}).get("backend")
    if backend and backend not in ["voicevox", "piper", "piper_plus", "auto"]:
        raise ValueError(f"Unknown TTS backend: {backend}")

    fallback = (settings or {}).get("fallback_backend")
    if fallback and fallback not in ["voicevox", "piper", "piper_plus", "auto"]:
        raise ValueError(f"Unknown fallback TTS backend: {fallback}")

    return save_tts_settings(settings or {})


def _synthesize_selected(text: str, speaker: int, selected: str) -> bytes:
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


def synthesize_voice(text: str, speaker: int = 1, backend: str | None = None) -> bytes:
    settings = load_tts_settings()
    selected = (backend or get_default_tts_backend() or "voicevox").lower()
    speaker = int(speaker or settings.get("speaker", 1))

    try:
        return _synthesize_selected(text, speaker, selected)
    except Exception:
        if not settings.get("auto_fallback", True):
            raise

        fallback = str(settings.get("fallback_backend", "voicevox")).lower()
        if fallback == selected:
            raise

        return _synthesize_selected(text, speaker, fallback)
