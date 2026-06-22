from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

# 1. import追加
old_import = "from personality.state_schema import normalize_sessions_personality\n"
new_import = old_import + "from memory.vector_search import search_similar_memories\nfrom memory.memory_reflection import reflect_conversation_to_memory\n"

if "from memory.vector_search import search_similar_memories" not in text:
    text = text.replace(old_import, new_import)

# 2. Embedding記憶プロンプト helper 追加
old_helper = '''def build_long_term_memory_prompt(user_text: str, model: str = FAST_MODEL) -> str:
    limit = SMART_MEMORY_LIMIT if model == SMART_MODEL else FAST_MEMORY_LIMIT
    return build_topic_memory_prompt(memory_db, user_text, limit=limit)
'''

new_helper = '''def build_long_term_memory_prompt(user_text: str, model: str = FAST_MODEL) -> str:
    limit = SMART_MEMORY_LIMIT if model == SMART_MODEL else FAST_MEMORY_LIMIT
    return build_topic_memory_prompt(memory_db, user_text, limit=limit)


def build_embedding_memory_prompt(user_text: str) -> str:
    try:
        results = search_similar_memories(
            user_text,
            top_k=5,
            min_score=0.35,
            backend="ollama",
        )
    except Exception as e:
        print("embedding memory search error:", e)
        return ""

    if not results:
        return ""

    lines = ["【Embedding長期記憶】"]
    for item in results:
        text = (item.get("text") or "").strip()
        if text:
            lines.append(f"- {text}")

    return "\\n".join(lines)
'''

if "def build_embedding_memory_prompt" not in text:
    text = text.replace(old_helper, new_helper)

# 3. ask() 内の memories_text 生成を差し替え
old_mem = '''        memories_text = build_long_term_memory_prompt(q, model=model)
        messages = build_messages(
'''

new_mem = '''        memory_db_text = build_long_term_memory_prompt(q, model=model)
        embedding_text = build_embedding_memory_prompt(q)

        memories_text = "\\n\\n".join(
            part for part in [memory_db_text, embedding_text]
            if part and part.strip()
        )

        messages = build_messages(
'''

if "embedding_text = build_embedding_memory_prompt(q)" not in text:
    text = text.replace(old_mem, new_mem)

# 4. finalize_interaction() 内の保存処理にEmbedding反映を追加
old_finalize = '''    maybe_store_long_term_memory(user_text, intent=intent)

    seed = (session.get("summary") or "").strip() or user_text
'''

new_finalize = '''    maybe_store_long_term_memory(user_text, intent=intent)

    try:
        reflect_conversation_to_memory(user_text, assistant_text)
    except Exception as e:
        print("embedding memory reflection error:", e)

    seed = (session.get("summary") or "").strip() or user_text
'''

if "reflect_conversation_to_memory(user_text, assistant_text)" not in text:
    text = text.replace(old_finalize, new_finalize)

path.write_text(text, encoding="utf-8")
print("main.py embedding memory patch applied.")
