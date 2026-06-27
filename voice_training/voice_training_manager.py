import csv
import json
from pathlib import Path


BASE_DIR = Path("voice_training")
CONFIG_PATH = BASE_DIR / "configs" / "voice_training_config.json"
METADATA_PATH = BASE_DIR / "metadata.csv"

TARGET_DIRS = [
    BASE_DIR / "raw_voice",
    BASE_DIR / "cleaned_voice",
    BASE_DIR / "transcripts",
    BASE_DIR / "stylebert_dataset",
    BASE_DIR / "teacher_audio",
    BASE_DIR / "piper_dataset",
    BASE_DIR / "exports",
    BASE_DIR / "configs",
]


def ensure_voice_training_workspace():
    for path in TARGET_DIRS:
        path.mkdir(parents=True, exist_ok=True)

    if not METADATA_PATH.exists():
        with open(METADATA_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "text", "source", "status", "duration_sec", "notes"])


def load_voice_training_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}

    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def scan_voice_training_workspace() -> dict:
    ensure_voice_training_workspace()

    wav_files = list(BASE_DIR.rglob("*.wav"))
    txt_files = list(BASE_DIR.rglob("*.txt"))

    metadata_rows = 0
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8", newline="") as f:
            metadata_rows = max(sum(1 for _ in f) - 1, 0)

    return {
        "base": str(BASE_DIR),
        "config": load_voice_training_config(),
        "wav_count": len(wav_files),
        "txt_count": len(txt_files),
        "metadata_rows": metadata_rows,
        "folders": {str(path): path.exists() for path in TARGET_DIRS},
    }


if __name__ == "__main__":
    print(scan_voice_training_workspace())
