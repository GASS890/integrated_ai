from typing import TypedDict, Literal


Tone = Literal["normal", "friendly", "close"]
Sentiment = Literal["positive", "neutral", "negative"]
Attitude = Literal["polite", "normal", "aggressive"]


class PersonalityDict(TypedDict, total=False):
    affinity: int
    tone: Tone
    turn_count: int
    last_sentiment: Sentiment
    last_attitude: Attitude
    last_reason: str