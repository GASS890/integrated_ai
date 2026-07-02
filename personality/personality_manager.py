from personality.loader import load_personality_profile
from personality.runtime_manager import (
    create_default_runtime_state,
    load_runtime_state,
    save_runtime_state,
)
from personality.runtime_state import RuntimeState


def get_profile():
    return load_personality_profile()


def create_default_state() -> RuntimeState:
    return create_default_runtime_state()


def get_runtime_state() -> RuntimeState:
    return load_runtime_state()


def save_runtime_state_current(state: RuntimeState) -> dict:
    return save_runtime_state(state)
