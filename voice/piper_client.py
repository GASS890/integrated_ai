import os
import subprocess
import tempfile
from pathlib import Path


PIPER_EXE = os.getenv("PIPER_EXE", "piper")
PIPER_MODEL = os.getenv("PIPER_MODEL", "models/piper/default.onnx")
PIPER_CONFIG = os.getenv("PIPER_CONFIG", "")


def is_piper_ready() -> bool:
    model_path = Path(PIPER_MODEL)
    return bool(PIPER_EXE) and model_path.exists()


def synthesize_piper(text: str, speaker: int | None = None) -> bytes:
    text = (text or "").strip()
    if not text:
        return b""

    if not is_piper_ready():
        raise RuntimeError(
            f"Piper is not ready. Set PIPER_EXE and PIPER_MODEL. current model={PIPER_MODEL}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav_path = f.name

    cmd = [
        PIPER_EXE,
        "--model",
        PIPER_MODEL,
        "--output_file",
        wav_path,
    ]

    if PIPER_CONFIG:
        cmd.extend(["--config", PIPER_CONFIG])

    try:
        subprocess.run(
            cmd,
            input=text,
            text=True,
            encoding="utf-8",
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        with open(wav_path, "rb") as f:
            return f.read()

    finally:
        try:
            os.remove(wav_path)
        except Exception:
            pass
