from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

bad = '''class MemorySaveRequest(BaseModel):
    text: str


class EmbeddingMemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5
    kind: str | None = None
'''

good = '''class MemorySaveRequest(BaseModel):
    text: str
    kind: str | None = None


class EmbeddingMemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5
'''

text = text.replace(bad, good)

path.write_text(text, encoding="utf-8")
print("MemorySaveRequest kind fixed.")
