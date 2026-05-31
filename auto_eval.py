import json
import time
import uuid
import requests

BASE_URL = "http://127.0.0.1:8000"
SCENARIOS_FILE = "eval_scenarios.json"
OUTPUT_FILE = "eval_logs.jsonl"


def load_scenarios(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("eval_scenarios.json は配列形式である必要があります")
    return data


def create_session():
    res = requests.post(f"{BASE_URL}/new_session", timeout=15)
    res.raise_for_status()
    data = res.json()
    return data["session_id"]


def ask_once(session_id: str, user_text: str):
    payload = {
        "q": user_text,
        "session_id": session_id,
    }
    res = requests.post(f"{BASE_URL}/ask", json=payload, timeout=180)
    res.raise_for_status()
    return res.json()


def append_jsonl(path: str, obj: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main():
    scenarios = load_scenarios(SCENARIOS_FILE)

    run_id = str(uuid.uuid4())
    print(f"[start] run_id={run_id} count={len(scenarios)}")

    for i, item in enumerate(scenarios, start=1):
        scenario_id = item.get("id", f"no_id_{i}")
        category = item.get("category", "")
        user_text = item.get("user", "")

        if not isinstance(user_text, str) or not user_text.strip():
            print(f"[skip] {scenario_id} user が空です")
            continue

        try:
            session_id = create_session()
            result = ask_once(session_id, user_text)

            answer = result.get("answer", "")
            title = result.get("title", "")

            log_item = {
                "ts": time.time(),
                "run_id": run_id,
                "scenario_id": scenario_id,
                "category": category,
                "session_id": session_id,
                "user": user_text,
                "answer": answer,
                "title": title,
            }
            append_jsonl(OUTPUT_FILE, log_item)

            print(f"[ok] {i}/{len(scenarios)} {scenario_id}")

        except Exception as e:
            error_item = {
                "ts": time.time(),
                "run_id": run_id,
                "scenario_id": scenario_id,
                "category": category,
                "user": user_text,
                "error": f"{type(e).__name__}: {e}",
            }
            append_jsonl(OUTPUT_FILE, error_item)
            print(f"[error] {i}/{len(scenarios)} {scenario_id} {type(e).__name__}: {e}")

    print("[done]")


if __name__ == "__main__":
    main()