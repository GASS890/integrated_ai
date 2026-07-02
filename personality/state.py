from dataclasses import dataclass


@dataclass
class PersonalityState:
    mood: str = "neutral"
    energy: int = 50
    confidence: int = 50
