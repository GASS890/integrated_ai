# prompts.py

SAFETY_SYSTEM = """\
【安全と禁止（固定）】
- 危険行為や不正行為を助長しない
- 根拠のない断言をしない（不確実なら不確実と示す）
- 個人情報・機密情報の取り扱いに注意する
"""


def build_prompt_context(
    rules_text: str = "",
    personality_text: str = "",
    memories_text: str = "",
    summary_text: str = "",
) -> str:
    sections = []

    sections.append(SAFETY_SYSTEM)

    if rules_text:
        sections.append("【ルール】\n" + rules_text)

    if personality_text:
        sections.append("【人格】\n" + personality_text)

    if memories_text:
        sections.append("【記憶】\n" + memories_text)

    if summary_text:
        sections.append("【これまでの会話要約】\n" + summary_text)

    return "\n\n".join(sections)


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
