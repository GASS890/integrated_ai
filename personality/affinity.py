from personality.state_manager import _ensure_personality


def update_personality(session: dict, user_text: str):
    p = _ensure_personality(session)

    text = user_text or ""
    p["turn_count"] += 1

    # 基本：会話するだけで少し親密度上昇
    p["affinity"] += 1

    # 長めの相談・説明依頼は関係性が進んだとみなす
    if len(text) >= 40:
        p["affinity"] += 1

    p["affinity"] = max(0, min(1000, int(p["affinity"])))

    if p["affinity"] < 100:
        p["tone"] = "normal"
    elif p["affinity"] < 300:
        p["tone"] = "friendly"
    else:
        p["tone"] = "close"

    return p