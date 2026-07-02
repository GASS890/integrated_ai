from dataclasses import dataclass, field


@dataclass
class PersonalityProfile:
    name: str
    role: str
    tone: str
    speaking_style: str
    first_person: str = "私"
    second_person: str = "あなた"
    sentence_endings: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    growth_policy: str = ""
    learning_rate: str = "low"
