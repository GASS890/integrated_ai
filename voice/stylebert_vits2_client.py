from pathlib import Path
from datetime import datetime
import requests


DEFAULT_URL = "http://127.0.0.1:5000/voice"


def stylebert_say(
    text: str,
    output_dir: str = "outputs/tts",
    model_id: int = 0,
    speaker_id: int = 0,
    style: str = "Neutral",
    style_weight: float = 5.0,
    length: float = 1.0,
    language: str = "JP",
    server_url: str = DEFAULT_URL,
) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("text is empty")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    params = {
        "text": text,
        "model_id": model_id,
        "speaker_id": speaker_id,
        "style": style,
        "style_weight": style_weight,
        "length": length,
        "language": language,
        "auto_split": True,
        "split_interval": 0.5,
    }

    response = requests.get(server_url, params=params, timeout=120)
    response.raise_for_status()

    filename = "stylebert_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".wav"
    output_path = Path(output_dir) / filename
    output_path.write_bytes(response.content)

    return {
        "status": "ok",
        "backend": "style_bert_vits2",
        "output_file": str(output_path.resolve()),
        "bytes": output_path.stat().st_size,
        "server_url": server_url,
        "model_id": model_id,
        "speaker_id": speaker_id,
        "style": style,
    }
