import json
import os
import time

INPUT_FILE = "eval_results.jsonl"
OUTPUT_FILE = "feedback.jsonl"
MIN_SCORE = 85


def read_jsonl(path: str):
    items = []
    if not os.path.exists(path):
        return items

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def append_jsonl(path: str, obj: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main():
    results = read_jsonl(INPUT_FILE)
    print(f"[start] results={len(results)} min_score={MIN_SCORE}")

    imported = 0
    skipped = 0

    for item in results:
        score = item.get("score")
        answer = item.get("answer")
        user_text = item.get("user")

        if not isinstance(score, int):
            skipped += 1
            continue

        if score < MIN_SCORE:
            skipped += 1
            continue

        if not isinstance(user_text, str) or not user_text.strip():
            skipped += 1
            continue

        if not isinstance(answer, str) or not answer.strip():
            skipped += 1
            continue

        feedback_item = {
            "ts": time.time(),
            "session_id": f"auto_eval_{item.get('run_id', 'unknown')}",
            "user_text": user_text,
            "assistant_text": answer,
            "rating": "good",
            "model": "auto-import",
            "reason": f"auto_import score={score} scenario_id={item.get('scenario_id')}",
        }

        append_jsonl(OUTPUT_FILE, feedback_item)
        imported += 1

    print(f"[done] imported={imported} skipped={skipped}")


if __name__ == "__main__":
    main()