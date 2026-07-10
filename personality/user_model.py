from dataclasses import dataclass, field


@dataclass
class UserModel:
    interests: dict[str, float] = field(default_factory=dict)
    preferences: dict[str, float] = field(default_factory=dict)
    knowledge_level: dict[str, float] = field(default_factory=dict)
    conversation_style: dict[str, float] = field(default_factory=dict)
    observations: dict[str, int] = field(default_factory=dict)
