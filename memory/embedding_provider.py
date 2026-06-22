import json
import urllib.request
import urllib.error

from memory.embedding_store import simple_embedding


OLLAMA_EMBED_MODEL = "nomic-embed-text"
OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embed"


def get_embedding(text: str, backend: str = "ollama"):
    text = (text or "").strip()

    if not text:
        return simple_embedding("")

    if backend == "ollama":
        vec = _ollama_embedding(text)
        if vec:
            return vec

    return simple_embedding(text)


def _ollama_embedding(text: str):
    payload = {
        "model": OLLAMA_EMBED_MODEL,
        "input": text
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_EMBED_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            body = json.loads(res.read().decode("utf-8"))
            embeddings = body.get("embeddings")
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            return None
    except urllib.error.URLError:
        return None
    except Exception:
        return None
