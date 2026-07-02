from personality.loader import load_personality_profile
from personality.prompt_builder import build_personality_prompt
from personality.runtime_manager import (
    create_default_runtime_state,
    load_runtime_state,
    save_runtime_state,
)
from personality.runtime_state import RuntimeState


def create_default_personality_state() -> RuntimeState:
    return create_default_runtime_state()


def get_current_personality_state() -> RuntimeState:
    return load_runtime_state()


def save_current_personality_state(state: RuntimeState) -> dict:
    return save_runtime_state(state)


def build_current_personality_prompt(
    state: RuntimeState | None = None,
) -> str:
    if state is None:
        state = get_current_personality_state()

    return build_personality_prompt(state)


def get_current_personality_profile():
    return load_personality_profile()
