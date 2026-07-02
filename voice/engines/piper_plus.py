from voice.piper_plus_client import synthesize_piper_plus, is_piper_plus_ready


def synthesize(text: str, speaker: int = 1) -> bytes:
    return synthesize_piper_plus(text, speaker=speaker)


def is_ready() -> bool:
    return is_piper_plus_ready()
