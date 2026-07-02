from voice.tts_settings import load_tts_settings, save_tts_settings, get_default_tts_backend
from voice.tts_status import get_tts_status, get_available_tts_backends
from voice.engine_registry import get_engine_names
from voice.engines import voicevox, piper, piper_plus


ENGINE_PLUGINS = {
    "voicevox": voicevox,
    "piper": piper,
    "piper_plus": piper_plus,
}


def update_tts_settings(settings: dict) -> dict:
    backend = (settings or {}).get("backend")
    if backend and backend not in get_engine_names():
        raise ValueError(f"Unknown TTS backend: {backend}")

    fallback = (settings or {}).get("fallback_backend")
    if fallback and fallback not in get_engine_names():
        raise ValueError(f"Unknown fallback TTS backend: {fallback}")

    return save_tts_settings(settings or {})


def _is_voicevox_enabled(settings: dict | None = None) -> bool:
    settings = settings or load_tts_settings()
    return bool(settings.get("voicevox_enabled", False))


def _synthesize_engine(text: str, speaker: int, selected: str, settings: dict) -> bytes:
    if selected == "voicevox" and not _is_voicevox_enabled(settings):
        raise RuntimeError("VOICEVOX is disabled by settings.")

    engine = ENGINE_PLUGINS.get(selected)
    if engine is None:
        raise ValueError(f"Unknown TTS backend: {selected}")

    return engine.synthesize(text, speaker=speaker)


def _synthesize_auto(text: str, speaker: int, settings: dict) -> bytes:
    if piper_plus.is_ready():
        return piper_plus.synthesize(text, speaker=speaker)

    if piper.is_ready():
        return piper.synthesize(text, speaker=speaker)

    if _is_voicevox_enabled(settings):
        return voicevox.synthesize(text, speaker=speaker)

    raise RuntimeError("No available TTS backend. VOICEVOX is disabled.")


def _synthesize_selected(text: str, speaker: int, selected: str, settings: dict) -> bytes:
    if selected == "auto":
        return _synthesize_auto(text, speaker, settings)

    return _synthesize_engine(text, speaker, selected, settings)


def synthesize_voice(text: str, speaker: int = 1, backend: str | None = None) -> bytes:
    settings = load_tts_settings()
    selected = (backend or get_default_tts_backend() or "voicevox").lower()
    speaker = int(speaker or settings.get("speaker", 1))

    try:
        return _synthesize_selected(text, speaker, selected, settings)
    except Exception:
        if not settings.get("auto_fallback", True):
            raise

        fallback = str(settings.get("fallback_backend", "voicevox")).lower()
        if fallback == selected:
            raise
        if fallback == "voicevox" and not settings.get("voicevox_enabled", False):
            raise RuntimeError("Fallback VOICEVOX is disabled by settings.")

        return _synthesize_selected(text, speaker, fallback, settings)
