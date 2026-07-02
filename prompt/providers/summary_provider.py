from prompt.formatter import format_section


def build(summary_text: str = "") -> str:
    return format_section("これまでの会話要約", summary_text)
