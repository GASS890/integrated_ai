# memory_store.py
import json
import os
import re
import time
import uuid


MEMORY_FILE = "memories.json"

EXPLICIT_MEMORY_MARKERS = [
    "覚えて",
    "記憶して",
    "今後は",
    "今後も",
    "以後は",
    "以後も",
    "固定",
    "この設定",
    "この口調",
    "この呼び方",
]

SETTING_HINTS = [
    "口調",
    "性格",
    "呼び方",
    "設定",
    "ルール",
    "禁止",
    "優先",
    "好み",
    "苦手",
]

PERSONAL_HINTS = [
    "私は",
    "僕は",
    "わたしは",
    "自分は",
    "好き",
    "苦手",
    "嫌い",
    "好み",
]


def _default_db() -> dict:
    return {"memories": []}


def load_memory_db(path: str = MEMORY_FILE) -> dict:
    if not os.path.exists(path):
        return _default_db()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("memories"), list):
            return data
    except Exception:
        pass

    return _default_db()


def save_memory_db(db: dict, path: str = MEMORY_FILE):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _normalize_text(text: str) -> str:
    t = (text or "").strip()
    t = t.replace("\r", " ").replace("\n", " ")
    t = " ".join(t.split())
    return t


def _infer_kind(text: str) -> str:
    t = text or ""

    if any(x in t for x in ["口調", "性格", "呼び方", "設定", "ルール", "禁止"]):
        return "setting"
    if any(x in t for x in ["好き", "苦手", "嫌い", "好み", "優先"]):
        return "preference"
    return "fact"


def should_auto_store_memory(user_text: str) -> bool:
    t = _normalize_text(user_text)
    if not t:
        return False

    if any(x in t for x in EXPLICIT_MEMORY_MARKERS):
        return True

    has_setting = any(x in t for x in SETTING_HINTS)
    has_personal = any(x in t for x in PERSONAL_HINTS)

    if has_setting and ("今後" in t or "以後" in t or "固定" in t):
        return True

    if has_personal and ("今後" in t or "覚えて" in t):
        return True

    return False


def extract_memory_text(user_text: str) -> str:
    t = _normalize_text(user_text)

    replacements = [
        "覚えておいて",
        "覚えて",
        "記憶しておいて",
        "記憶して",
        "今後は",
        "今後も",
        "以後は",
        "以後も",
    ]
    for x in replacements:
        t = t.replace(x, "")

    t = t.strip(" 。、")
    return t


def upsert_memory(db: dict, text: str, kind: str | None = None) -> dict | None:
    clean = _normalize_text(text)
    if not clean:
        return None

    memories = db.setdefault("memories", [])
    inferred_kind = kind or _infer_kind(clean)
    now = time.time()

    for item in memories:
        if (
            isinstance(item, dict)
            and item.get("text") == clean
            and item.get("kind") == inferred_kind
        ):
            item["updated_at"] = now
            item["hits"] = int(item.get("hits", 0)) + 1
            return item

    new_item = {
        "id": str(uuid.uuid4()),
        "text": clean,
        "kind": inferred_kind,
        "created_at": now,
        "updated_at": now,
        "hits": 1,
    }
    memories.append(new_item)
    return new_item


def auto_store_user_memory(db: dict, user_text: str) -> dict | None:
    if not should_auto_store_memory(user_text):
        return None

    text = extract_memory_text(user_text)
    if not text:
        return None

    return upsert_memory(db, text)


def delete_memory(db: dict, memory_id: str) -> bool:
    memories = db.setdefault("memories", [])
    before = len(memories)
    db["memories"] = [m for m in memories if m.get("id") != memory_id]
    return len(db["memories"]) != before


def _extract_keywords(text: str) -> set[str]:
    t = _normalize_text(text)
    if not t:
        return set()

    # 英数字語 + 日本語2文字以上
    words = re.findall(r"[A-Za-z0-9_]{2,}|[一-龥ぁ-んァ-ヶー]{2,}", t)
    return {w for w in words if len(w) >= 2}


