from personality.adaptive_dedup import (
    claim_adaptive_event,
)
from personality.adaptive_event_detector import (
    detect_emotion_event,
)
from personality.adaptive_runtime_config import (
    ADAPTIVE_ENABLED,
    DEVELOPER_SESSION_IDS,
    EMOTION_DECAY_INTERVAL,
    EMOTION_ENABLED,
    GROWTH_ENABLED,
    IGNORED_SESSION_PREFIXES,
    IMPORTANT_MEMORY_ENABLED,
    MAX_RECENT_MESSAGES,
    MEMORY_SAVE_THRESHOLD,
    PERSONALITY_GROWTH_ENABLED,
    PREFERENCE_HISTORY_ENABLED,
    PREFERENCE_SNAPSHOT_INTERVAL,
    REFLECTION_ENABLED,
    REFLECTION_INTERVAL,
)
from personality.adaptive_runtime_state import (
    load_adaptive_runtime_state,
    save_adaptive_runtime_state,
)
from personality.emotion_engine import (
    decay_emotion_state,
    update_emotion_from_event,
)
from personality.growth_engine import (
    observe_user_text,
)
from personality.personality_growth_manager import (
    apply_latest_reflection_to_growth,
)
from personality.preference_history import (
    record_user_model_snapshot,
)
from personality.reflection_engine import (
    create_conversation_reflection,
)

from memory.importance_engine import (
    calculate_memory_importance,
)
from memory.importance_store import (
    add_importance_memory,
)


def _should_skip_session(
    session_id: str,
) -> tuple[bool, str]:
    normalized = str(session_id or "").strip()

    if normalized in DEVELOPER_SESSION_IDS:
        return True, "developer_session"

    if any(
        normalized.startswith(prefix)
        for prefix in IGNORED_SESSION_PREFIXES
    ):
        return True, "ignored_session_prefix"

    return False, ""


def process_adaptive_input(
    user_text: str,
    session_id: str = "",
    explicit_memory: bool = False,
) -> dict:
    text = str(user_text or "").strip()

    result = {
        "executed": False,
        "stage": "input",
        "session_id": session_id,
        "growth": {
            "executed": False,
        },
        "memory": {
            "evaluated": False,
            "saved": False,
        },
    }

    if not ADAPTIVE_ENABLED:
        result["reason"] = "adaptive_disabled"
        return result

    if not text:
        result["reason"] = "empty_text"
        return result

    skip, reason = _should_skip_session(
        session_id
    )

    if skip:
        result["reason"] = reason
        return result

    dedup_result = claim_adaptive_event(
        stage="input",
        session_id=session_id,
        user_text=text,
    )

    result["dedup"] = dedup_result

    if not dedup_result.get("allowed", False):
        result["reason"] = "duplicate_event"
        return result

    state = load_adaptive_runtime_state()
    state["input_count"] += 1

    result["executed"] = True

    if GROWTH_ENABLED:
        growth_result = observe_user_text(text)

        result["growth"] = {
            "executed": True,
            "result": growth_result,
        }

    if IMPORTANT_MEMORY_ENABLED:
        evaluation = calculate_memory_importance(
            text=text,
            explicit=explicit_memory,
            source="conversation",
        )

        memory_result = {
            "evaluated": True,
            "saved": False,
            "importance": evaluation[
                "importance"
            ],
            "reasons": evaluation["reasons"],
            "threshold": MEMORY_SAVE_THRESHOLD,
        }

        if (
            evaluation["importance"]
            >= MEMORY_SAVE_THRESHOLD
        ):
            saved = add_importance_memory(
                text=text,
                source="conversation",
                explicit=explicit_memory,
                metadata={
                    "session_id": session_id,
                    "input_count": state[
                        "input_count"
                    ],
                },
            )

            memory_result["saved"] = True
            memory_result["memory"] = saved

        result["memory"] = memory_result

    state["last_input_result"] = result
    save_adaptive_runtime_state(state)

    return result


