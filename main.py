from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dev_assistant.auto_change_flow import propose_change, approve_change
from dev_assistant.manual_change_flow import (
    apply_manual_change_plan,
    restore_from_change_history,
)
from prompts import build_messages
from dev_assistant.developer_agent import (
    ask_developer_agent,
    propose_archive_update,
    propose_pending_patch,
    propose_autonomous_development,
    reflect_improvement_to_pending_patch,
    reflect_saved_improvement_to_pending_patch,
    save_improvement_text,
)
from dev_assistant.dev_mode import DevMode
from dev_assistant.archive_manager import append_archive
from dev_assistant.pending_archive import load_pending_update, clear_pending_update
from dev_assistant.pending_patch import has_pending_patch, load_pending_patch, delete_pending_patch
from dev_assistant.safe_apply import apply_pending_patch_with_compile_check
from dev_assistant.code_reviewer import review_current_diff, is_review_approved
from dev_assistant.commit_message_generator import generate_commit_message
from dev_assistant.git_tools import get_git_status, get_git_diff, commit_all_changes, push_to_origin

from dev_assistant.check_tools import py_compile_all
from dev_assistant.release_check import release_check
from dev_assistant.release_candidate import generate_release_candidate_report
from dev_assistant.autonomous_history import get_autonomous_history_report

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

from llm_client import call_chat_routed as call_chat, stream_chat_routed as stream_chat, OPTIONS
from voicevox_client import synthesize_voice
from io import BytesIO
from file_ops import (
    write_file,
    append_file,
    read_file,
    read_line,
    delete_line,
    list_files,
    search_text_in_files,
    search_function,
    search_import,
    show_change_candidate,
    replace_text_in_file,
    preview_replace_plan,
    replace_text_from_plan,
    py_compile_file,
    restore_backup,
)
from memory_store import (
    load_memory_db,
    save_memory_db,
    auto_store_user_memory,
    build_topic_memory_prompt,
    list_memories,
    upsert_memory,
    delete_memory,
)

from personality.state_manager import _init_personality, _ensure_personality
from personality.affinity import update_personality
from personality.personality_prompt import build_personality_prompt
from personality.attitude_analysis import analyze_user_intent_llm, schedule_personality_analysis
from personality.state_schema import normalize_sessions_personality
from memory.vector_search import search_similar_memories
from memory.memory_reflection import reflect_conversation_to_memory
from memory.embedding_store import load_embedding_memories, add_embedding_memory
from personality.learning_config import describe_learning_strength
from personality.tone_profile import update_tone_profile, build_tone_prompt, summarize_tone_profile
from personality.growth_manager import update_growth_state, build_growth_prompt, summarize_growth_state

DEVELOPER_SESSION_ID = "__developer_chat__"
DEVELOPER_SESSION_TITLE = "🛠 開発・改善専用"

def is_developer_chat(session_id: str | None) -> bool: return session_id == DEVELOPER_SESSION_ID
def handle_code_lookup_command(q: str) -> str:
    lines = [line.strip() for line in q.splitlines() if line.strip()]
    if len(lines) < 2:
        return "使い方:\nコード取得:\nmain.py\n検索キーワード"

    target_path = lines[1]
    keyword = lines[2] if len(lines) >= 3 else ""
    context = 25

    if not os.path.exists(target_path):
        return f"ファイルが見つかりません: {target_path}"

    with open(target_path, "r", encoding="utf-8") as f:
        file_lines = f.read().splitlines()

    if keyword:
        hit_index = None
        for i, line in enumerate(file_lines):
            if keyword in line:
                hit_index = i
                break
        if hit_index is None:
            return f"キーワードが見つかりません: {keyword}"

        start = max(0, hit_index - context)
        end = min(len(file_lines), hit_index + context + 1)
    else:
        start = 0
        end = min(len(file_lines), 80)

    body = []
    for i in range(start, end):
        body.append(f"{i + 1}: {file_lines[i]}")

    return "===== Code Lookup =====\nfile: " + target_path + "\nkeyword: " + keyword + "\n\n```text\n" + "\n".join(body) + "\n```"

