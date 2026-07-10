import json
from pathlib import Path

from personality.user_model import UserModel


USER_MODEL_PATH = (
    Path(__file__).resolve().parent
    / "user_model.json"
)


DEFAULT_USER_MODEL = UserModel(
    interests={
        "AI開発": 0.5,
        "Python": 0.5,
        "FastAPI": 0.5,
        "音声AI": 0.5,
    },
    preferences={
        "PowerShell形式": 0.5,
        "手順を細かく": 0.5,
        "コード全文": 0.5,
        "バージョン管理": 0.5,
    },
    knowledge_level={
        "AI": 0.5,
        "Python": 0.5,
        "Git": 0.5,
        "FastAPI": 0.5,
    },
    conversation_style={
        "詳細さ": 0.5,
        "構造化": 0.5,
        "理由付き説明": 0.5,
    },
)


def _clamp_score(value: float) -> float:
    return round(
        max(0.0, min(1.0, float(value))),
        4,
    )


def user_model_to_dict(model: UserModel) -> dict:
    return {
        "interests": dict(model.interests),
        "preferences": dict(model.preferences),
        "knowledge_level": dict(model.knowledge_level),
        "conversation_style": dict(model.conversation_style),
        "observations": dict(model.observations),
    }


def user_model_from_dict(data: dict) -> UserModel:
    data = data or {}

    return UserModel(
        interests=dict(data.get("interests", {})),
        preferences=dict(data.get("preferences", {})),
        knowledge_level=dict(data.get("knowledge_level", {})),
        conversation_style=dict(
            data.get("conversation_style", {})
        ),
        observations=dict(data.get("observations", {})),
    )


def create_default_user_model() -> UserModel:
    return user_model_from_dict(
        user_model_to_dict(DEFAULT_USER_MODEL)
    )


def save_user_model(model: UserModel) -> dict:
    data = user_model_to_dict(model)

    USER_MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        USER_MODEL_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return data


def load_user_model() -> UserModel:
    if not USER_MODEL_PATH.exists():
        model = create_default_user_model()
        save_user_model(model)
        return model

    try:
        with open(
            USER_MODEL_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception:
        return create_default_user_model()

    return user_model_from_dict(data)


def update_score(
    category: str,
    key: str,
    amount: float,
) -> dict:
    model = load_user_model()

    category_data = getattr(model, category, None)

    if not isinstance(category_data, dict):
        raise ValueError(
            f"Unknown user model category: {category}"
        )

    current = float(category_data.get(key, 0.5))
    category_data[key] = _clamp_score(current + amount)

    observation_key = f"{category}:{key}"
    model.observations[observation_key] = (
        int(model.observations.get(observation_key, 0))
        + 1
    )

    save_user_model(model)

    return {
        "category": category,
        "key": key,
        "score": category_data[key],
        "observations": model.observations[
            observation_key
        ],
    }


def set_score(
    category: str,
    key: str,
    value: float,
) -> dict:
    model = load_user_model()

    category_data = getattr(model, category, None)

    if not isinstance(category_data, dict):
        raise ValueError(
            f"Unknown user model category: {category}"
        )

    category_data[key] = _clamp_score(value)

    save_user_model(model)

    return {
        "category": category,
        "key": key,
        "score": category_data[key],
    }


def reset_user_model() -> dict:
    model = create_default_user_model()
    return save_user_model(model)
