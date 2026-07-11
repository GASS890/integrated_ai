from dataclasses import dataclass, field

from memory.prompt_builder import build_memory_prompt
from personality.persona_manager import build_current_personality_prompt
from personality.runtime_state import RuntimeState
from personality.user_model_prompt import build_user_model_prompt
from prompt.context_builder import build_prompt_context


@dataclass
class PromptBundle:
    safety_rules_context: str = ""
    personality_context: str = ""
    memory_context: str = ""
    user_model_context: str = ""
    final_system_context: str = ""
    metadata: dict = field(default_factory=dict)


def build_prompt_bundle(
    rules_text: str = "",
    memories_text: str = "",
    summary_text: str = "",
    learning_text: str = "",
    preferences_text: str = "",
    runtime_state: RuntimeState | None = None,
) -> PromptBundle:
    personality_context = build_current_personality_prompt(
        runtime_state
    )

    memory_context = build_memory_prompt(
        memories_text=memories_text,
        summary_text=summary_text,
        learning_text=learning_text,
        preferences_text=preferences_text,
    )

    user_model_context = build_user_model_prompt()

    combined_memory_context = "\n\n".join(
        section
        for section in (
            memory_context,
            user_model_context,
        )
        if section
    )

    final_system_context = build_prompt_context(
        rules_text=rules_text,
        personality_text=personality_context,
        memories_text=combined_memory_context,
        summary_text="",
    )

    return PromptBundle(
        safety_rules_context=rules_text,
        personality_context=personality_context,
        memory_context=memory_context,
        user_model_context=user_model_context,
        final_system_context=final_system_context,
        metadata={
            "has_rules": bool(rules_text),
            "has_personality": bool(personality_context),
            "has_memory": bool(memory_context),
            "has_user_model": bool(user_model_context),
        },
    )
