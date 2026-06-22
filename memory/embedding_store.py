import json
import math
import os
import hashlib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE_PATH = os.path.join(BASE_DIR, "memory", "embedding_memories.json")


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _tokenize(text: str):
    return [c for c in text.lower().strip() if not c.isspace()]


def simple_embedding(text: str):
    vec = [0.0] * 128
    for token in _tokenize(text):
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        vec[h % 128] += 1.0

    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def build_embedding(text: str, backend: str = "ollama"):
    try:
        from memory.embedding_provider import get_embedding
        return get_embedding(text, backend=backend)
    except Exception:
        return simple_embedding(text)


def load_embedding_memories():
    if not os.path.exists(STORE_PATH):
        return []
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_embedding_memories(items):
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def add_embedding_memory(text: str, meta: dict | None = None):
    text = (text or "").strip()
    if not text:
        return None

    meta = meta or {}
    backend = meta.get("embedding_backend", "ollama")

    items = load_embedding_memories()
    item = {
        "id": hashlib.sha1((text + _now()).encode("utf-8")).hexdigest()[:16],
        "text": text,
        "embedding": build_embedding(text, backend=backend),
        "embedding_backend": backend,
        "meta": meta,
        "created_at": _now(),
        "updated_at": _now(),
        "importance": float(meta.get("importance", 0.5)),
        "access_count": 0,
    }
    items.append(item)
    save_embedding_memories(items)
    return item


def update_memory_access(memory_id: str):
    items = load_embedding_memories()
    for item in items:
        if item.get("id") == memory_id:
            item["access_count"] = int(item.get("access_count", 0)) + 1
            item["updated_at"] = _now()
            break
    save_embedding_memories(items)