from app_settings import (
    load_app_settings,
    is_developer_agent_enabled,
    set_developer_agent_enabled,
    is_auto_git_commit_enabled,
    is_auto_git_push_enabled,
    get_autonomous_level,
    set_autonomous_level,
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
        formatted = call_chat(prompt, FORMAT_MODEL, options=OPTIONS["format"])
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
        title = call_chat(prompt, TITLE_MODEL, options=OPTIONS["title"]) or ""
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
        new_summary = call_chat(summary_prompt, SUMMARIZE_MODEL, options=OPTIONS["summarize"]) or ""
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
            session["summary"] = call_chat(shrink_prompt, SUMMARIZE_MODEL, options=OPTIONS["summarize"]) or s
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

        # ===== 開発補助: ファイル一覧 =====
        if text in [
            "ファイル一覧",
            "ファイル構成",
            "現在のファイル構成",
            "プロジェクト構成",
        ]:
            return list_files(".", max_depth=3)
        
        # ===== 開発補助: ファイル内検索 =====
        if text.startswith("検索 "):
            keyword = text.replace("検索 ", "", 1).strip()

            if not keyword:
                return "検索語を入力してください。"

            return search_text_in_files(keyword)

        if text.startswith("search "):
            keyword = text.replace("search ", "", 1).strip()

            if not keyword:
                return "検索語を入力してください。"

            return search_text_in_files(keyword)

        # ===== 開発補助: 関数検索 =====
        if text.startswith("関数 "):
            func_name = text.replace("関数 ", "", 1).strip()

            if not func_name:
                return "関数名を入力してください。"

            return search_function(func_name)

        if text.startswith("function "):
            func_name = text.replace("function ", "", 1).strip()

            if not func_name:
                return "関数名を入力してください。"

            return search_function(func_name)

        # ===== 開発補助: import検索 =====
        if text.startswith("import "):
            keyword = text.replace("import ", "", 1).strip()

            if not keyword:
                return "import検索語を入力してください。"

            return search_import(keyword)

        if text.startswith("インポート "):
            keyword = text.replace("インポート ", "", 1).strip()

            if not keyword:
                return "import検索語を入力してください。"

            return search_import(keyword)

        # ===== 開発補助: 変更候補表示 =====
        if text.startswith("変更候補 "):
            keyword = text.replace("変更候補 ", "", 1).strip()

            if not keyword:
                return "変更候補の検索語を入力してください。"

            return show_change_candidate(keyword)

        if text.startswith("candidate "):
            keyword = text.replace("candidate ", "", 1).strip()

            if not keyword:
                return "変更候補の検索語を入力してください。"

            return show_change_candidate(keyword)

        # ===== 開発補助: 置換実行 =====
        if text.startswith("置換実行 "):
            plan_path = text.replace("置換実行 ", "", 1).strip()

         # ===== 開発補助: 置換プレビュー =====
        if text.startswith("置換確認 "):
            plan_path = text.replace("置換確認 ", "", 1).strip()

            if not plan_path:
                return "置換指示ファイル名を入力してください。"

            return preview_replace_plan(plan_path)

        if text.startswith("preview-replace "):
            plan_path = text.replace("preview-replace ", "", 1).strip()

            if not plan_path:
                return "置換指示ファイル名を入力してください。"

            return preview_replace_plan(plan_path)

        # ===== 開発補助: 置換実行 =====
        if text.startswith("置換実行 "):
            if not plan_path:
                return "置換指示ファイル名を入力してください。"

            return replace_text_from_plan(plan_path)

        if text.startswith("replace-plan "):
            plan_path = text.replace("replace-plan ", "", 1).strip()

            if not plan_path:
                return "置換指示ファイル名を入力してください。"

            return replace_text_from_plan(plan_path)

        # ===== 開発補助: 構文チェック =====
        if text.startswith("構文確認 "):
            path = text.replace("構文確認 ", "", 1).strip()

            if not path:
                return "構文確認するファイル名を入力してください。"

            return py_compile_file(path)

        if text.startswith("compile "):
            path = text.replace("compile ", "", 1).strip()

            if not path:
                return "構文確認するファイル名を入力してください。"

            return py_compile_file(path)

        # ===== 開発補助: ロールバック =====
        if text.startswith("復元 "):
            path = text.replace("復元 ", "", 1).strip()

            if not path:
                return "復元するファイル名を入力してください。"

            return restore_backup(path)

        if text.startswith("rollback "):
            path = text.replace("rollback ", "", 1).strip()

            if not path:
                return "復元するファイル名を入力してください。"

            return restore_backup(path)

        if text.startswith("replace-plan "):
            plan_path = text.replace("replace-plan ", "", 1).strip()

            if not plan_path:
                return "置換指示ファイル名を入力してください。"

            return replace_text_from_plan(plan_path)

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

        if text.startswith("読込 "):
            filename = text.replace("読込 ", "", 1).strip()
            return read_file(filename)

        if text.startswith("read "):
            filename = text.replace("read ", "", 1).strip()
            return read_file(filename)

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
    personality_id = "default"

    session = {
        "title": "",
        "title_fixed": False,
        "summary": "",
        "messages": [],
        "created_at": time.time(),
        "personality_id": personality_id,
    }

    _ensure_personality(session)

    return session

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
        safe_sessions = {}

        for sid, s in sessions.items():
            copy_session = dict(s)

            if "personality" in copy_session:
                del copy_session["personality"]

            safe_sessions[sid] = copy_session

        save_sessions_to_file(safe_sessions)


def persist_memories():
    with memories_lock:
        save_memory_db(memory_db, MEMORY_FILE)

_loaded = load_sessions_from_file()
_loaded = normalize_sessions_personality(_loaded)

if DEVELOPER_SESSION_ID not in _loaded: _loaded[DEVELOPER_SESSION_ID] = {"title": DEVELOPER_SESSION_TITLE, "title_fixed": True, "summary": "", "messages": [], "created_at": time.time(), "personality_id": "default", "chat_type": "developer"}

_now = time.time()
for sid, s in _loaded.items():
    if isinstance(s, dict) and "created_at" not in s:
        s["created_at"] = _now
    if isinstance(s, dict) and "title_fixed" not in s:
        s["title_fixed"] = False
    if isinstance(s, dict):
        s["personality_id"] = s.get("personality_id") or "default"
        _ensure_personality(s)

sessions = defaultdict(_new_session, _loaded)
memory_db = load_memory_db(MEMORY_FILE)


# =========================================================
# Request Body
# =========================================================
class AskRequest(BaseModel):
    message: str
    session_id: str | None = None


class DevChangeRequest(BaseModel):
    request: str
    files: list[str]

class AppSettingsRequest(BaseModel):
    use_developer_agent: bool

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


class EmbeddingMemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5


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

    return "\n".join(lines)

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
    update_tone_profile(session, user_text)
    update_growth_state(session, user_text, assistant_text)

    _append_session_message(session, "user", user_text)
    _append_session_message(session, "assistant", assistant_text)

    if len(session["messages"]) >= SUMMARIZE_TRIGGER_MSGS:
        summarize_session(session)

    maybe_store_long_term_memory(user_text, intent=intent)

    try:
        reflect_conversation_to_memory(user_text, assistant_text)
    except Exception as e:
        print("embedding memory reflection error:", e)

    seed = (session.get("summary") or "").strip() or user_text
    _ensure_title_once(session, seed_text=seed)

    persist_sessions()

    if run_attitude:
        schedule_personality_analysis(session_id, user_text, intent=intent)

def is_developer_request(text: str) -> bool:
    keywords = [
        "実装",
        "修正",
        "改善",
        "変更",
        "リファクタ",
        "レビュー",
        "コードレビュー",
        "backend",
        "llm backend",
        "OpenAI backend",
        "エラー修正",
        "コード変更",
        "開発相談",
    ]

    lowered = text.lower()

    return any(keyword.lower() in lowered for keyword in keywords)

def is_improvement_proposal_text(
    text: str,
) -> bool:
    normalized = (
        text.replace(" ", "")
        .replace("　", "")
    )

    target_patterns = [
        "変更対象ファイル",
        "対象ファイル",
    ]

    purpose_patterns = [
        "変更目的",
        "目的",
    ]

    before_patterns = [
        "変更前コード",
        "変更前",
        "-----変更前-----",
    ]

    after_patterns = [
        "変更後コード",
        "変更後",
        "-----変更後-----",
    ]

    return (
        any(
            pattern in normalized
            for pattern in target_patterns
        )
        and any(
            pattern in normalized
            for pattern in purpose_patterns
        )
        and any(
            pattern in normalized
            for pattern in before_patterns
        )
        and any(
            pattern in normalized
            for pattern in after_patterns
        )
    )

@app.get("/app_settings")
def get_app_settings():
    return load_app_settings()

@app.post("/app_settings")
def update_app_settings(req: AppSettingsRequest):
    return set_developer_agent_enabled(
        req.use_developer_agent
    )

@app.post("/dev/propose_change")
def dev_propose_change(req: DevChangeRequest):
    return {
        "result": propose_change(req.request, req.files)
    }


@app.post("/dev/approve_change")
def dev_approve_change():
    return {
        "result": approve_change()
    }




@app.get("/change_history_view")
def change_history_view():
    try:
        import subprocess

        r = subprocess.run(
            [
                "git",
                "log",
                "--date=format:%Y-%m-%d %H:%M",
                "--pretty=format:%h%x09%d%x09%ad%x09%s",
                "-30",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if r.returncode != 0:
            return {"text": "Git履歴の取得に失敗しました。\n" + r.stderr}

        if not r.stdout.strip():
            return {"text": "変更履歴はまだありません。"}

        def translate_message(msg: str) -> str:
            rules = [
                ("Force fix change history view endpoint", "変更履歴表示APIの不具合を強制修正"),
                ("Fix change history GUI and developer chat UI", "変更履歴GUIと開発専用チャット表示を修正"),
                ("Fix phase1d history view and developer chat UI", "Phase1-Dの履歴表示と開発専用チャットUIを修正"),
                ("Fix change history view with direct git log", "変更履歴をGit履歴から直接表示するよう修正"),
                ("Add safe change history GUI button", "安全版の変更履歴ボタンを追加"),
                ("Restore developer chat color and delete lock", "開発専用チャットの色分けと削除禁止を復元"),
                ("Add safe change history view API", "安全版の変更履歴表示APIを追加"),
                ("Show developer chat in chat list", "開発・改善専用チャットを一覧に表示"),
                ("Fix ask_stream command handling", "ask_streamのコマンド処理を修正"),
                ("Add standalone code lookup tool", "単体コード取得ツールを追加"),
                ("Fix code lookup stream display", "コード取得のストリーム表示を修正"),
                ("Wire code lookup command to stream route", "コード取得コマンドをストリーム経路へ接続"),
                ("Wire code lookup command to ask route", "コード取得コマンドを通常応答経路へ接続"),
                ("Add code lookup command", "コード取得コマンドを追加"),
                ("Add fixed developer chat session for phase0", "Phase0用の固定開発チャットセッションを追加"),
            ]

            for en, ja in rules:
                if en in msg:
                    return ja

            return msg

        lines = ["===== 変更履歴 ====="]

        for raw in r.stdout.splitlines():
            parts = raw.split("\t")
            if len(parts) < 4:
                continue

            commit_hash, decoration, date_text, message = parts[0], parts[1], parts[2], parts[3]

            version = ""
            for token in decoration.replace("(", "").replace(")", "").split(","):
                token = token.strip()
                if token.startswith("tag:"):
                    tag = token.replace("tag:", "").strip()
                    if tag.startswith("v"):
                        version = tag
                        break

            if not version:
                version = "タグなし"

            summary = translate_message(message)

            lines.append("")
            lines.append(f"■ {version}")
            lines.append(f"日時: {date_text}")
            lines.append(f"内容: {summary}")
            lines.append(f"コミット: {commit_hash}")

            if version != "タグなし":
                lines.append(f"復元: バージョン復元:{version}")

            lines.append("--------------------------------")

        lines.append("")
        lines.append("復元する場合は、開発・改善専用チャットで以下の形式を送信してください。")
        lines.append("バージョン復元:v0.99-test-xx")

        return {"text": "\n".join(lines)}

    except Exception as e:
        return {"text": f"変更履歴の取得に失敗しました: {type(e).__name__}: {e}"}


def handle_llm_status_command() -> str:
    try:
        from llm.router import get_backend
        backend = get_backend("ollama")

        return "\n".join([
            "===== LLM確認 =====",
            "router: OK",
            f"default backend: {backend.name}",
            "available backends: ollama, openai, claude",
            "current mode: main.py -> llm_client.call_chat_routed -> Ollama",
        ])
    except Exception as e:
        return f"LLM確認に失敗しました: {type(e).__name__}: {e}"



def handle_llm_status_command() -> str:
    try:
        import json
        from pathlib import Path
        from llm.router import get_backend, load_default_backend

        config_path = Path("config/llm_backend.json")
        config_backend = "ollama"

        if config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8-sig"))
            config_backend = data.get("default_backend", "ollama")

        active_backend = load_default_backend()
        backend = get_backend(active_backend)

        openai_ready = False
        try:
            from llm.openai_backend import OpenAIBackend
            openai_ready = OpenAIBackend().is_configured()
        except Exception:
            openai_ready = False

        return "\n".join([
            "===== LLM確認 =====",
            "router: OK",
            f"設定ファイル: {config_path}",
            f"設定上のbackend: {config_backend}",
            f"有効backend: {backend.name}",
            "利用可能backend: ollama, openai, claude",
            f"OpenAI APIキー: {'設定済み' if openai_ready else '未設定'}",
            "現在の経路: main.py -> llm_client.call_chat_routed -> Ollama",
        ])

    except Exception as e:
        return f"LLM確認に失敗しました: {type(e).__name__}: {e}"



def handle_llm_switch_command(q: str) -> str:
    try:
        import json
        from pathlib import Path

        backend = q.replace("LLM切替:", "", 1).strip()
        allowed = {"ollama", "openai", "claude"}

        if backend not in allowed:
            return "指定できるbackendは ollama / openai / claude です。\n例: LLM切替:ollama"

        config_path = Path("config/llm_backend.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_path.write_text(
            json.dumps({"default_backend": backend}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        note = ""
        if backend != "ollama":
            note = "\n注意: openai / claude backend はまだ未接続です。"

        return f"LLM backendを {backend} に切り替えました。{note}"

    except Exception as e:
        return f"LLM backend切替に失敗しました: {type(e).__name__}: {e}"


# =========================================================
# endpoints
# =========================================================
@app.post("/ask")
def ask(req: AskRequest):
    # phase0 code lookup command
    if req.message.startswith("コード取得:"):
        return {"reply": handle_code_lookup_command(req.message)}

    try:
        q = req.message
        session_id = req.session_id

        if q.startswith("LLM切替:"):
            return {"answer": handle_llm_switch_command(q)}


        if q.startswith("LLM確認"):
            return {"answer": handle_llm_status_command()}


        if q.startswith("コード取得:"):
            return {"reply": handle_code_lookup_command(q)}

        if q.startswith("改善案反映:"):
            try:
                plan_text = q.replace("改善案反映:", "", 1).strip()
                result = apply_manual_change_plan(plan_text)

                return {
                    "answer": result
                }

            except Exception as e:
                return {
                    "answer": f"改善案適用失敗: {e}"
                }

        if q.startswith("バージョン復元:"):
            try:
                version = q.replace("バージョン復元:", "", 1).strip()
                result = restore_from_change_history(version)

                return {
                    "answer": result
                }

            except Exception as e:
                return {
                    "answer": f"バージョン復元失敗: {e}"
                }

        if q.startswith("アーカイブ更新案"):
            completed_work = q.replace("アーカイブ更新案", "", 1).strip()

            if not completed_work:
                completed_work = "直近のDeveloper Agent実装作業"
        
            result = propose_archive_update(completed_work)

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "archive_proposal",
            }

            def archive_event():
                yield f"data: {json.dumps({'type': 'replace', 'text': result}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'meta', 'title': '', 'model': 'archive_proposal', 'personality': {}}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                archive_event(),
                media_type="text/event-stream",
            )

        if q.startswith("自律開発レベル "):
            value = q.replace("自律開発レベル ", "", 1).strip()

            try:
                level = int(value)
                settings = set_autonomous_level(level)
                result = (
                    "自律開発レベルを更新しました。\n"
                    f"autonomous_level: {settings.get('autonomous_level')}"
                )
            except Exception as e:
                result = (
                    "自律開発レベルの更新に失敗しました。\n"
                    f"{type(e).__name__}: {e}"
                )

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "autonomous_level",
            }

        if q.strip() == "自律開発レベル":
            result = (
                "現在の自律開発レベル:\n"
                f"{get_autonomous_level()}"
            )

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "autonomous_level",
            }

        if q.startswith("自律開発 "):
            goal = q.replace("自律開発 ", "", 1).strip()

            if not goal:
                result = "自律開発の目標が空です。"
            else:
                result = propose_autonomous_development(goal)

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "autonomous_development",
            }

        if is_improvement_proposal_text(q):
            save_result = save_improvement_text(q)

            try:
                reflect_result = reflect_saved_improvement_to_pending_patch()
                result = (
                    f"{save_result}\n\n"
                    "===== auto reflect result =====\n"
                    f"{reflect_result}"
                )
            except Exception as e:
                result = (
                    f"{save_result}\n\n"
                    "===== auto reflect failed =====\n"
                    f"{type(e).__name__}: {e}"
                )

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "auto_save_and_reflect_improvement",
            }

        if q.startswith("改善案保存"):
            improvement_text = q.replace("改善案保存", "", 1).strip()

            result = save_improvement_text(improvement_text)

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "save_improvement",
            }

        if q.startswith("改善案反映"):
            improvement_text = q.replace("改善案反映", "", 1).strip()

            if not improvement_text:
                result = "改善案の内容が空です。"
            else:
                result = reflect_improvement_to_pending_patch(improvement_text)

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "reflect_improvement",
            }

        if q.startswith("変更提案 "):
            instruction = q.replace("変更提案 ", "", 1).strip()

            if not instruction:
                result = "変更提案の内容が空です。"
            else:
                result = propose_pending_patch(instruction)

            def propose_patch_event():
                yield f"data: {json.dumps({'type': 'replace', 'text': result}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'meta', 'title': '', 'model': 'propose_patch', 'personality': {}}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                propose_patch_event(),
                media_type="text/event-stream",
            )

        if q.strip() == "変更却下":
            deleted = delete_pending_patch()

            if deleted:
                result = (
                    "保留中の変更案を却下しました。\n"
                    "pending_patch.json を削除しました。"
                )
            else:
                result = "却下する変更案はありません。"
    
            def reject_patch_event():
                yield f"data: {json.dumps({'type': 'replace', 'text': result}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'meta', 'title': '', 'model': 'reject_patch', 'personality': {}}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
    
            return StreamingResponse(
                reject_patch_event(),
                media_type="text/event-stream",
            )

        if q.strip() == "変更承認":
            try:
                patch = load_pending_patch()
                commit_message = generate_commit_message(patch.purpose)

                apply_result = apply_pending_patch_with_compile_check()

                if apply_result.startswith("Patch applied successfully."):
                    review_result = review_current_diff()

                    if not is_review_approved(review_result):
                        git_result = (
                            "Git commit skipped because code review was not approved."
                        )
                    elif is_auto_git_commit_enabled():
                        git_result = commit_all_changes(
                            commit_message
                        )

                        if git_result.startswith("Git commit completed."):
                            if is_auto_git_push_enabled():
                                push_result = push_to_origin()
                                git_result = (
                                    f"{git_result}\n\n"
                                    "===== git push result =====\n"
                                    f"{push_result}"
                                )
                            else:
                                git_result = (
                                    f"{git_result}\n\n"
                                    "Git push skipped because auto_git_push is disabled."
                                )
                    else:
                        git_result = "Auto git commit is disabled."

                    result = (
                        f"{apply_result}\n\n"
                        "===== code review result =====\n"
                        f"{review_result}\n\n"
                        "===== git commit result =====\n"
                        f"{git_result}"
                    )
                else:
                    result = apply_result

            except Exception as e:
                result = f"変更適用に失敗しました。\n{type(e).__name__}: {e}"

        if q.strip() == "リリース候補":
            result = generate_release_candidate_report()

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "release_candidate",
            }

        if q.strip() == "自律開発履歴":
            result = get_autonomous_history_report()

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "autonomous_history",
            }

        if q.strip() == "コードレビュー":
            try:
                result = review_current_diff()
            except Exception as e:
                result = f"コードレビューに失敗しました。\n{type(e).__name__}: {e}"

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "code_review",
            }

        if is_developer_agent_enabled() and is_developer_request(q):
            result = ask_developer_agent(
                instruction=q,
                mode=DevMode.FEATURE,
            )

            return {
                "answer": result,
                "title": "",
                "personality": {},
                "mode": "developer_agent",
            }

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

        memory_db_text = build_long_term_memory_prompt(q, model=model)
        embedding_text = build_embedding_memory_prompt(q)

        memories_text = "\n\n".join(
            part for part in [memory_db_text, embedding_text]
            if part and part.strip()
        )

        messages = build_messages(
            user_text=q,
            history=session.get("messages", []),
            memories_text=memories_text,
            summary_text=session.get("summary", ""),
            rules_text=RULES,
        )        

        personality_text = build_personality_prompt(session, memories_text)
        if personality_text.strip():
            messages.insert(1, {"role": "system", "content": personality_text})

        tone_text = build_tone_prompt(session)
        if tone_text.strip():
            messages.insert(1, {"role": "system", "content": tone_text})

        growth_text = build_growth_prompt(session)
        if growth_text.strip():
            messages.insert(1, {"role": "system", "content": growth_text})

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

        raw_answer = call_chat(messages, model, options=opt)
        answer = format_answer(q, raw_answer)

        if is_improvement_proposal_text(answer):
            save_result = save_improvement_text(answer)

            try:
                reflect_result = reflect_saved_improvement_to_pending_patch()
                answer = (
                    f"{answer}\n\n"
                    "===== auto saved improvement =====\n"
                    f"{save_result}\n\n"
                    "===== auto reflected pending patch =====\n"
                    f"{reflect_result}\n\n"
                    "次に「変更承認」または「変更却下」を選んでください。"
                )
            except Exception as e:
                answer = (
                    f"{answer}\n\n"
                    "===== auto improvement save failed =====\n"
                    f"{type(e).__name__}: {e}"
                )

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
    session = _new_session()
    session["personality_id"] = "default"

    _ensure_personality(session)

    sessions[sid] = session
    persist_sessions()

    return {"session_id": sid, "title": "新しいチャット"}

