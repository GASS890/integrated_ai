from .models import PersonalityState
from .learning_policy import normalize_learning_policy


def build_personality_state(raw: dict | None) -> PersonalityState:
    raw = raw if isinstance(raw, dict) else {}

    return PersonalityState(
        personality_id=raw.get("personality_id", "default"),
        mood=raw.get("mood", "neutral"),
        affinity=int(raw.get("affinity", 0) or 0),
        traits=raw.get("traits", {}) if isinstance(raw.get("traits", {}), dict) else {},
        learning_policy=normalize_learning_policy(raw.get("learning_policy")),
    )


def personality_state_to_dict(state: PersonalityState) -> dict:
    return {
        "personality_id": state.personality_id,
        "mood": state.mood,
        "affinity": state.affinity,
        "traits": state.traits,
        "learning_policy": state.learning_policy,
    }


def normalize_session_personality(session: dict) -> dict:
    if not isinstance(session, dict):
        return session

    raw_personality = session.get("personality", {})

    if not isinstance(raw_personality, dict):
        raw_personality = {}

    if "personality_id" not in raw_personality:
        raw_personality["personality_id"] = session.get("personality_id", "default")

    state = build_personality_state(raw_personality)
    session["personality"] = personality_state_to_dict(state)
    session["personality_id"] = state.personality_id

    return session


def normalize_sessions_personality(sessions: dict) -> dict:
    if not isinstance(sessions, dict):
        return sessions

    for _, session in sessions.items():
        if isinstance(session, dict):
            normalize_session_personality(session)

    return sessions
