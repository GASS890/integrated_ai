import json
import os
import time

INPUT_FILE = "eval_logs.jsonl"
OUTPUT_FILE = "eval_results.jsonl"


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


def contains_any(text: str, words: list[str]) -> bool:
    if not isinstance(text, str):
        return False
    return any(w in text for w in words)


def is_mostly_japanese(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False

    jp_count = 0
    total = 0

    for ch in text:
        code = ord(ch)
        if ch.isspace():
            continue
        total += 1
        if (
            0x3040 <= code <= 0x309F or  # ひらがな
            0x30A0 <= code <= 0x30FF or  # カタカナ
            0x4E00 <= code <= 0x9FFF     # 漢字
        ):
            jp_count += 1

    if total == 0:
        return False

    return (jp_count / total) >= 0.2


def score_answer(answer: str) -> dict:
    answer = answer or ""

    score = 0
    checks = {}

    checks["has_answer"] = bool(answer.strip())
    if checks["has_answer"]:
        score += 20

    checks["is_japanese"] = is_mostly_japanese(answer)
    if checks["is_japanese"]:
        score += 20

    checks["not_too_short"] = len(answer.strip()) >= 8
    if checks["not_too_short"]:
        score += 10

    checks["not_too_long"] = len(answer) <= 1200
    if checks["not_too_long"]:
        score += 10

    checks["has_conclusion_like"] = contains_any(answer, ["結論", "補足"])
    if checks["has_conclusion_like"]:
        score += 15

    checks["mentions_uncertainty"] = contains_any(answer, ["不確実", "推測", "情報不足", "分かりません"])
    if checks["mentions_uncertainty"]:
        score += 5

    checks["no_obvious_refusal_noise"] = not contains_any(
        answer,
        ["申し訳ありませんが、そのリクエストにはお応えできません"]
    )
    if checks["no_obvious_refusal_noise"]:
        score += 5

    checks["no_traceback"] = not contains_any(
        answer,
        ["Traceback", "Exception", "Error:"]
    )
    if checks["no_traceback"]:
        score += 15

    return {
        "score": score,
        "checks": checks,
    }


def main():
    logs = read_jsonl(INPUT_FILE)
    print(f"[start] logs={len(logs)}")

    count = 0

    for item in logs:
        answer = item.get("answer")
        if not isinstance(answer, str):
            continue

        result = score_answer(answer)

        out = {
            "ts": time.time(),
            "run_id": item.get("run_id"),
            "scenario_id": item.get("scenario_id"),
            "category": item.get("category"),
            "user": item.get("user"),
            "answer": answer,
            "title": item.get("title"),
            "score": result["score"],
            "checks": result["checks"],
        }

        append_jsonl(OUTPUT_FILE, out)
        count += 1

    print(f"[done] scored={count}")


if __name__ == "__main__":
    main()