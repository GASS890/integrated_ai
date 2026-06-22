import math
from memory.embedding_store import build_embedding, load_embedding_memories, update_memory_access


def cosine_similarity(a, b):
    if not a or not b:
        return 0.0

    length = min(len(a), len(b))
    if length == 0:
        return 0.0

    a = a[:length]
    b = b[:length]

    return sum(x * y for x, y in zip(a, b)) / (
        (math.sqrt(sum(x * x for x in a)) or 1.0) *
        (math.sqrt(sum(y * y for y in b)) or 1.0)
    )


def search_similar_memories(query: str, top_k: int = 5, min_score: float = 0.25, backend: str = "ollama"):
    q_vec = build_embedding(query, backend=backend)
    results = []

    for item in load_embedding_memories():
        score = cosine_similarity(q_vec, item.get("embedding", []))
        if score >= min_score:
            results.append({
                "id": item.get("id"),
                "text": item.get("text", ""),
                "score": score,
                "importance": item.get("importance", 0.5),
                "access_count": item.get("access_count", 0),
                "embedding_backend": item.get("embedding_backend", "unknown"),
                "meta": item.get("meta", {}),
            })

    results.sort(
        key=lambda x: (
            x["score"] * 0.7 +
            float(x.get("importance", 0.5)) * 0.2 +
            min(int(x.get("access_count", 0)), 10) * 0.01
        ),
        reverse=True
    )

    selected = results[:top_k]
    for item in selected:
        if item.get("id"):
            update_memory_access(item["id"])

    return selected
