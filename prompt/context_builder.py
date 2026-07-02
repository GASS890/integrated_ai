from prompt.providers import safety_provider
from prompt.providers import rule_provider
from prompt.providers import personality_provider
from prompt.providers import memory_provider
from prompt.providers import summary_provider


def build_prompt_context(
    rules_text: str = "",
    personality_text: str = "",
    memories_text: str = "",
    summary_text: str = "",
) -> str:
    sections = [
        safety_provider.build(),
        rule_provider.build(rules_text),
        personality_provider.build(personality_text),
        memory_provider.build(memories_text),
        summary_provider.build(summary_text),
    ]

    return "\n\n".join(section for section in sections if section)
