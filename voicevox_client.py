# voicevox_client.py
import requests

VOICEVOX_URL = "http://127.0.0.1:50021"

def synthesize_voice(
    text: str,
    speaker: int = 1,
    speed: float = 1.0,
    pitch: float = 0.0,
    intonation: float = 1.0
) -> bytes:

    if not text.strip():
        return b""

    # 音声クエリ
    query = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": speaker}
    )
    query.raise_for_status()

    query_json = query.json()

    # ★パラメータ調整
    query_json["speedScale"] = speed
    query_json["pitchScale"] = pitch
    query_json["intonationScale"] = intonation

    # 音声合成
    res = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": speaker},
        json=query_json
    )
    res.raise_for_status()

    return res.content