from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from prompts import build_messages
from personality.state_manager import _ensure_personality
from personality.attitude_analysis import analyze_attitude
from personality.affinity import update_affinity
from personality.mood import update_mood
from personality.personality_prompt import build_personality_text

import json
import traceback
import glob
import re
from collections import defaultdict
from threading import Lock, Thread

import os
import sys
import time
import uuid

from llm_client import call_ollama_chat, stream_ollama_chat, OPTIONS
from voicevox_client import synthesize_voice
from io import BytesIO
from file_ops import write_file, append_file, read_file, read_line, delete_line
from memory_store import (
    load_memory_db,
    save_memory_db,
    auto_store_user_memory,
    build_topic_memory_prompt,
    list_memories,
    upsert_memory,
    delete_memory,
)

from personality.state_manager import _ensure_personality
from personality.affinity import update_personality
from personality.personality_prompt import build_personality_prompt
from personality.attitude_analysis import (
    analyze_user_intent_llm,
    schedule_personality_analysis,
)

# ===== FastAPI App =====
app = FastAPI()
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


STATIC_DIR = resource_path("static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ===== Files =====
SESSIONS_FILE = "sessions.json"
FEEDBACK_FILE = "feedback.jsonl"
MEMORY_FILE = "memories.json"

DEBUG = False

# ===== Model Routing =====
FAST_MODEL = "gemma2:2b"
SMART_MODEL = "qwen2.5:14b"

# ===== Answer Formatting =====
FORMAT_MODEL = "gemma2:2b"

# ===== Summarize / Title =====
SUMMARIZE_MODEL = "gemma2:2b"
TITLE_MODEL = "gemma2:2b"

DETAIL_REQUEST_WORDS = [
    "詳しく", "詳細", "もっと", "もう少し", "具体的に", "例", "サンプル",
    "手順", "ステップ", "根拠", "理由", "続き", "掘り下げ", "深掘り",
    "比較", "違い", "メリット", "デメリット", "代替案", "他の方法",
]

HEAVY_WORDS = [
    "原因", "修正", "最適化", "設計", "改善", "仕様", "バグ", "エラー",
    "パフォーマンス", "速度", "例外", "ログ", "スタックトレース", "差分", "diff",
]

CODE_MARKERS = [
    "```", "Traceback", "Exception", "Error",
    ".py", ".js", ".html", ".css",
    "function", "class ", "import ", "def ", "{", "}", "=>",
]

# ===== コンテキスト肥大対策 =====
MAX_STORED_MSG_CHARS = 1000
MAX_SUMMARY_CHARS = 900
KEEP_LAST = 6
SUMMARIZE_TRIGGER_MSGS = 18

FAST_MEMORY_LIMIT = 3
SMART_MEMORY_LIMIT = 5

# =========================================================
# txt読み込み
# =========================================================
def load_text_file(path: str, default: str = "") -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"{path} 読み込み失敗:", e)
        return default


def load_rules_dir(dir_path: str = "rules") -> str:
    parts = []
    for path in sorted(glob.glob(f"{dir_path}/*.txt")):
        try:
            with open(path, encoding="utf-8") as f:
                parts.append(f"\n\n# file: {path}\n" + f.read())
        except Exception:
            continue
    return "\n".join(parts).strip()


RULES = load_rules_dir(resource_path("rules"))
STYLE = load_text_file(resource_path("style.txt"), default="")

FORMAT_SYSTEM = load_text_file(resource_path("prompts/format_system.txt"), default="")
TITLE_SYSTEM = load_text_file(resource_path("prompts/title_system.txt"), default="")
SUMMARIZE_SYSTEM = load_text_file(resource_path("prompts/summarize_system.txt"), default="")
GOOD_EXAMPLES_SYSTEM = load_text_file(resource_path("prompts/good_examples_system.txt"), default="")

# =========================================================
# ルータ / 整形 / 要約
# =========================================================
def _contains_any(text: str, words: list[str]) -> bool:
    t = text or ""
    return any(w in t for w in words)


def _is_detail_request(user_text: str, session: dict | None) -> bool:
    t = (user_text or "").strip()
    if not t:
        return False
    if _contains_any(t, DETAIL_REQUEST_WORDS):
        return True
    if len(t) <= 20 and session and (session.get("messages") or []):
        triggers = ["それ", "上の", "この", "さっき", "前の", "続き", "もう一度"]
        if any(x in t for x in triggers):
            return True
    return False


