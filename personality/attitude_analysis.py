import json
import re
import threading

#from ollama_client import chat
from personality.state_manager import _ensure_personality


INTENT_OPTIONS = {
    "temperature": 0.1,
    "top_p": 0.8,
    "num_predict": 220,
}


def _extract_json_object(text: str) -> dict:
    if not text:
        return {}

    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}

    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


def analyze_user_intent_llm(user_text: str) -> dict:
    prompt = f"""
次のユーザー発話を分析してください。

出力はJSONのみ。
余計な説明は禁止。

分類:
- sentiment: positive / neutral / negative
- attitude: polite / normal / aggressive
- intimacy_delta: -2〜3 の整数
- reason: 短く

ユーザー発話:
{user_text}
""".strip()

    messages = [
        {
            "role": "system",
            "content": "あなたはユーザー発話の態度分析器です。必ずJSONのみを返します。",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    try:
        return {
            "sentiment": "neutral",
            "attitude": "normal",
            "intimacy_delta": 0,
            "reason": "v0.2 temporary stub",
        }
        data = _extract_json_object(text)

        if not data:
            return {
                "sentiment": "neutral",
                "attitude": "normal",
                "intimacy_delta": 0,
                "reason": "JSON解析失敗",
            }

        return data

    except Exception as e:
        return {
            "sentiment": "neutral",
            "attitude": "normal",
            "intimacy_delta": 0,
            "reason": f"分析失敗: {e}",
        }


def apply_attitude_to_personality(session: dict, intent: dict):
    p = _ensure_personality(session)

    try:
        delta = int(intent.get("intimacy_delta", 0))
    except Exception:
        delta = 0

    p["affinity"] += delta
    p["affinity"] = max(0, min(1000, int(p["affinity"])))

    if p["affinity"] < 100:
        p["tone"] = "normal"
    elif p["affinity"] < 300:
        p["tone"] = "friendly"
    else:
        p["tone"] = "close"

    p["last_sentiment"] = intent.get("sentiment", "neutral")
    p["last_attitude"] = intent.get("attitude", "normal")
    p["last_reason"] = intent.get("reason", "")

    return p


def schedule_personality_analysis(session_id: str, user_text: str, intent: dict | None = None):
    """
    応答速度を落とさないため、LLM態度判定は別スレッドで実行。
    注意:
    session保存関数は main.py 側にあるため、ここでは即時保存しない。
    v0.2では main.py 内の session に対する軽い更新用として使う。
    """

    def worker():
        try:
            if intent is None:
                analyze_user_intent_llm(user_text)
        except Exception:
            pass

    t = threading.Thread(target=worker, daemon=True)
    t.start()