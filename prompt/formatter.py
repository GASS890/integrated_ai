def format_section(title: str, content: str) -> str:
    if not content:
        return ""

    return f"【{title}】\n{content}"
