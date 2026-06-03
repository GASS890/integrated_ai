import json
import os
import time


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(BASE_DIR, "personality_state.json")


def _init_personality():
    return {
        "affinity": 0,
        "tone": "normal",
        "turn_count": 0,
        "last_sentiment": "neutral",
        "last_attitude": "normal",
        "last_reason": "",
        "updated_at": time.time(),
    }


def load_personality_states() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_personality_states(states: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(states, f, ensure_ascii=False, indent=2)


def _normalize_personality(p: dict) -> dict:
    base = _init_personality()

    if not isinstance(p, dict):
        return base

    base.update(p)

    base["affinity"] = max(0, min(1000, int(base.get("affinity", 0))))
    base["turn_count"] = max(0, int(base.get("turn_count", 0)))

    if base.get("tone") not in ["normal", "friendly", "close"]:
        base["tone"] = "normal"

    if base.get("last_sentiment") not in ["positive", "neutral", "negative"]:
        base["last_sentiment"] = "neutral"

    if base.get("last_attitude") not in ["polite", "normal", "aggressive"]:
        base["last_attitude"] = "normal"

    base["updated_at"] = time.time()

    return base


def get_personality_key(session: dict) -> str:
    return str(session.get("personality_id") or session.get("id") or "default")


def _ensure_personality(session: dict) -> dict:
    key = get_personality_key(session)
    session["personality_id"] = key

    states = load_personality_states()

    if key not in states:
        states[key] = session.get("personality") or _init_personality()

    p = _normalize_personality(states[key])

    states[key] = p
    save_personality_states(states)

    session["personality"] = p

    return p


def save_personality(session: dict) -> dict:
    key = get_personality_key(session)
    p = _normalize_personality(session.get("personality") or _init_personality())

    states = load_personality_states()
    states[key] = p
    save_personality_states(states)

    session["personality"] = p

    return p

def save_personality_by_id(personality_id: str, personality: dict) -> dict:
    key = str(personality_id or "default")
    p = _normalize_personality(personality)

    states = load_personality_states()
    states[key] = p
    save_personality_states(states)

    return p


def load_personality_by_id(personality_id: str) -> dict:
    key = str(personality_id or "default")

    states = load_personality_states()

    if key not in states:
        states[key] = _init_personality()
        save_personality_states(states)

    return _normalize_personality(states[key])