
from personality.profile import PersonalityProfile
from personality.profile_manager import load_profile_data


def load_personality_profile() -> PersonalityProfile:
    data = load_profile_data()

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
