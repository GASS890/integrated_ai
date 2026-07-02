from dataclasses import dataclass, field

@dataclass
class PersonalityProfile:
    name: str
    role: str
    tone: str
    speaking_style: str
    values: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    growth_policy: str = ""
