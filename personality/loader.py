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

    identity = data.get("identity", {})
    speech = data.get("speech", {})
    personality = data.get("personality", {})
    growth = data.get("growth", {})

    return PersonalityProfile(
        name=identity.get("name", "あなた"),
        role=identity.get("role", "看板キャラ兼開発補助AI"),
        tone=speech.get("tone", "落ち着いた丁寧語"),
        speaking_style=speech.get("speaking_style", "簡潔・親しみやすい"),
        first_person=speech.get("first_person", "私"),
        second_person=speech.get("second_person", "あなた"),
        sentence_endings=speech.get("sentence_endings", []),
        values=personality.get("values", []),
        traits=personality.get("traits", []),
        growth_policy=growth.get("policy", ""),
        learning_rate=growth.get("learning_rate", "low"),
    )
