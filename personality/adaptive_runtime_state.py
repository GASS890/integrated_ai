import json
from pathlib import Path


ADAPTIVE_RUNTIME_STATE_PATH = (
    Path(__file__).resolve().parent
    / "adaptive_runtime_state.json"
)


DEFAULT_ADAPTIVE_RUNTIME_STATE = {
    "input_count": 0,
    "output_count": 0,
    "reflection_count": 0,
    "preference_snapshot_count": 0,
    "emotion_decay_count": 0,
    "last_input_result": {},
    "last_output_result": {},
}


def load_adaptive_runtime_state() -> dict:
    if not ADAPTIVE_RUNTIME_STATE_PATH.exists():
        return save_adaptive_runtime_state(
            DEFAULT_ADAPTIVE_RUNTIME_STATE
        )

    try:
        with open(
            ADAPTIVE_RUNTIME_STATE_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception:
        return dict(DEFAULT_ADAPTIVE_RUNTIME_STATE)

    merged = dict(DEFAULT_ADAPTIVE_RUNTIME_STATE)
    merged.update(data or {})

    return merged


def save_adaptive_runtime_state(
    state: dict,
) -> dict:
    merged = dict(DEFAULT_ADAPTIVE_RUNTIME_STATE)
    merged.update(state or {})

    with open(
        ADAPTIVE_RUNTIME_STATE_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            merged,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return merged


def reset_adaptive_runtime_state() -> dict:
    return save_adaptive_runtime_state(
        DEFAULT_ADAPTIVE_RUNTIME_STATE
    )
