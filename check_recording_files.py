from pathlib import Path
import wave


BASE_DIR = Path("tools/Style-Bert-VITS2/Data/あなた")
SCRIPT_PATH = BASE_DIR / "recording_script.txt"
WAV_DIR = BASE_DIR / "raw_wav"


def load_script_numbers() -> list[str]:
    if not SCRIPT_PATH.exists():
        return []

    numbers = []
    for line in SCRIPT_PATH.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if len(line) >= 5 and line[:4].isdigit() and line[4] == ":":
            numbers.append(line[:4])
    return numbers


def get_wav_duration(path: Path) -> float | None:
    try:
        with wave.open(str(path), "rb") as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            if rate <= 0:
                return None
            return frames / float(rate)
    except Exception:
        return None


def check_recordings() -> dict:
    WAV_DIR.mkdir(parents=True, exist_ok=True)

    numbers = load_script_numbers()
    wav_files = sorted(WAV_DIR.glob("*.wav"))

    existing_stems = {p.stem for p in wav_files}
    expected_set = set(numbers)
    expected_files = [f"{num}.wav" for num in numbers]

    missing = [
        name for name in expected_files
        if Path(name).stem not in existing_stems
    ]

    unexpected = [
        p.name for p in wav_files
        if p.stem not in expected_set
    ]

    too_short = []
    unreadable = []

    for p in wav_files:
        duration = get_wav_duration(p)
        if duration is None:
            unreadable.append(p.name)
            continue
        if duration < 0.5:
            too_short.append({
                "file": p.name,
                "duration_sec": round(duration, 3),
            })

    status = "ok"
    if missing or unexpected or too_short or unreadable:
        status = "not_ready"

    return {
        "status": status,
        "script_count": len(numbers),
        "wav_count": len(wav_files),
        "raw_wav_dir": str(WAV_DIR),
        "missing_count": len(missing),
        "missing": missing[:20],
        "unexpected_count": len(unexpected),
        "unexpected": unexpected[:20],
        "too_short_count": len(too_short),
        "too_short": too_short[:20],
        "unreadable_count": len(unreadable),
        "unreadable": unreadable[:20],
        "expected_name_rule": "0001.wav, 0002.wav, 0003.wav ...",
    }


if __name__ == "__main__":
    result = check_recordings()
    for key, value in result.items():
        print(f"{key}: {value}")
