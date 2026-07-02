import json
from pathlib import Path

from personality.profile import PersonalityProfile

PROFILE_PATH = (
    Path(__file__).resolve().parent
    / "personality_profile.json"
)


def load_personality_profile() -> PersonalityProfile:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return PersonalityProfile(**data)
