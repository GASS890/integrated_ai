def _init_personality():
    return {
        "affinity": 0,
        "tone": "normal",
        "turn_count": 0,
    }


def _ensure_personality(session: dict) -> dict:
    p = session.setdefault("personality", _init_personality())

    if "affinity" not in p:
        p["affinity"] = 0
    if "tone" not in p:
        p["tone"] = "normal"
    if "turn_count" not in p:
        p["turn_count"] = 0

    return p