import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("使い方: python tools/code_lookup.py main.py 検索キーワード")
        return

    target = Path(sys.argv[1])
    keyword = sys.argv[2] if len(sys.argv) >= 3 else ""
    context = 25

    if not target.exists():
        print(f"ファイルが見つかりません: {target}")
        return

    lines = target.read_text(encoding="utf-8").splitlines()

    if keyword:
        hit = None
        for i, line in enumerate(lines):
            if keyword in line:
                hit = i
                break

        if hit is None:
            print(f"キーワードが見つかりません: {keyword}")
            return

        start = max(0, hit - context)
        end = min(len(lines), hit + context + 1)
    else:
        start = 0
        end = min(len(lines), 80)

    print("===== Code Lookup =====")
    print(f"file: {target}")
    print(f"keyword: {keyword}")
    print()

    for i in range(start, end):
        print(f"{i + 1}: {lines[i]}")

if __name__ == "__main__":
    main()
