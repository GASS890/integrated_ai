from .models import PersonalityState


def get_default_learning_policy() -> dict:
    return {
        "tone": "medium",
        "values": "low",
        "preferences": "medium",
        "relationship_style": "medium",
        "do_not_learn_sensitive": True,
    }


def normalize_learning_policy(policy: dict | None) -> dict:
    base = get_default_learning_policy()
    if isinstance(policy, dict):
        base.update(policy)
    return base
