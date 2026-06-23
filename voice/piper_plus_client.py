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

PIPER_PLUS_CONFIG = os.getenv(
    "PIPER_PLUS_CONFIG",
    str(BASE_DIR / "tools" / "piper-plus" / "src" / "python_run" / "config.json")
)


def is_piper_plus_ready() -> bool:
    return (
        Path(PIPER_PLUS_PYTHON).exists()
        and Path(PIPER_PLUS_WORKDIR).exists()
        and Path(PIPER_PLUS_MODEL).exists()
        and Path(PIPER_PLUS_CONFIG).exists()
    )


def synthesize_piper_plus(text: str, speaker: int | None = None) -> bytes:
    text = (text or "").strip()
    if not text:
        return b""

    if not is_piper_plus_ready():
        raise RuntimeError(
            "Piper Plus is not ready. "
            f"python={PIPER_PLUS_PYTHON}, workdir={PIPER_PLUS_WORKDIR}, "
            f"model={PIPER_PLUS_MODEL}, config={PIPER_PLUS_CONFIG}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav_path = f.name

    cmd = [
        PIPER_PLUS_PYTHON,
        "-m",
        "piper",
        "--model",
        PIPER_PLUS_MODEL,
        "--config",
        PIPER_PLUS_CONFIG,
        text,
        "--output_file",
        wav_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=PIPER_PLUS_WORKDIR,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Piper Plus synthesis failed.\n"
                f"command={cmd}\n"
                f"stdout={result.stdout}\n"
                f"stderr={result.stderr}"
            )

        with open(wav_path, "rb") as f:
            return f.read()

    finally:
        try:
            os.remove(wav_path)
        except Exception:
            pass
