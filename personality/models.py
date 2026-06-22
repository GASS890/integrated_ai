from dataclasses import dataclass, field
from typing import Any


@dataclass
class PersonalityState:
    personality_id: str = "default"
    mood: str = "neutral"
    affinity: int = 0
    traits: dict[str, Any] = field(default_factory=dict)
    learning_policy: dict[str, Any] = field(default_factory=dict)
