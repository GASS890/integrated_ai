from prompt.formatter import format_section


def build(personality_text: str = "") -> str:
    return format_section("人格", personality_text)
