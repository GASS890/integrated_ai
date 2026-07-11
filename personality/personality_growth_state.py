from dataclasses import dataclass, field


@dataclass
class PersonalityGrowthState:
    experience_points: int = 0
    confidence: float = 0.5
    specialties: dict[str, float] = field(
        default_factory=dict
    )
    response_skills: dict[str, float] = field(
        default_factory=dict
    )
    reflection_count: int = 0
