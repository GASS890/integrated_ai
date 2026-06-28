from pathlib import Path

base = Path("tools/Style-Bert-VITS2/Data")

speaker = "あなた"

folders = [
    base / speaker,
    base / speaker / "raw",
    base / speaker / "raw_wav",
    base / speaker / "raw_mp3",
    base / speaker / "processed",
    base / speaker / "dataset",
    base / speaker / "transcripts",
    base / speaker / "backup",
]

for f in folders:
    f.mkdir(parents=True, exist_ok=True)

readme = base / speaker / "README.txt"

readme.write_text(
"""Style-Bert-VITS2 Training Folder

raw/
    元音声

raw_wav/
    WAV化した音声

raw_mp3/
    MP3保管

processed/
    前処理済み

dataset/
    学習データ

transcripts/
    文字起こし

backup/
    バックアップ
""",
encoding="utf-8"
)

print("created:")
for f in folders:
    print(" ", f)

print()
print("README:", readme.exists())
