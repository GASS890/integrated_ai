from personality.personality_manager import get_profile
from personality.personality_manager import get_runtime_state
from personality.personality_manager import create_default_state
from personality.personality_manager import save_runtime_state_current
from personality.prompt_builder import build_personality_prompt
from personality.runtime_state import RuntimeState


def create_default_personality_state() -> RuntimeState:
    return create_default_state()


def get_current_personality_state() -> RuntimeState:
    return get_runtime_state()


def save_current_personality_state(state: RuntimeState) -> dict:
    return save_runtime_state_current(state)


def build_current_personality_prompt(
    state: RuntimeState | None = None,
) -> str:
    if state is None:
        state = get_current_personality_state()

    return build_personality_prompt(state)


def get_current_personality_profile():
    return get_profile()
