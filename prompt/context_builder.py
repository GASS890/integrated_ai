from prompt.sections import SAFETY_SYSTEM
from prompt.formatter import format_section


def build_prompt_context(
    rules_text: str = "",
    personality_text: str = "",
    memories_text: str = "",
    summary_text: str = "",
) -> str:
    sections = []

    sections.append(SAFETY_SYSTEM)

    if rules_text:
        sections.append(format_section("ルール", rules_text))

    if personality_text:
        sections.append(format_section("人格", personality_text))

    if memories_text:
        sections.append(format_section("記憶", memories_text))

    if summary_text:
        sections.append(format_section("これまでの会話要約", summary_text))

    return "\n\n".join(section for section in sections if section)
