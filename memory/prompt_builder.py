def _section(title: str, content: str) -> str:
    content = str(content or "").strip()

    if not content:
        return ""

    return f"【{title}】\n{content}"


def build_memory_prompt(
    memories_text: str = "",
    summary_text: str = "",
    learning_text: str = "",
    preferences_text: str = "",
) -> str:
    sections = [
        _section("長期記憶", memories_text),
        _section("これまでの会話要約", summary_text),
        _section("学習結果", learning_text),
        _section("ユーザーの好み", preferences_text),
    ]

    sections = [
        section
        for section in sections
        if section
    ]

    if not sections:
        return ""

    header = (
        "以下は会話を補助する記憶情報です。\n"
        "現在の質問に関係する情報だけを使用し、"
        "記憶にない内容を作り出さないでください。"
    )

    return header + "\n\n" + "\n\n".join(sections)
