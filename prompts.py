# prompts.py

SAFETY_SYSTEM = """\
【安全と禁止（固定）】
- 危険行為や不正行為を助長しない
- 根拠のない断言をしない（不確実なら不確実と示す）
- 個人情報・機密情報の取り扱いに注意する
"""

def build_messages(
    session: dict,
    user_text: str,
    rules_text: str = "",
    memories_text: str = "",
) -> list:
    """
    system 構成:
    - SAFETY_SYSTEM
    - rules_text
    - memories_text（長期記憶）
    - summary（短期要約）
    - recent messages
    - current user
    """
    rules = (rules_text or "").strip()
    memories = (memories_text or "").strip()

    system_blocks = []
    if SAFETY_SYSTEM.strip():
        system_blocks.append(SAFETY_SYSTEM.strip())
    if rules:
        system_blocks.append(rules)

    system_content = "\n\n".join(system_blocks).strip()
    messages = [{"role": "system", "content": system_content}] if system_content else []

    if memories:
        messages.append({
            "role": "system",
            "content": memories
        })

    summary = session.get("summary", "")
    if isinstance(summary, str) and summary.strip():
        messages.append({
            "role": "system",
            "content": "以下はこれまでの会話の要約です。\n" + summary.strip()
        })

    for m in session.get("messages", []):
        role = m.get("role")
        content = m.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content})

    if isinstance(user_text, str) and user_text.strip():
        messages.append({"role": "user", "content": user_text.strip()})

    return messages