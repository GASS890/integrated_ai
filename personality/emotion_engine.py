import json
from pathlib import Path

from personality.emotion_state import EmotionState


EMOTION_STATE_PATH = (
    Path(__file__).resolve().parent
    / "emotion_state.json"
)


def _clamp(
    value: float,
) -> float:
    return round(
        max(0.0, min(1.0, float(value))),
        4,
    )


def emotion_state_to_dict(
    state: EmotionState,
) -> dict:
    return {
        "mood": state.mood,
        "energy": state.energy,
        "confidence": state.confidence,
        "stress": state.stress,
        "curiosity": state.curiosity,
        "focus": state.focus,
        "warmth": state.warmth,
    }


def emotion_state_from_dict(
    data: dict,
) -> EmotionState:
    data = data or {}

    return EmotionState(
        mood=data.get("mood", "neutral"),
        energy=float(data.get("energy", 0.5)),
        confidence=float(
            data.get("confidence", 0.5)
        ),
        stress=float(data.get("stress", 0.2)),
        curiosity=float(
            data.get("curiosity", 0.5)
        ),
        focus=float(data.get("focus", 0.5)),
        warmth=float(data.get("warmth", 0.5)),
    )


def create_default_emotion_state(
) -> EmotionState:
    return EmotionState()


def save_emotion_state(
    state: EmotionState,
) -> dict:
    data = emotion_state_to_dict(state)

    with open(
        EMOTION_STATE_PATH,
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


def load_emotion_state() -> EmotionState:
    if not EMOTION_STATE_PATH.exists():
        state = create_default_emotion_state()
        save_emotion_state(state)
        return state

    try:
        with open(
            EMOTION_STATE_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception:
        return create_default_emotion_state()

    return emotion_state_from_dict(data)


def update_emotion_from_event(
    event: str,
    intensity: float = 0.1,
) -> dict:
    state = load_emotion_state()
    amount = abs(float(intensity))

    if event == "success":
        state.confidence = _clamp(
            state.confidence + amount
        )
        state.energy = _clamp(
            state.energy + amount * 0.5
        )
        state.stress = _clamp(
            state.stress - amount
        )
        state.mood = "satisfied"

    elif event == "error":
        state.stress = _clamp(
            state.stress + amount
        )
        state.confidence = _clamp(
            state.confidence - amount * 0.4
        )
        state.mood = "concerned"

    elif event == "development":
        state.focus = _clamp(
            state.focus + amount
        )
        state.curiosity = _clamp(
            state.curiosity + amount * 0.5
        )
        state.mood = "focused"

    elif event == "praise":
        state.confidence = _clamp(
            state.confidence + amount * 0.7
        )
        state.warmth = _clamp(
            state.warmth + amount
        )
        state.mood = "pleased"

    elif event == "casual":
        state.stress = _clamp(
            state.stress - amount
        )
        state.warmth = _clamp(
            state.warmth + amount * 0.5
        )
        state.mood = "relaxed"

    elif event == "curiosity":
        state.curiosity = _clamp(
            state.curiosity + amount
        )
        state.focus = _clamp(
            state.focus + amount * 0.3
        )
        state.mood = "curious"

    save_emotion_state(state)

    return emotion_state_to_dict(state)


def decay_emotion_state(
    rate: float = 0.02,
) -> dict:
    state = load_emotion_state()
    amount = abs(float(rate))

    state.energy = _move_toward(
        state.energy,
        0.5,
        amount,
    )

    state.confidence = _move_toward(
        state.confidence,
        0.5,
        amount,
    )

    state.stress = _move_toward(
        state.stress,
        0.2,
        amount,
    )

    state.curiosity = _move_toward(
        state.curiosity,
        0.5,
        amount,
    )

    state.focus = _move_toward(
        state.focus,
        0.5,
        amount,
    )

    state.warmth = _move_toward(
        state.warmth,
        0.5,
        amount,
    )

    if (
        abs(state.energy - 0.5) < 0.05
        and abs(state.stress - 0.2) < 0.05
        and abs(state.focus - 0.5) < 0.05
    ):
        state.mood = "neutral"

    save_emotion_state(state)

    return emotion_state_to_dict(state)


def _move_toward(
    value: float,
    target: float,
    amount: float,
) -> float:
    if value < target:
        return _clamp(
            min(target, value + amount)
        )

    if value > target:
        return _clamp(
            max(target, value - amount)
        )

    return _clamp(value)


def build_emotion_prompt() -> str:
    state = load_emotion_state()

    return f"""
【現在の感情状態】
- mood: {state.mood}
- energy: {state.energy:.2f}
- confidence: {state.confidence:.2f}
- stress: {state.stress:.2f}
- curiosity: {state.curiosity:.2f}
- focus: {state.focus:.2f}
- warmth: {state.warmth:.2f}

【感情表現規則】
- 感情は口調の微調整にだけ使用する
- 正確性・安全性・中立性は感情で変更しない
- stressが高くても攻撃的・乱暴な表現は使わない
- confidenceが高くても不確実なことを断定しない
- 感情表現は人格Profileで許可された範囲に留める
""".strip()
