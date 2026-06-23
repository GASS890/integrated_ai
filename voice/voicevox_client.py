from voicevox_client import synthesize_voice as synthesize_voicevox


def synthesize_voice(text: str, speaker: int = 1) -> bytes:
    return synthesize_voicevox(text, speaker=speaker)
