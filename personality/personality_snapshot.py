import json
from datetime import datetime
from pathlib import Path

from personality.character_profile import get_character_profile
from speaker.speaker_service import get_speaker_status
from demo.demo_status import get_demo_status


BASE_DIR = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = BASE_DIR / "personality_snapshots"


def build_personality_snapshot(note: str = "") -> dict:
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "note": note,
        "character_profile": get_character_profile(),
        "speaker_status": get_speaker_status(),
        "demo_status": get_demo_status(),
    }


def save_personality_snapshot(note: str = "") -> dict:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    snapshot = build_personality_snapshot(note=note)
    filename = "personality_snapshot_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    path = SNAPSHOT_DIR / filename

    path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "status": "ok",
        "path": str(path),
        "created_at": snapshot["created_at"],
        "note": note,
    }


def list_personality_snapshots() -> list[dict]:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    items = []
    for path in sorted(SNAPSHOT_DIR.glob("personality_snapshot_*.json")):
        items.append({
            "filename": path.name,
            "path": str(path),
            "size": path.stat().st_size,
            "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        })

    return items