def process_adaptive_output(
    user_text: str,
    assistant_text: str = "",
    history: list[dict] | None = None,
    session_id: str = "",
    error_occurred: bool = False,
    success: bool = False,
) -> dict:
    result = {
        "executed": False,
        "stage": "output",
        "session_id": session_id,
        "emotion": {
            "executed": False,
        },
        "reflection": {
            "created": False,
        },
        "personality_growth": {
            "updated": False,
        },
        "preference_snapshot": {
            "created": False,
        },
        "emotion_decay": {
            "executed": False,
        },
    }

    if not ADAPTIVE_ENABLED:
        result["reason"] = "adaptive_disabled"
        return result

    skip, reason = _should_skip_session(
        session_id
    )

    if skip:
        result["reason"] = reason
        return result

    dedup_result = claim_adaptive_event(
        stage="output",
        session_id=session_id,
        user_text=user_text,
        assistant_text=assistant_text,
    )

    result["dedup"] = dedup_result

    if not dedup_result.get("allowed", False):
        result["reason"] = "duplicate_event"
        return result

    state = load_adaptive_runtime_state()
    state["output_count"] += 1

    result["executed"] = True

    if EMOTION_ENABLED:
        event_result = detect_emotion_event(
            user_text=user_text,
            assistant_text=assistant_text,
            error_occurred=error_occurred,
            success=success,
        )

        event = event_result.get("event")

        if event:
            emotion_state = (
                update_emotion_from_event(
                    event=event,
                    intensity=event_result.get(
                        "intensity",
                        0.05,
                    ),
                )
            )

            result["emotion"] = {
                "executed": True,
                "event": event,
                "reason": event_result.get(
                    "reason",
                    "",
                ),
                "state": emotion_state,
            }
        else:
            result["emotion"] = {
                "executed": False,
                "reason": "no_event",
            }

    if (
        EMOTION_ENABLED
        and EMOTION_DECAY_INTERVAL > 0
        and state["output_count"]
        % EMOTION_DECAY_INTERVAL
        == 0
    ):
        result["emotion_decay"] = {
            "executed": True,
            "state": decay_emotion_state(),
        }

        state["emotion_decay_count"] += 1

    messages = list(
        history or []
    )[-MAX_RECENT_MESSAGES:]

    if user_text:
        last_message = (
            messages[-1]
            if messages
            else {}
        )

        if not (
            isinstance(last_message, dict)
            and last_message.get("role")
            == "user"
            and last_message.get("content")
            == user_text
        ):
            messages.append({
                "role": "user",
                "content": user_text,
            })

    if assistant_text:
        messages.append({
            "role": "assistant",
            "content": assistant_text,
        })

    should_reflect = (
        REFLECTION_ENABLED
        and REFLECTION_INTERVAL > 0
        and state["output_count"]
        % REFLECTION_INTERVAL
        == 0
    )

    if should_reflect:
        reflection = (
            create_conversation_reflection(
                messages=messages,
                session_id=session_id,
            )
        )

        result["reflection"] = {
            "created": True,
            "reflection": reflection,
        }

        state["reflection_count"] += 1

        if PERSONALITY_GROWTH_ENABLED:
            growth_result = (
                apply_latest_reflection_to_growth()
            )

            result["personality_growth"] = {
                "updated": bool(
                    growth_result.get(
                        "updated",
                        False,
                    )
                ),
                "result": growth_result,
            }

    should_snapshot = (
        PREFERENCE_HISTORY_ENABLED
        and PREFERENCE_SNAPSHOT_INTERVAL > 0
        and state["output_count"]
        % PREFERENCE_SNAPSHOT_INTERVAL
        == 0
    )

    if should_snapshot:
        snapshot = record_user_model_snapshot(
            reason=(
                "adaptive_runtime_"
                f"{state['output_count']}"
            )
        )

        result["preference_snapshot"] = {
            "created": True,
            "snapshot": snapshot,
        }

        state[
            "preference_snapshot_count"
        ] += 1

    state["last_output_result"] = result
    save_adaptive_runtime_state(state)

    return result


def get_adaptive_runtime_status() -> dict:
    return {
        "enabled": ADAPTIVE_ENABLED,
        "config": {
            "growth_enabled": GROWTH_ENABLED,
            "important_memory_enabled": (
                IMPORTANT_MEMORY_ENABLED
            ),
            "emotion_enabled": EMOTION_ENABLED,
            "reflection_enabled": (
                REFLECTION_ENABLED
            ),
            "personality_growth_enabled": (
                PERSONALITY_GROWTH_ENABLED
            ),
            "preference_history_enabled": (
                PREFERENCE_HISTORY_ENABLED
            ),
            "memory_save_threshold": (
                MEMORY_SAVE_THRESHOLD
            ),
            "reflection_interval": (
                REFLECTION_INTERVAL
            ),
            "preference_snapshot_interval": (
                PREFERENCE_SNAPSHOT_INTERVAL
            ),
            "emotion_decay_interval": (
                EMOTION_DECAY_INTERVAL
            ),
        },
        "state": load_adaptive_runtime_state(),
    }
