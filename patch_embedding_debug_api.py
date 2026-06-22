from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

# import追加
old_import = "from memory.memory_reflection import reflect_conversation_to_memory\n"
new_import = old_import + "from memory.embedding_store import load_embedding_memories, add_embedding_memory\n"

if "from memory.embedding_store import load_embedding_memories, add_embedding_memory" not in text:
    text = text.replace(old_import, new_import)

# Request model追加
old_model = '''class MemorySaveRequest(BaseModel):
    text: str
'''

new_model = '''class MemorySaveRequest(BaseModel):
    text: str


class EmbeddingMemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5
'''

if "class EmbeddingMemorySearchRequest" not in text:
    text = text.replace(old_model, new_model)

# API追加
insert_before = '''@app.get("/", response_class=HTMLResponse)
def read_root():
'''

api_code = '''@app.get("/memory/embedding")
def get_embedding_memories():
    items = load_embedding_memories()
    return {
        "count": len(items),
        "items": [
            {
                "id": item.get("id"),
                "text": item.get("text"),
                "embedding_backend": item.get("embedding_backend"),
                "embedding_dim": len(item.get("embedding", [])),
                "importance": item.get("importance"),
                "access_count": item.get("access_count"),
                "meta": item.get("meta", {}),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
            }
            for item in items[-100:]
        ]
    }


@app.post("/memory/embedding/search")
def search_embedding_memories(req: EmbeddingMemorySearchRequest):
    results = search_similar_memories(
        req.query,
        top_k=req.top_k,
        min_score=0.0,
        backend="ollama",
    )
    return {
        "query": req.query,
        "count": len(results),
        "results": results,
    }


@app.post("/memory/embedding/save")
def save_embedding_memory_debug(req: MemorySaveRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is empty")

    item = add_embedding_memory(
        text,
        {
            "importance": 0.7,
            "category": "debug",
            "embedding_backend": "ollama",
            "source": "debug_api",
        }
    )

    return {
        "status": "ok",
        "id": item.get("id"),
        "embedding_backend": item.get("embedding_backend"),
        "embedding_dim": len(item.get("embedding", [])),
    }


'''

if '@app.get("/memory/embedding")' not in text:
    text = text.replace(insert_before, api_code + insert_before)

path.write_text(text, encoding="utf-8")
print("embedding debug api patch applied.")
