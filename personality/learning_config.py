LEARNING_STRENGTH = {
    "口調": "高",
    "好み": "中",
    "価値観": "低",
    "性格": "中",
    "開発方針": "高",
    "debug": "中",
    "conversation_reflection": "中",
}

WEIGHT_MAP = {
    "高": 1.3,
    "中": 1.0,
    "低": 0.5,
    "なし": 0.0,
}


def get_learning_strength(category: str) -> str:
    category = category or "conversation_reflection"
    return LEARNING_STRENGTH.get(category, "中")


def get_learning_weight(category: str) -> float:
    strength = get_learning_strength(category)
    return WEIGHT_MAP.get(strength, 1.0)


def describe_learning_strength() -> dict:
    return {
        "learning_strength": dict(LEARNING_STRENGTH),
        "weight_map": dict(WEIGHT_MAP),
    }
