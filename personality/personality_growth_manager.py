import json
from pathlib import Path

from personality.personality_growth_state import (
    PersonalityGrowthState,
)
from personality.reflection_engine import (
    get_latest_reflection,
)


PERSONALITY_GROWTH_PATH = (
    Path(__file__).resolve().parent
    / "personality_growth_state.json"
)


def _clamp(
    value: float,
) -> float:
    return round(
        max(0.0, min(1.0, float(value))),
        4,
    )


def create_default_growth_state(
) -> PersonalityGrowthState:
    return PersonalityGrowthState(
        specialties={
            "AI開発": 0.3,
            "記憶": 0.3,
            "音声": 0.3,
            "Web/API": 0.3,
            "Python": 0.3,
            "Git": 0.3,
        },
        response_skills={
            "構造化説明": 0.4,
            "段階的案内": 0.4,
            "根拠付き説明": 0.4,
        },
    )


def growth_state_to_dict(
    state: PersonalityGrowthState,
) -> dict:
    return {
        "experience_points": state.experience_points,
        "confidence": state.confidence,
        "specialties": dict(state.specialties),
        "response_skills": dict(
            state.response_skills
        ),
        "reflection_count": state.reflection_count,
    }


def growth_state_from_dict(
    data: dict,
) -> PersonalityGrowthState:
    data = data or {}

    return PersonalityGrowthState(
        experience_points=int(
            data.get("experience_points", 0)
        ),
        confidence=float(
            data.get("confidence", 0.5)
        ),
        specialties=dict(
            data.get("specialties", {})
        ),
        response_skills=dict(
            data.get("response_skills", {})
        ),
        reflection_count=int(
            data.get("reflection_count", 0)
        ),
    )


def save_personality_growth_state(
    state: PersonalityGrowthState,
) -> dict:
    data = growth_state_to_dict(state)

    with open(
        PERSONALITY_GROWTH_PATH,
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


def load_personality_growth_state(
) -> PersonalityGrowthState:
    if not PERSONALITY_GROWTH_PATH.exists():
        state = create_default_growth_state()
        save_personality_growth_state(state)
        return state

    try:
        with open(
            PERSONALITY_GROWTH_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception:
        return create_default_growth_state()

    return growth_state_from_dict(data)


def apply_latest_reflection_to_growth(
) -> dict:
    reflection = get_latest_reflection()

    if not reflection:
        return {
            "updated": False,
            "reason": "no_reflection",
        }

    state = load_personality_growth_state()
    topics = reflection.get("topics", {})
    preferences = reflection.get(
        "preference_signals",
        {},
    )

    updates = []

    for topic, count in topics.items():
        current = float(
            state.specialties.get(topic, 0.3)
        )

        amount = min(
            0.03,
            0.005 * int(count),
        )

        state.specialties[topic] = _clamp(
            current + amount
        )

        updates.append({
            "type": "specialty",
            "key": topic,
            "score": state.specialties[topic],
        })

    if preferences.get(
        "段階的な手順",
        0,
    ):
        current = state.response_skills.get(
            "段階的案内",
            0.4,
        )

        state.response_skills[
            "段階的案内"
        ] = _clamp(current + 0.01)

    if preferences.get(
        "詳しい説明",
        0,
    ):
        current = state.response_skills.get(
            "構造化説明",
            0.4,
        )

        state.response_skills[
            "構造化説明"
        ] = _clamp(current + 0.01)

    state.experience_points += max(
        1,
        int(
            reflection.get(
                "user_message_count",
                1,
            )
        ),
    )

    state.reflection_count += 1

    state.confidence = _clamp(
        0.5
        + min(
            0.3,
            state.reflection_count * 0.002,
        )
    )

    save_personality_growth_state(state)

    return {
        "updated": True,
        "updates": updates,
        "state": growth_state_to_dict(state),
    }


def build_personality_growth_prompt() -> str:
    state = load_personality_growth_state()

    specialties = sorted(
        state.specialties.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    skills = sorted(
        state.response_skills.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    lines = [
        "【経験による成長状態】",
        (
            "- 経験値: "
            f"{state.experience_points}"
        ),
        (
            "- 推定自信度: "
            f"{state.confidence:.2f}"
        ),
        "- 得意分野:",
    ]

    lines.extend(
        f"  - {key}: {score:.2f}"
        for key, score in specialties
        if score >= 0.35
    )

    lines.append("- 応答技能:")

    lines.extend(
        f"  - {key}: {score:.2f}"
        for key, score in skills
        if score >= 0.35
    )

    lines.extend([
        "",
        "【成長適用ルール】",
        "- 人格の核心・価値観・口調は変更しない",
        "- 得意分野は関連する質問でのみ活用する",
        "- 自信度が高くても、不確実な内容は断定しない",
        "- 成長状態は経験の補助情報として使用する",
    ])

    return "\n".join(lines)
