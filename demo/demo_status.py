import subprocess
from pathlib import Path

from speaker.speaker_service import get_speaker_status
from voice.tts_status import get_tts_status
from memory.embedding_store import load_embedding_memories


BASE_DIR = Path(__file__).resolve().parent.parent


def _git_short_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=BASE_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _git_latest_tag() -> str:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=BASE_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _memory_status() -> dict:
    try:
        embedding_items = load_embedding_memories()
        return {
            "embedding_memory_count": len(embedding_items),
            "embedding_memory_ready": True,
        }
    except Exception as e:
        return {
            "embedding_memory_count": 0,
            "embedding_memory_ready": False,
            "error": str(e),
        }


def _personality_status() -> dict:
    files = [
        "personality/learning_config.py",
        "personality/tone_profile.py",
        "personality/growth_manager.py",
    ]

    return {
        "learning_config_exists": (BASE_DIR / files[0]).exists(),
        "tone_profile_exists": (BASE_DIR / files[1]).exists(),
        "growth_manager_exists": (BASE_DIR / files[2]).exists(),
        "planned_next": "人格スナップショットと口調レビューを追加予定",
    }


def get_demo_status() -> dict:
    speaker = get_speaker_status()
    tts = get_tts_status()

    return {
        "demo_ready": bool(
            tts.get("backends", {}).get("piper_plus", {}).get("ready")
            and speaker.get("worker", {}).get("running") is not None
        ),
        "version": {
            "git_hash": _git_short_hash(),
            "latest_tag": _git_latest_tag(),
        },
        "tts": tts,
        "speaker": speaker,
        "memory": _memory_status(),
        "personality": _personality_status(),
        "current_capabilities": [
            "テキストチャット",
            "Embedding長期記憶",
            "Piper Plus音声生成",
            "TTSバックエンド切替",
            "Speaker Queue",
            "Speaker Worker",
            "Speaker Audio Player",
            "人格・口調学習の基礎",
        ],
        "next_steps": [
            "34-2 docs/demo_status.md",
            "34-3 start_demo_ai.bat",
            "35-1 character_profile.py",
            "35-2 personality_snapshot.py",
            "35-3 tone_learning_review.py",
        ],
    }
