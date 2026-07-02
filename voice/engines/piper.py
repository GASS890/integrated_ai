from voice.piper_client import synthesize_piper, is_piper_ready


def synthesize(text: str, speaker: int = 1) -> bytes:
    return synthesize_piper(text, speaker=speaker)


def is_ready() -> bool:
    return is_piper_ready()
