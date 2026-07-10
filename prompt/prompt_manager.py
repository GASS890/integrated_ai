from dataclasses import dataclass, field

from prompt.conversation_builder import build_conversation_messages
from prompt.prompt_router import build_prompt_bundle

from prompt.context_builder import build_prompt_context
from prompt.message_builder import build_messages as build_raw_messages


@dataclass
class PromptContext:
    rules_text: str = ""
    personality_text: str = ""
    memories_text: str = ""
    summary_text: str = ""
    metadata: dict = field(default_factory=dict)


def build_system_context(context: PromptContext) -> str:
    return build_prompt_context(
        rules_text=context.rules_text,
        personality_text=context.personality_text,
        memories_text=context.memories_text,
        summary_text=context.summary_text,
    )


def build_messages(
    user_text: str,
    history: list,
    context: PromptContext | None = None,
):
    if context is None:
        context = PromptContext()

    return build_raw_messages(
        user_text=user_text,
        history=history,
        rules_text=context.rules_text,
        personality_text=context.personality_text,
        memories_text=context.memories_text,
        summary_text=context.summary_text,
    )

def build_routed_messages(
    user_text: str,
    history: list,
    context: PromptContext | None = None,
    learning_text: str = "",
    preferences_text: str = "",
):
    if context is None:
        context = PromptContext()

    bundle = build_prompt_bundle(
        rules_text=context.rules_text,
        memories_text=context.memories_text,
        summary_text=context.summary_text,
        learning_text=learning_text,
        preferences_text=preferences_text,
    )

    return build_conversation_messages(
        user_text=user_text,
        history=history,
        bundle=bundle,
    )

