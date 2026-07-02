from prompt.formatter import format_section


def build(rules_text: str = "") -> str:
    return format_section("ルール", rules_text)
