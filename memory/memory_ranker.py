from personality.learning_config import get_learning_weight, get_learning_strength


def _memory_category(item: dict) -> str:
    meta = item.get("meta", {}) or {}
    return meta.get("category") or meta.get("type") or "conversation_reflection"


def rank_memories(memories, learning_strength=None):
    """
    learning_strength を指定した場合は一時的に上書き。
    省略時は personality.learning_config.LEARNING_STRENGTH を使用。
    """
    learning_strength = learning_strength or {}

    local_weight_map = {
        "高": 1.3,
        "中": 1.0,
        "低": 0.5,
        "なし": 0.0,
    }

    def category_weight(item):
        category = _memory_category(item)
        if category in learning_strength:
            return local_weight_map.get(learning_strength.get(category), 1.0)
        return get_learning_weight(category)

    ranked = []
    for item in memories:
        score = float(item.get("score", 0.0))
        importance = float(item.get("importance", 0.5))
        access = min(int(item.get("access_count", 0)), 10) * 0.01
        category = _memory_category(item)
        strength = learning_strength.get(category) or get_learning_strength(category)

        final_score = (score * 0.75 + importance * 0.2 + access) * category_weight(item)

        copied = dict(item)
        copied["category"] = category
        copied["learning_strength"] = strength
        copied["learning_weight"] = category_weight(item)
        copied["rank_score"] = final_score
        ranked.append(copied)

    ranked.sort(key=lambda x: x["rank_score"], reverse=True)
    return ranked
