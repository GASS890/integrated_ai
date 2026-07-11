from dataclasses import dataclass


@dataclass
class EmotionState:
    mood: str = "neutral"
    energy: float = 0.5
    confidence: float = 0.5
    stress: float = 0.2
    curiosity: float = 0.5
    focus: float = 0.5
    warmth: float = 0.5
