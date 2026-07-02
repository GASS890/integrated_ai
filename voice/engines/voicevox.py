from voice.voicevox_client import synthesize_voice as synthesize_voicevox


def synthesize(text: str, speaker: int = 1) -> bytes:
    return synthesize_voicevox(text, speaker=speaker)


def is_ready() -> bool:
    return True
