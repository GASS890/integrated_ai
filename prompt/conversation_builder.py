from prompt.prompt_router import PromptBundle


def normalize_history(history: list | None = None) -> list[dict]:
    normalized = []

    for message in history or []:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = str(message.get("content") or "").strip()

        if role not in ("user", "assistant"):
            continue

        if not content:
            continue

        normalized.append({
            "role": role,
            "content": content,
        })

    return normalized


def build_conversation_messages(
    user_text: str,
    history: list | None,
    bundle: PromptBundle,
) -> list[dict]:
    messages = []

    if bundle.final_system_context:
        messages.append({
            "role": "system",
            "content": bundle.final_system_context,
        })

    messages.extend(normalize_history(history))

    messages.append({
        "role": "user",
        "content": str(user_text or "").strip(),
    })

    return messages
