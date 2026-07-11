import hashlib
import json
import time
from pathlib import Path


ADAPTIVE_DEDUP_PATH = (
    Path(__file__).resolve().parent
    / "adaptive_dedup_state.json"
)

DEFAULT_DEDUP_WINDOW_SECONDS = 8
MAX_DEDUP_RECORDS = 500


def _load_state() -> dict:
    if not ADAPTIVE_DEDUP_PATH.exists():
        return {"events": {}}

    try:
        with open(
            ADAPTIVE_DEDUP_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception:
        return {"events": {}}

    if not isinstance(data, dict):
        return {"events": {}}

    events = data.get("events", {})

    if not isinstance(events, dict):
        events = {}

    return {"events": events}


def _save_state(state: dict) -> dict:
    with open(
        ADAPTIVE_DEDUP_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return state


def _normalize_text(text: str) -> str:
    return " ".join(
        str(text or "").strip().split()
    )


def build_event_fingerprint(
    stage: str,
    session_id: str,
    user_text: str,
    assistant_text: str = "",
) -> str:
    source = "\n".join([
        str(stage or "").strip(),
        str(session_id or "").strip(),
        _normalize_text(user_text),
        _normalize_text(assistant_text),
    ])

    return hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()


def claim_adaptive_event(
    stage: str,
    session_id: str,
    user_text: str,
    assistant_text: str = "",
    window_seconds: int = DEFAULT_DEDUP_WINDOW_SECONDS,
) -> dict:
    now = time.time()

    fingerprint = build_event_fingerprint(
        stage=stage,
        session_id=session_id,
        user_text=user_text,
        assistant_text=assistant_text,
    )

    state = _load_state()
    events = state["events"]

    previous = events.get(fingerprint)

    if previous is not None:
        age = now - float(previous)

        if age < max(1, int(window_seconds)):
            return {
                "allowed": False,
                "reason": "duplicate_event",
                "fingerprint": fingerprint,
                "age_seconds": round(age, 3),
            }

    events[fingerprint] = now

    cutoff = now - 3600

    events = {
        key: timestamp
        for key, timestamp in events.items()
        if float(timestamp) >= cutoff
    }

    if len(events) > MAX_DEDUP_RECORDS:
        sorted_events = sorted(
            events.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        events = dict(
            sorted_events[:MAX_DEDUP_RECORDS]
        )

    state["events"] = events
    _save_state(state)

    return {
        "allowed": True,
        "reason": "",
        "fingerprint": fingerprint,
    }


def reset_adaptive_dedup_state() -> dict:
    return _save_state({
        "events": {},
    })
