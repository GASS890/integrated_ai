# ollama_client.py
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

# ★HTTP接続を再利用（keep-alive）
http_session = requests.Session()

# ===== 用途別オプション =====
OPTIONS = {
    # 雑談・短文：速く、ブレ少なく、短め
    "fast_chat": {
        "temperature": 0.35,
        "top_p": 0.9,
        "num_predict": 180,
        "num_ctx": 2048,
    },
    # 設計/デバッグ：長め出力を許可
    "smart_chat": {
        "temperature": 0.45,
        "top_p": 0.9,
        "num_predict": 768,
        "num_ctx": 4096,
    },
    # 整形：ブレない（低温度）、そこそこ短い
    "format": {
        "temperature": 0.2,
        "top_p": 0.9,
        "num_predict": 400,
    },
    # 要約：ブレない、短め
    "summarize": {
        "temperature": 0.2,
        "top_p": 0.9,
        "num_predict": 280,
    },
    # タイトル：超短い
    "title": {
        "temperature": 0.2,
        "top_p": 0.9,
        "num_predict": 60,
    },
}

def _pick_timeout(model: str, options: dict | None) -> int:
    """
    用途別にタイムアウトを調整する。
    - fast: 短め（失敗したら早く返す）
    - smart/長文: 長め（生成時間を許容）
    """
    # options の num_predict が大きいほど時間がかかりやすい
    num_predict = None
    if isinstance(options, dict):
        num_predict = options.get("num_predict")

    # 明示的に大きいなら長め
    if isinstance(num_predict, int) and num_predict >= 800:
        return 300

    # モデル名でざっくり
    m = (model or "").lower()
    if "14b" in m or "32b" in m or "70b" in m:
        return 300

    return 90

def call_ollama_chat(messages, model, options=None, timeout=None):
    """
    通常（非ストリーミング）で Ollama Chat を呼び出し、assistant の全文を返す
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if options:
        payload["options"] = options

    if timeout is None:
        timeout = _pick_timeout(model, options)

    res = http_session.post(OLLAMA_URL, json=payload, timeout=timeout)
    res.raise_for_status()

    data = res.json()
    if "message" not in data or "content" not in data["message"]:
        raise RuntimeError(f"Ollama response format error: {data}")

    return data["message"]["content"]

def stream_ollama_chat(messages, model, options=None, timeout=None):
    """
    stream=True を使って、増分テキスト（delta）を yield する
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if options:
        payload["options"] = options

    if timeout is None:
        timeout = _pick_timeout(model, options)

    with http_session.post(
        OLLAMA_URL,
        json=payload,
        timeout=timeout,
        stream=True
    ) as res:
        res.raise_for_status()

        for line in res.iter_lines(decode_unicode=True):
            if not line:
                continue

            data = json.loads(line)
            if data.get("done") is True:
                break

            delta = (data.get("message") or {}).get("content") or ""
            if delta:
                yield delta