from prompt.formatter import format_section


def build(memories_text: str = "") -> str:
    return format_section("記憶", memories_text)
