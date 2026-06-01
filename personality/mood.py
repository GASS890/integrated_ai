def get_mood_from_personality(session: dict) -> str:
    p = session.get("personality", {})

    last_sentiment = p.get("last_sentiment", "neutral")
    tone = p.get("tone", "normal")

    if last_sentiment == "positive":
        return "cheerful"

    if last_sentiment == "negative":
        return "cautious"

    if tone == "close":
        return "relaxed"

    return "calm"