from pathlib import Path

from memory.importance_store import (
    IMPORTANCE_MEMORY_PATH,
    list_importance_memories,
)
from personality.adaptive_dedup import (
    reset_adaptive_dedup_state,
)
from personality.adaptive_runtime_coordinator import (
    get_adaptive_runtime_status,
)
from personality.adaptive_runtime_state import (
    reset_adaptive_runtime_state,
)
from personality.emotion_engine import (
    create_default_emotion_state,
    emotion_state_to_dict,
    load_emotion_state,
    save_emotion_state,
)
from personality.personality_growth_manager import (
    PERSONALITY_GROWTH_PATH,
    create_default_growth_state,
    growth_state_to_dict,
    load_personality_growth_state,
    save_personality_growth_state,
)
from personality.preference_history import (
    PREFERENCE_HISTORY_PATH,
)
from personality.reflection_engine import (
    REFLECTION_PATH,
    get_latest_reflection,
)
from personality.user_model_manager import (
    load_user_model,
    reset_user_model,
    user_model_to_dict,
)


ALLOWED_RESET_SCOPES = {
    "runtime",
    "dedup",
    "user_model",
    "emotion",
    "personality_growth",
    "reflections",
    "preference_history",
    "important_memories",
}


def get_adaptive_status_data() -> dict:
    return {
        "runtime": get_adaptive_runtime_status(),
        "user_model": user_model_to_dict(
            load_user_model()
        ),
        "emotion": emotion_state_to_dict(
            load_emotion_state()
        ),
        "personality_growth": growth_state_to_dict(
            load_personality_growth_state()
        ),
        "latest_reflection": (
            get_latest_reflection()
        ),
        "important_memories": (
            list_importance_memories(
                minimum_importance=0.0,
                limit=20,
            )
        ),
    }


def _delete_file(path: Path) -> bool:
    if not path.exists():
        return False

    path.unlink()
    return True


def reset_adaptive_data(
    scopes: list[str] | None = None,
) -> dict:
    requested = scopes or [
        "runtime",
        "dedup",
    ]

    invalid = [
        scope
        for scope in requested
        if scope not in ALLOWED_RESET_SCOPES
    ]

    if invalid:
        return {
            "ok": False,
            "errors": [
                "Unknown reset scope: "
                + ", ".join(invalid)
            ],
            "reset": {},
        }

    reset_result = {}

    for scope in requested:
        if scope == "runtime":
            reset_result[scope] = (
                reset_adaptive_runtime_state()
            )

        elif scope == "dedup":
            reset_result[scope] = (
                reset_adaptive_dedup_state()
            )

        elif scope == "user_model":
            reset_result[scope] = (
                reset_user_model()
            )

        elif scope == "emotion":
            state = create_default_emotion_state()

            reset_result[scope] = (
                save_emotion_state(state)
            )

        elif scope == "personality_growth":
            state = create_default_growth_state()

            reset_result[scope] = (
                save_personality_growth_state(
                    state
                )
            )

        elif scope == "reflections":
            reset_result[scope] = {
                "deleted": _delete_file(
                    REFLECTION_PATH
                )
            }

        elif scope == "preference_history":
            reset_result[scope] = {
                "deleted": _delete_file(
                    PREFERENCE_HISTORY_PATH
                )
            }

        elif scope == "important_memories":
            reset_result[scope] = {
                "deleted": _delete_file(
                    IMPORTANCE_MEMORY_PATH
                )
            }

    return {
        "ok": True,
        "errors": [],
        "reset": reset_result,
        "status": get_adaptive_status_data(),
    }
