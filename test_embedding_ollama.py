from memory.embedding_store import add_embedding_memory
from memory.vector_search import search_similar_memories

item = add_embedding_memory(
    "ユーザーはローカルAI integrated_ai の長期記憶をOllama Embeddingで高精度化したい",
    {
        "importance": 0.9,
        "category": "好み",
        "embedding_backend": "ollama"
    }
)

print("追加された記憶:")
print(item["id"])
print("embedding次元数:", len(item["embedding"]))
print("backend:", item.get("embedding_backend"))

print("\n検索結果:")
print(search_similar_memories(
    "integrated_ai の長期記憶を高精度化したい",
    top_k=3,
    backend="ollama"
))
