import os
import subprocess
from pathlib import Path


def play_wav(path: str) -> dict:
    wav_path = Path(path)

    if not wav_path.exists():
        raise FileNotFoundError(f"wav file not found: {wav_path}")

    try:
        os.startfile(str(wav_path))
        return {
            "status": "ok",
            "method": "os.startfile",
            "file": str(wav_path),
        }
    except Exception:
        subprocess.Popen(
            ["powershell", "-Command", f"Start-Process '{wav_path}'"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {
            "status": "ok",
            "method": "powershell Start-Process",
            "file": str(wav_path),
        }
