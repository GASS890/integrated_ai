from personality.loader import load_personality_profile
from personality.state import PersonalityState


def build_personality_prompt(
    state: PersonalityState,
) -> str:

    profile = load_personality_profile()

    values = "\n".join(f"- {v}" for v in profile.values)
    traits = "\n".join(f"- {t}" for t in profile.traits)

    return f"""
あなたはローカルAIの人格モジュールです。

名前:
{profile.name}

役割:
{profile.role}

口調:
{profile.tone}

話し方:
{profile.speaking_style}

価値観:
{values}

性格特徴:
{traits}

成長方針:
{profile.growth_policy}

現在状態:
- mood: {state.mood}
- energy: {state.energy}
- confidence: {state.confidence}
- user_tone: {state.user_tone}
- conversation_mode: {state.conversation_mode}
""".strip()
