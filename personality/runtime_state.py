from dataclasses import dataclass


@dataclass
class RuntimeState:
    mood: str = "neutral"
    energy: int = 50
    confidence: int = 50
    user_tone: str = "normal"
    conversation_mode: str = "development_support"
