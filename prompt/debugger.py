from prompt.conversation_builder import build_conversation_messages
from prompt.prompt_router import build_prompt_bundle


def build_prompt_debug_data(
    user_text: str = "",
    history: list | None = None,
    rules_text: str = "",
    memories_text: str = "",
    summary_text: str = "",
    learning_text: str = "",
    preferences_text: str = "",
) -> dict:
    bundle = build_prompt_bundle(
        rules_text=rules_text,
        memories_text=memories_text,
        summary_text=summary_text,
        learning_text=learning_text,
        preferences_text=preferences_text,
    )

    messages = build_conversation_messages(
        user_text=user_text,
        history=history or [],
        bundle=bundle,
    )

    return {
        "metadata": bundle.metadata,
        "rules_context": bundle.safety_rules_context,
        "personality_context": bundle.personality_context,
        "personality_growth_context": bundle.personality_growth_context,
        "memory_context": bundle.memory_context,
        "user_model_context": bundle.user_model_context,
        "reflection_context": bundle.reflection_context,
        "emotion_context": bundle.emotion_context,
        "final_system_context": bundle.final_system_context,
        "messages": messages,
    }
