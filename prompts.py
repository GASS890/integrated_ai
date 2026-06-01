# prompts.py

SAFETY_SYSTEM = """\
【安全と禁止（固定）】
- 危険行為や不正行為を助長しない
- 根拠のない断言をしない（不確実なら不確実と示す）
- 個人情報・機密情報の取り扱いに注意する
"""

def build_messages(
    user_text: str,
    history: list,
    memories_text: str = "",
    summary_text: str = "",
    personality_text: str = "",
    rules_text: str = "",
):
    messages = []

    system_parts = []

    if rules_text:
        system_parts.append(rules_text)

    if personality_text:
        system_parts.append(personality_text)

    if memories_text:
        system_parts.append(memories_text)

    if summary_text:
        system_parts.append("【これまでの会話要約】\n" + summary_text)

    if system_parts:
        messages.append({
            "role": "system",
            "content": "\n\n".join(system_parts),
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