from pathlib import Path
import csv


BASE = Path("datasets/voice")
METADATA = BASE / "metadata.csv"

TARGET_DIRS = [
    BASE / "raw" / "your_voice",
    BASE / "transcripts",
    BASE / "style_bert_vits2",
    BASE / "checked",
    BASE / "piper_plus",
    BASE / "archive",
    BASE / "exports",
]


def ensure_voice_dataset_dirs():
    for path in TARGET_DIRS:
        path.mkdir(parents=True, exist_ok=True)

    if not METADATA.exists():
        with open(METADATA, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "text", "source", "status", "duration_sec", "notes"])


def scan_voice_dataset():
    ensure_voice_dataset_dirs()

    wav_files = list(BASE.rglob("*.wav"))
    txt_files = list(BASE.rglob("*.txt"))

    metadata_rows = 0
    if METADATA.exists():
        with open(METADATA, "r", encoding="utf-8", newline="") as f:
            metadata_rows = max(sum(1 for _ in f) - 1, 0)

    return {
        "base": str(BASE),
        "wav_count": len(wav_files),
        "txt_count": len(txt_files),
        "metadata_rows": metadata_rows,
        "folders": {str(path): path.exists() for path in TARGET_DIRS},
    }


if __name__ == "__main__":
    ensure_voice_dataset_dirs()
    print(scan_voice_dataset())