@app.post("/ask_stream")
def ask_stream(req: AskRequest):
    try:
        q = req.message
        session_id = req.session_id

        if q.startswith("LLM切替:"):
            msg = handle_llm_switch_command(q)
            def llm_switch_event():
                yield f"data: {json.dumps({'type': 'delta', 'text': msg}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(llm_switch_event(), media_type="text/event-stream")


        if q.startswith("LLM確認"):
            msg = handle_llm_status_command()
            def llm_status_event():
                yield f"data: {json.dumps({'type': 'delta', 'text': msg}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(llm_status_event(), media_type="text/event-stream")


        if q.startswith("コード取得:"):
            lookup_text = handle_code_lookup_command(q)

            def code_lookup_event():
                yield f"data: {json.dumps({'type': 'delta', 'text': lookup_text}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                code_lookup_event(),
                media_type="text/event-stream"
            )

        if q.startswith("改善案反映:"):
            try:
                plan_text = q.replace("改善案反映:", "", 1).strip()
                result = apply_manual_change_plan(plan_text)
            except Exception as e:
                result = f"改善案適用失敗: {e}"

            def manual_change_event():
                yield f"data: {json.dumps({'type': 'delta', 'text': result}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                manual_change_event(),
                media_type="text/event-stream"
            )

        normal_result = ask(req)

        if isinstance(normal_result, dict):
            msg = (
                normal_result.get("answer")
                or normal_result.get("reply")
                or normal_result.get("result")
                or str(normal_result)
            )
        else:
            msg = str(normal_result)

        def normal_chat_event():
            yield f"data: {json.dumps({'type': 'delta', 'text': msg}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            normal_chat_event(),
            media_type="text/event-stream"
        )

    except Exception as e:
        tb = traceback.format_exc()
        print("ask_stream() error:", repr(e))
        print(tb)
        raise HTTPException(status_code=500, detail={"error": f"{type(e).__name__}: {str(e)}", "traceback": tb[-2000:]})

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
        temp_session = {"personality_id": "default"}
        return {
            "summary": "",
            "messages": [],
            "personality": _ensure_personality(temp_session),
        }

    return {
        "summary": session.get("summary", ""),
        "messages": session.get("messages", []),
        "personality": _ensure_personality(session),
        "tone_profile": summarize_tone_profile(session),
        "growth_state": summarize_growth_state(session),
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


@app.get("/personality/growth")
def get_personality_growth(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return summarize_growth_state(session)


@app.get("/personality/tone_profile")
def get_personality_tone_profile(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return summarize_tone_profile(session)


@app.get("/personality/learning_strength")
def get_personality_learning_strength():
    return describe_learning_strength()


@app.get("/memory/embedding")
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

