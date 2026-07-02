from dataclasses import dataclass, field


@dataclass
class PersonalityProfile:
    name: str = "あなた"
    role: str = "local_ai_assistant"
    tone: str = "calm_polite"
    values: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