def _history_heavy_score(session: dict | None, lookback: int = 10) -> int:
    if not session:
        return 0
    msgs = session.get("messages") or []
    recent = msgs[-lookback:] if len(msgs) > lookback else msgs

    score = 0
    for m in recent:
        c = m.get("content") or ""
        if not isinstance(c, str) or not c:
            continue
        if _contains_any(c, CODE_MARKERS):
            score += 2
        if _contains_any(c, HEAVY_WORDS):
            score += 1
        if len(c) >= 400:
            score += 1
    return score


def _quick_code_signal(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    strong = ["```", "Traceback", "Exception", "Error", "import ", "def ", "class "]
    if any(s in t for s in strong):
        return True
    if any(x in t for x in [".py", ".js", ".html", ".css", "diff", "スタックトレース", "ログ"]):
        return True
    return False


def choose_model(user_text: str, session: dict | None = None, intent: dict | None = None) -> str:
    session = session or {}
    t = (user_text or "").strip()
    if not t:
        return FAST_MODEL

    if isinstance(intent, dict) and intent.get("model_need") == "smart":
        return SMART_MODEL

    if _is_detail_request(t, session):
        return SMART_MODEL
    if _quick_code_signal(t):
        return SMART_MODEL

    heavy_hits = sum(1 for w in HEAVY_WORDS if w in t)
    if heavy_hits >= 2:
        return SMART_MODEL

    if len(t) >= 350:
        return SMART_MODEL

    summary = session.get("summary") or ""
    if isinstance(summary, str) and summary:
        if len(summary) > 800:
            return SMART_MODEL
        if _quick_code_signal(summary):
            return SMART_MODEL
        if sum(1 for w in HEAVY_WORDS if w in summary) >= 3:
            return SMART_MODEL

    if _history_heavy_score(session, lookback=8) >= 5:
        return SMART_MODEL

    return FAST_MODEL


def should_format(user_text: str, answer_text: str) -> bool:
    u = (user_text or "")
    a = (answer_text or "")
    if len(a) >= 600:
        return True
    keywords = ["添削", "修正", "改善", "差分", "変更前", "変更後", "コード", "バグ", "エラー"]
    return any(k in u for k in keywords)


def _count_code_fences(text: str) -> int:
    return (text or "").count("```")


def _looks_like_hallucinated_format(raw: str, formatted: str) -> bool:
    if not formatted:
        return True
    if _count_code_fences(formatted) > _count_code_fences(raw):
        return True
    if len(formatted) > max(2000, len(raw) * 2):
        return True
    return False


def format_answer(user_text: str, raw_answer: str) -> str:
    if not should_format(user_text, raw_answer):
        return raw_answer

    prompt = [
        {"role": "system", "content": FORMAT_SYSTEM or ""},
        {"role": "user", "content": f"【ユーザーの要求】\n{user_text}\n\n【元の回答】\n{raw_answer}\n"},
    ]
    try:
        formatted = call_ollama_chat(prompt, FORMAT_MODEL, options=OPTIONS["format"])
        if _looks_like_hallucinated_format(raw_answer, formatted):
            return raw_answer
        return formatted
    except Exception as e:
        print("format_answer error:", e)
        return raw_answer


def _sanitize_title(title: str, max_len: int = 15) -> str:
    t = title or ""
    t = t.replace("\n", " ").replace("\r", " ")
    t = " ".join(t.split())
    t = t.replace("。", "").replace("、", "")
    return t[:max_len].strip()


def generate_title(text: str) -> str:
    if not text or not text.strip():
        return ""

    prompt = [
        {"role": "system", "content": TITLE_SYSTEM or ""},
        {"role": "user", "content": text},
    ]

    try:
        title = call_ollama_chat(prompt, TITLE_MODEL, options=OPTIONS["title"]) or ""
        return _sanitize_title(title, max_len=15)
    except Exception as e:
        print("generate_title error:", e)
        return ""


def _shrink_text_for_storage(text: str, max_chars: int) -> str:
    t = text or ""
    if len(t) <= max_chars:
        return t
    head = t[: max_chars // 2]
    tail = t[- max_chars // 2 :]
    return head + "\n...\n(長文省略)\n...\n" + tail


def _append_session_message(session: dict, role: str, content: str):
    if not isinstance(content, str):
        return
    c = content.strip()
    if not c:
        return
    c = _shrink_text_for_storage(c, MAX_STORED_MSG_CHARS)
    session["messages"].append({"role": role, "content": c})


def summarize_session(session: dict):
    messages_text = "\n".join(
        f"{m.get('role','')}: {m.get('content','')}"
        for m in session.get("messages", [])
    )

    summary_prompt = [
        {"role": "system", "content": SUMMARIZE_SYSTEM or ""},
        {
            "role": "user",
            "content": (
                "【これまでの要約】\n"
                + (session.get("summary", "") or "")
                + "\n\n【新しい会話】\n"
                + messages_text
            )
        }
    ]

    try:
        new_summary = call_ollama_chat(summary_prompt, SUMMARIZE_MODEL, options=OPTIONS["summarize"]) or ""
        session["summary"] = new_summary
    except Exception as e:
        print("summarize_session error:", e)

    try:
        s = session.get("summary") or ""
        if isinstance(s, str) and len(s) > MAX_SUMMARY_CHARS:
            shrink_prompt = [
                {"role": "system", "content": SUMMARIZE_SYSTEM or ""},
                {"role": "user", "content": f"【目的】以下の要約を短く圧縮してください。\n最大{MAX_SUMMARY_CHARS}文字程度。\n\n【要約】\n{s}"},
            ]
            session["summary"] = call_ollama_chat(shrink_prompt, SUMMARIZE_MODEL, options=OPTIONS["summarize"]) or s
    except Exception as e:
        print("summary shrink error:", e)

    session["messages"] = session.get("messages", [])[-KEEP_LAST:]


def _ensure_title_once(session: dict, seed_text: str):
    if session.get("title_fixed") is True:
        return

    title = (session.get("title") or "").strip()
    if title and title != "新しいチャット":
        session["title"] = _sanitize_title(title, 15) or "新しいチャット"
        session["title_fixed"] = True
        return

    gen = generate_title(seed_text)
    if gen:
        session["title"] = gen
        session["title_fixed"] = True
        return

    fallback = _sanitize_title(seed_text, 15) or "新しいチャット"
    session["title"] = fallback
    session["title_fixed"] = True


# =========================================================
# ファイル操作
# =========================================================
def try_file_operation(user_text: str):
    text = (user_text or "").strip()

    try:
        # ===== 明示コマンド =====
        if text.startswith("保存:"):
            _, rest = text.split("保存:", 1)
            filename, content = rest.strip().split(" ", 1)
            return write_file(filename.strip(), content.strip())

        if text.startswith("追記:"):
            _, rest = text.split("追記:", 1)
            filename, content = rest.strip().split(" ", 1)
            return append_file(filename.strip(), content.strip())

        if text.startswith("読込:"):
            _, filename = text.split("読込:", 1)
            return read_file(filename.strip())

        if text.startswith("行読込:"):
            _, rest = text.split("行読込:", 1)
            filename, line_no = rest.strip().split(" ", 1)
            return read_line(filename.strip(), int(line_no.strip()))

        if text.startswith("削除:"):
            _, rest = text.split("削除:", 1)
            filename, line_no = rest.strip().split(" ", 1)
            return delete_line(filename.strip(), int(line_no.strip()))

        # ===== 自然文解析 =====
        file_match = re.search(r'([^\s]+\.txt)', text)
        line_match = re.search(r'(\d+)\s*行(?:目)?', text)

        filename = file_match.group(1) if file_match else None
        line_no = int(line_match.group(1)) if line_match else None

        # ===== 行削除 =====
        if ("削除" in text or "消して" in text):
            if filename and line_no is not None:
                return delete_line(filename, line_no)

        # ===== 行読込 / 全読込 =====
        if ("読んで" in text or "見せて" in text or "表示" in text or "開いて" in text):
            if filename and line_no is not None:
                return read_line(filename, line_no)
            if filename:
                return read_file(filename)

        # ===== 追記 =====
        if ("追加" in text or "追記" in text or "書いて" in text):
            if filename:
                content = text
                content = re.sub(r'[^\s]+\.txt', '', content)
                content = re.sub(r'(追加|追記|書いて)', '', content)
                content = re.sub(r'(に|へ|を)', '', content)
                content = content.strip()
                if content:
                    return append_file(filename, content)

        # ===== 保存 =====
        if "保存" in text:
            if filename:
                content = text
                content = re.sub(r'[^\s]+\.txt', '', content)
                content = re.sub(r'保存', '', content)
                content = re.sub(r'(に|へ|を)', '', content)
                content = content.strip()
                if content:
                    return write_file(filename, content)

    except ValueError as e:
        return str(e)
    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return str(e)

    return None


# =========================================================
# sessions 永続化
# =========================================================
def _new_session():
    return {
        "title": "",
        "title_fixed": False,
        "summary": "",
        "messages": [],
        "created_at": time.time(),
        "personality": _init_personality(),
    }


def load_sessions_from_file() -> dict:
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print("sessions.json 読み込み失敗:", e)
        return {}


def save_sessions_to_file(sessions_dict: dict):
    tmp = SESSIONS_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(sessions_dict, f, ensure_ascii=False, indent=2)
        os.replace(tmp, SESSIONS_FILE)
    except Exception as e:
        print("sessions.json 保存失敗:", e)


sessions_lock = Lock()
memories_lock = Lock()


def persist_sessions():
    with sessions_lock:
        save_sessions_to_file(dict(sessions))


def persist_memories():
    with memories_lock:
        save_memory_db(memory_db, MEMORY_FILE)


_loaded = load_sessions_from_file()

_now = time.time()
for sid, s in _loaded.items():
    if isinstance(s, dict) and "created_at" not in s:
        s["created_at"] = _now
    if isinstance(s, dict) and "title_fixed" not in s:
        s["title_fixed"] = False
    if isinstance(s, dict):
        _ensure_personality(s)

sessions = defaultdict(_new_session, _loaded)
memory_db = load_memory_db(MEMORY_FILE)


# =========================================================
# Request Body
# =========================================================
class AskRequest(BaseModel):
    q: str
    session_id: str


class ResetRequest(BaseModel):
    session_id: str


class DeleteSessionRequest(BaseModel):
    session_id: str


class FeedbackRequest(BaseModel):
    session_id: str
    user_text: str
    assistant_text: str
    rating: str
    model: str | None = None
    reason: str | None = None


class MemorySaveRequest(BaseModel):
    text: str
    kind: str | None = None


class MemoryDeleteRequest(BaseModel):
    memory_id: str

class TTSRequest(BaseModel):
    text: str
    speaker: int = 1
    speed: float = 1.0
    pitch: float = 0.0
    intonation: float = 1.0

# =========================================================
# good例注入（擬似RLHF）
# =========================================================
def load_recent_good_examples(
    path: str = FEEDBACK_FILE,
    limit: int = 3,
    *,
    allow_code: bool = False,
    preferred_model: str | None = None,
) -> list[str]:
    if not os.path.exists(path):
        return []

    items: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-300:]

        for line in reversed(lines):
            line = (line or "").strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                continue

            if (obj.get("rating") or "").lower() != "good":
                continue

            logged_model = obj.get("model")
            if preferred_model and isinstance(logged_model, str) and logged_model.strip():
                if logged_model.strip() != preferred_model:
                    continue

            u = (obj.get("user_text") or "").strip()
            a = (obj.get("assistant_text") or "").strip()
            if not u or not a:
                continue

            looks_code = _contains_any(u, CODE_MARKERS) or _contains_any(a, CODE_MARKERS)
            looks_heavy = _contains_any(u, HEAVY_WORDS) or _contains_any(a, HEAVY_WORDS)
            if (looks_code or looks_heavy) and not allow_code:
                continue

            u = u[:200]
            a = a[:500]
            items.append(f"【ユーザー】{u}\n【良い回答】{a}")

            if len(items) >= limit:
                break

    except Exception as e:
        print("load_recent_good_examples error:", e)
        return []

    return list(reversed(items))


# =========================================================
# 長期記憶 helper
# =========================================================
def build_long_term_memory_prompt(user_text: str, model: str = FAST_MODEL) -> str:
    limit = SMART_MEMORY_LIMIT if model == SMART_MODEL else FAST_MEMORY_LIMIT
    return build_topic_memory_prompt(memory_db, user_text, limit=limit)

def maybe_store_long_term_memory(user_text: str, intent: dict | None = None):
    if isinstance(intent, dict) and intent.get("memory_intent") is True:
        item = upsert_memory(memory_db, user_text)
    else:
        item = auto_store_user_memory(memory_db, user_text)

    if item:
        persist_memories()
    return item

def finalize_interaction(
    session_id: str,
    session: dict,
    user_text: str,
    assistant_text: str,
    *,
    run_attitude: bool = True,
    intent: dict | None = None,
):
    """
    会話後処理を一元化する。
    - 履歴保存
    - 要約
    - 長期記憶保存
    - タイトル生成
    - sessions保存
    - 人格分析
    """
    _append_session_message(session, "user", user_text)
    _append_session_message(session, "assistant", assistant_text)

    if len(session["messages"]) >= SUMMARIZE_TRIGGER_MSGS:
        summarize_session(session)

    maybe_store_long_term_memory(user_text, intent=intent)

    seed = (session.get("summary") or "").strip() or user_text
    _ensure_title_once(session, seed_text=seed)

    persist_sessions()

    if run_attitude:
        schedule_personality_analysis(session_id, user_text, intent=intent)


# =========================================================
# endpoints
# =========================================================
@app.post("/ask")
def ask(req: AskRequest):
    try:
        q = req.q
        session_id = req.session_id

        session = sessions.get(session_id)
        if not session:
            sessions[session_id] = _new_session()
            session = sessions[session_id]

        # ===== ファイル操作分岐 =====
        file_result = try_file_operation(q)
        if file_result is not None:
            intent = analyze_user_intent_llm(q)
            update_personality(session, q)
            finalize_interaction(session_id, session, q, file_result, intent=intent)

            return {
                "answer": file_result,
                "title": session.get("title", ""),
                "personality": _ensure_personality(session),
            }

        intent = analyze_user_intent_llm(q)

        model = choose_model(q, session, intent=intent)
        print(f"[ask] model={model} intent={intent} session_id={session_id} q={q[:60]!r}")

        update_personality(session, q)

        memories_text = build_long_term_memory_prompt(q, model=model)
        messages = build_messages(
            user_text=user_text,
            history=history,
            memories_text=memories_text,
            summary_text=summary_text,
            personality_text=personality_text,
        )

        personality_text = build_personality_prompt(session, memories_text)
        if personality_text.strip():
            messages.insert(1, {"role": "system", "content": personality_text})

        if STYLE.strip():
            messages.insert(0, {"role": "system", "content": STYLE})

        allow_code = (model == SMART_MODEL) or _quick_code_signal(q) or _contains_any(q, HEAVY_WORDS)
        good_examples = load_recent_good_examples(
            FEEDBACK_FILE,
            limit=2 if model == FAST_MODEL else 3,
            allow_code=allow_code,
            preferred_model=model
        )
        if good_examples:
            example_block = "\n\n".join(good_examples)
            messages.insert(1, {
                "role": "system",
                "content": f"{(GOOD_EXAMPLES_SYSTEM or '').strip()}\n{example_block}".strip()
            })

        opt = OPTIONS["smart_chat"] if model == SMART_MODEL else OPTIONS["fast_chat"]

        raw_answer = call_ollama_chat(messages, model, options=opt)
        answer = format_answer(q, raw_answer)

        finalize_interaction(session_id, session, q, answer, intent=intent)

        return {
            "answer": answer,
            "title": session.get("title", ""),
            "personality": _ensure_personality(session),
        }

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        print("ask() error:", repr(e))
        print(tb)
        raise HTTPException(status_code=500, detail={"error": f"{type(e).__name__}: {str(e)}", "traceback": tb[-2000:]})


@app.post("/new_session")
def new_session():
    sid = str(uuid.uuid4())
    sessions[sid] = _new_session()
    persist_sessions()
    return {"session_id": sid, "title": "新しいチャット"}


@app.post("/ask_stream")
def ask_stream(req: AskRequest):
    q = req.q
    session_id = req.session_id

    session = sessions.get(session_id)
    if not session:
        sessions[session_id] = _new_session()
        session = sessions[session_id]

    # ===== ファイル操作分岐 =====
    file_result = try_file_operation(q)
    if file_result is not None:
        def file_event():
            yield f"data: {json.dumps({'type':'delta','text':file_result}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type':'meta','title':session.get('title',''), 'model':'file-op', 'personality': _ensure_personality(session)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        intent = analyze_user_intent_llm(q)
        update_personality(session, q)
        finalize_interaction(session_id, session, q, file_result, intent=intent)

        return StreamingResponse(file_event(), media_type="text/event-stream")

    intent = analyze_user_intent_llm(q)

    model = choose_model(q, session, intent=intent)
    print(f"[ask_stream] model={model} intent={intent} session_id={session_id} q={q[:60]!r}")

    opt = OPTIONS["smart_chat"] if model == SMART_MODEL else OPTIONS["fast_chat"]

    update_personality(session, q)

    memories_text = build_long_term_memory_prompt(q, model=model)
    messages = build_messages(
        session=session,
        user_text=q,
        rules_text=RULES,
        memories_text=memories_text,
    )

    personality_text = build_personality_prompt(session, memories_text)
    if personality_text.strip():
        messages.insert(1, {"role": "system", "content": personality_text})

    if STYLE.strip():
        messages.insert(0, {"role": "system", "content": STYLE})

    allow_code = (model == SMART_MODEL) or _quick_code_signal(q) or _contains_any(q, HEAVY_WORDS)
    good_examples = load_recent_good_examples(
    FEEDBACK_FILE,
    limit=2 if model == FAST_MODEL else 3,
    allow_code=allow_code,
    preferred_model=model
    )
    if good_examples:
        example_block = "\n\n".join(good_examples)
        messages.insert(1, {
            "role": "system",
            "content": f"{(GOOD_EXAMPLES_SYSTEM or '').strip()}\n{example_block}".strip()
        })

    def event_gen():
        answer_parts: list[str] = []
        try:
            for delta in stream_ollama_chat(messages, model, options=opt):
                answer_parts.append(delta)
                yield f"data: {json.dumps({'type':'delta','text':delta}, ensure_ascii=False)}\n\n"

            raw_answer = "".join(answer_parts)

            final_answer = raw_answer
            try:
                formatted = format_answer(q, raw_answer)
                if isinstance(formatted, str) and formatted.strip() and formatted.strip() != raw_answer.strip():
                    final_answer = formatted
                    yield f"data: {json.dumps({'type':'replace','text':formatted}, ensure_ascii=False)}\n\n"
            except Exception as e:
                print("format in stream error:", e)

            finalize_interaction(session_id, session, q, final_answer, intent=intent)

            yield f"data: {json.dumps({'type':'meta','title':session.get('title',''), 'model':model, 'personality': _ensure_personality(session)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type':'error','message':f'{type(e).__name__}: {str(e)}'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.post("/reset")
def reset_session(req: ResetRequest):
    sessions.pop(req.session_id, None)
    persist_sessions()
    return {"status": "ok"}


@app.post("/delete_session")
def delete_session(req: DeleteSessionRequest):
    sessions.pop(req.session_id, None)
    persist_sessions()
    return {"status": "ok"}


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    try:
        rating = (req.rating or "").strip().lower()
        if rating not in ("good", "bad"):
            raise HTTPException(status_code=400, detail="rating must be 'good' or 'bad'")

        item = {
            "ts": time.time(),
            "session_id": req.session_id,
            "user_text": req.user_text,
            "assistant_text": req.assistant_text,
            "rating": rating,
            "model": req.model,
            "reason": req.reason,
        }

        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="feedback save failed")


@app.get("/sessions")
def list_sessions():
    items = []
    for sid, s in sessions.items():
        title = (s.get("title") or "").strip() or "新しいチャット"
        created_at = s.get("created_at") or 0
        items.append({"id": sid, "title": title, "created_at": created_at})

    items.sort(key=lambda x: x["created_at"], reverse=True)
    items = [{"id": x["id"], "title": x["title"]} for x in items]
    return {"sessions": items}


@app.get("/history")
def get_history(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return {"summary": "", "messages": [], "personality": _init_personality()}

    return {
        "summary": session.get("summary", ""),
        "messages": session.get("messages", []),
        "personality": _ensure_personality(session),
    }

@app.get("/title")
def create_title(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")

    if session.get("title_fixed") is True:
        return {"title": session.get("title", "")}

    if session.get("summary"):
        seed_text = session["summary"]
    else:
        users = [m["content"] for m in session.get("messages", []) if m.get("role") == "user"]
        seed_text = users[0] if users else ""

    _ensure_title_once(session, seed_text=seed_text)
    persist_sessions()
    return {"title": session.get("title", "")}


# ===== 長期記憶 API =====
@app.get("/memories")
def get_memories():
    return {"memories": list_memories(memory_db, limit=200)}


@app.post("/memory/save")
def save_memory(req: MemorySaveRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    item = upsert_memory(memory_db, text, kind=req.kind)
    persist_memories()
    return {"status": "ok", "memory": item}


@app.post("/memory/delete")
def remove_memory(req: MemoryDeleteRequest):
    ok = delete_memory(memory_db, req.memory_id)
    if not ok:
        raise HTTPException(status_code=404, detail="memory not found")
    persist_memories()
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

# ==============================
# 音声合成API（VOICEVOX）
# ==============================
@app.post("/tts")
def tts(req: TTSRequest):
    try:
        audio = synthesize_voice(
            req.text,
            speaker=req.speaker,
            speed=req.speed,
            pitch=req.pitch,
            intonation=req.intonation
        )

        return StreamingResponse(
            BytesIO(audio),
            media_type="audio/wav"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))