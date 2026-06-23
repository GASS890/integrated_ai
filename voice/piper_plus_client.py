import os
import subprocess
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PIPER_PLUS_PYTHON = os.getenv(
    "PIPER_PLUS_PYTHON",
    str(BASE_DIR / ".venv_piper_plus" / "Scripts" / "python.exe")
)

PIPER_PLUS_WORKDIR = os.getenv(
    "PIPER_PLUS_WORKDIR",
    str(BASE_DIR / "tools" / "piper-plus" / "src" / "python_run")
)

PIPER_PLUS_MODEL = os.getenv(
    "PIPER_PLUS_MODEL",
    str(BASE_DIR / "tools" / "piper-plus" / "src" / "python_run" / "tsukuyomi-chan-6lang-fp16.onnx")
)


def is_piper_plus_ready() -> bool:
    return (
        Path(PIPER_PLUS_PYTHON).exists()
        and Path(PIPER_PLUS_WORKDIR).exists()
        and Path(PIPER_PLUS_MODEL).exists()
    )


def synthesize_piper_plus(text: str, speaker: int | None = None) -> bytes:
    text = (text or "").strip()
    if not text:
        return b""

    if not is_piper_plus_ready():
        raise RuntimeError(
            "Piper Plus is not ready. "
            f"python={PIPER_PLUS_PYTHON}, workdir={PIPER_PLUS_WORKDIR}, model={PIPER_PLUS_MODEL}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav_path = f.name

    cmd = [
        PIPER_PLUS_PYTHON,
        "-m",
        "piper",
        "--model",
        PIPER_PLUS_MODEL,
        text,
        "--output_file",
        wav_path,
    ]

    try:
        subprocess.run(
            cmd,
            cwd=PIPER_PLUS_WORKDIR,
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
