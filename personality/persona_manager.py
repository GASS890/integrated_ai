from personality.loader import load_personality_profile
from personality.prompt_builder import build_personality_prompt
from personality.state import PersonalityState


def create_default_personality_state() -> PersonalityState:
    return PersonalityState()


def build_current_personality_prompt(
    state: PersonalityState | None = None,
) -> str:
    if state is None:
        state = create_default_personality_state()

    return build_personality_prompt(state)


def get_current_personality_profile():
    return load_personality_profile()
