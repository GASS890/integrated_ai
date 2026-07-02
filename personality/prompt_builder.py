from personality.profile import PersonalityProfile
from personality.state import PersonalityState


def build_personality_prompt(
    profile: PersonalityProfile,
    state: PersonalityState,
) -> str:
    return (
        f"Name: {profile.name}\n"
        f"Role: {profile.role}\n"
        f"Tone: {profile.tone}\n"
        f"Mood: {state.mood}\n"
        f"Energy: {state.energy}\n"
        f"Confidence: {state.confidence}\n"
    )
