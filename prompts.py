# prompts.py

SAFETY_SYSTEM = """\
【安全と禁止（固定）】
- 危険行為や不正行為を助長しない
- 根拠のない断言をしない（不確実なら不確実と示す）
- 個人情報・機密情報の取り扱いに注意する
"""

def build_messages(
    user_text,
    history,
    memories_text="",
    summary_text="",
    personality_text="",
):
    messages = []

    system_parts = []

    if system_text:
        system_parts.append(system_text)

    if personality_text:
        system_parts.append(personality_text)

    if memories_text:
        system_parts.append(memories_text)

    if summary_text:
        system_parts.append(summary_text)

    messages.append({
        "role": "system",
        "content": "\n\n".join(system_parts),
    })

    return messages