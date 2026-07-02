from prompt.context_builder import build_prompt_context


def build_messages(
    user_text: str,
    history: list,
    memories_text: str = "",
    summary_text: str = "",
    personality_text: str = "",
    rules_text: str = "",
):
    messages = []

    system_context = build_prompt_context(
        rules_text=rules_text,
        personality_text=personality_text,
        memories_text=memories_text,
        summary_text=summary_text,
    )

    if system_context:
        messages.append({
            "role": "system",
            "content": system_context,
        })

    for m in history or []:
        role = m.get("role")
        content = m.get("content")

        if role in ("user", "assistant") and content:
            messages.append({
                "role": role,
                "content": content,
            })

    messages.append({
        "role": "user",
        "content": user_text,
    })

    return messages