def _score_memory(memory: dict, query: str) -> int:
    text = memory.get("text") or ""
    if not text:
        return 0

    query_keys = _extract_keywords(query)
    memory_keys = _extract_keywords(text)

    overlap = len(query_keys & memory_keys)
    score = overlap * 10

    # 明示設定は少し優先
    if memory.get("kind") == "setting":
        score += 3

    # 最近更新された記憶を少し優先
    updated_at = float(memory.get("updated_at", 0) or 0)
    age_bonus = int(updated_at // 86400)
    score += age_bonus % 3

    return score


def find_relevant_memories(db: dict, query: str, limit: int = 5) -> list[dict]:
    memories = db.get("memories", [])
    if not memories:
        return []

    scored = []
    for m in memories:
        if not isinstance(m, dict):
            continue
        s = _score_memory(m, query)
        if s > 0:
            scored.append((s, float(m.get("updated_at", 0) or 0), m))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    result = [x[2] for x in scored[:limit]]

    # 関連が1件もない場合、setting を最大2件だけ常時注入
    if not result:
        settings = [
            m for m in memories
            if isinstance(m, dict) and m.get("kind") == "setting"
        ]
        settings.sort(key=lambda x: float(x.get("updated_at", 0) or 0), reverse=True)
        result = settings[:2]

    return result


def _build_topic_profile(db: dict, query: str) -> dict:
    memories = db.get("memories", [])
    if not memories:
        return {
            "affinity_bias": 0,
            "caution_bias": 0,
            "matched": 0,
        }

    # 速度対策：記憶が増えすぎた場合は新しいものから最大100件だけ見る
    memories = sorted(
        [m for m in memories if isinstance(m, dict)],
        key=lambda x: float(x.get("updated_at", 0) or 0),
        reverse=True
    )[:100]

    qkeys = _extract_keywords(query)
    affinity_bias = 0
    caution_bias = 0
    matched = 0

    for m in memories:
        if not isinstance(m, dict):
            continue

        text = m.get("text") or ""
        if not text:
            continue

        mkeys = _extract_keywords(text)
        overlap = len(qkeys & mkeys)
        if overlap <= 0:
            continue

        matched += 1

        kind = m.get("kind") or "fact"
        hits = int(m.get("hits", 1) or 1)

        if kind == "setting":
            affinity_bias += 2 + min(4, hits // 2)
        elif kind == "preference":
            affinity_bias += 2 + min(3, hits // 3)
        else:
            caution_bias += 1 + min(3, hits // 4)

    return {
        "affinity_bias": affinity_bias,
        "caution_bias": caution_bias,
        "matched": matched,
    }


def build_topic_memory_prompt(db: dict, query: str, limit: int = 5) -> str:
    relevant = find_relevant_memories(db, query, limit=limit)
    profile = _build_topic_profile(db, query)

    lines = []

    if relevant:
        lines.append("以下は長期記憶です。必要な場合のみ参照してください。")
        for m in relevant:
            kind = m.get("kind") or "fact"
            text = m.get("text") or ""
            lines.append(f"- [{kind}] {text}")

    if profile["matched"] > 0:
        lines.append("")
        lines.append("【話題ごとの人格反応】")
        lines.append("- 関連する記憶がある話題では、過去のやり取りを踏まえた反応にする。")
        lines.append("- ユーザーの好み・継続的な関心がある話題では、少し親しみを強める。")
        lines.append("- 事実系の記憶が多い話題では、断定しすぎず慎重に答える。")
        lines.append(f"- 親和度補正: {profile['affinity_bias']}")
        lines.append(f"- 慎重さ補正: {profile['caution_bias']}")
        lines.append(f"- 関連記憶数: {profile['matched']}")

    return "\n".join(lines)

def list_memories(db: dict, limit: int = 100) -> list[dict]:
    memories = db.get("memories", [])
    items = [m for m in memories if isinstance(m, dict)]
    items.sort(key=lambda x: float(x.get("updated_at", 0) or 0), reverse=True)
    return items[:limit]