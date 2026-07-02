import json
from pathlib import Path

from personality.runtime_state import RuntimeState

RUNTIME_STATE_PATH = (
    Path(__file__).resolve().parent
    / "runtime_state.json"
)


def create_default_runtime_state() -> RuntimeState:
    return RuntimeState()


def runtime_state_to_dict(state: RuntimeState) -> dict:
    return {
        "mood": state.mood,
        "energy": state.energy,
        "confidence": state.confidence,
        "user_tone": state.user_tone,
        "conversation_mode": state.conversation_mode,
    }


def runtime_state_from_dict(data: dict) -> RuntimeState:
    data = data or {}

    return RuntimeState(
        mood=data.get("mood", "neutral"),
        energy=int(data.get("energy", 50)),
        confidence=int(data.get("confidence", 50)),
        user_tone=data.get("user_tone", "normal"),
        conversation_mode=data.get("conversation_mode", "development_support"),
    )


def load_runtime_state() -> RuntimeState:
    if not RUNTIME_STATE_PATH.exists():
        state = create_default_runtime_state()
        save_runtime_state(state)
        return state

    try:
        with open(RUNTIME_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return create_default_runtime_state()

    return runtime_state_from_dict(data)


def save_runtime_state(state: RuntimeState) -> dict:
    data = runtime_state_to_dict(state)

    with open(RUNTIME_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def reset_runtime_state() -> dict:
    state = create_default_runtime_state()
    return save_runtime_state(state)
