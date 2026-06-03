# file_ops.py
import os
from pathlib import Path

BASE_DIR = os.path.abspath("workspace")

def _safe_path(path: str) -> str:
    full = os.path.abspath(os.path.join(BASE_DIR, path))
    if not full.startswith(BASE_DIR):
        raise ValueError("許可されていないパスです")
    return full

def _read_lines(full: str) -> list[str]:
    if not os.path.exists(full):
        return []
    with open(full, "r", encoding="utf-8") as f:
        return f.readlines()

def _write_lines(full: str, lines: list[str]):
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.writelines(lines)

def _renumber(lines: list[str]) -> list[str]:
    new_lines = []
    for i, line in enumerate(lines, start=1):
        content = line.split(" ", 1)[-1].rstrip("\n")
        new_lines.append(f"{i} {content}\n")
    return new_lines

# ===== 書き込み（改行＋番号付与）=====
def write_file(path: str, content: str) -> str:
    full = _safe_path(path)
    lines = [f"1 {content}\n"]
    _write_lines(full, lines)
    return f"保存しました: {path}"

# ===== 追記（改行＋番号付与）=====
def append_file(path: str, content: str) -> str:
    full = _safe_path(path)
    lines = _read_lines(full)
    num = len(lines) + 1
    lines.append(f"{num} {content}\n")
    _write_lines(full, lines)
    return f"追記しました: {path}"

# ===== 全読込 =====
def read_file(path: str) -> str:
    full = _safe_path(path)
    if not os.path.exists(full):
        raise FileNotFoundError("ファイルが存在しません")
    return "".join(_read_lines(full))

# ===== 行読込 =====
def read_line(path: str, line_no: int) -> str:
    full = _safe_path(path)
    lines = _read_lines(full)
    if line_no < 1 or line_no > len(lines):
        raise ValueError("行番号が不正です")
    return lines[line_no - 1]

def read_line(path: str, line_no: int) -> str:
    full = _safe_path(path)
    lines = _read_lines(full)

    if line_no < 1 or line_no > len(lines):
        raise ValueError("指定された行番号が範囲外です。")

    return lines[line_no - 1]


def delete_line(path: str, line_no: int) -> str:
    full = _safe_path(path)
    lines = _read_lines(full)

    if line_no < 1 or line_no > len(lines):
        raise ValueError("指定された行番号が範囲外です。")

    deleted = lines.pop(line_no - 1)

    _write_lines(full, lines)

    return f"{path} の {line_no} 行目を削除しました。\n削除内容: {deleted.strip()}"

# ===== 行削除 =====
def list_files(base_dir: str = ".", max_depth: int = 3) -> str:
    """
    開発補助用:
    指定フォルダ以下のファイル一覧を表示する。
    危険なフォルダや一時ファイルは除外する。
    """
    ignore_dirs = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "build",
        "dist",
        "VOICEVOX",
    }

    ignore_suffixes = {
        ".pyc",
        ".pyo",
        ".exe",
        ".dll",
        ".log",
        ".key",
    }

    root = Path(base_dir).resolve()

    if not root.exists():
        return f"フォルダが存在しません: {base_dir}"

    results = []

    hidden_files = {
        "APIkey.txt",
        "sessions.json",
        "personality_state.json",
        "memories.json",
        "feedback.jsonl",
        "eval_logs.jsonl",
        "eval_results.jsonl",
        "sessions_backup_before_v013.json",
    }

    for path in root.rglob("*"):

        if path.name in hidden_files:
            continue

        try:
            relative = path.relative_to(root)
            depth = len(relative.parts)

            if depth > max_depth:
                continue

            if any(part in ignore_dirs for part in relative.parts):
                continue

            if path.is_file() and path.suffix in ignore_suffixes:
                continue

            prefix = "📁" if path.is_dir() else "📄"
            results.append(f"{prefix} {relative.as_posix()}")

        except Exception:
            continue

    if not results:
        return "表示できるファイルがありません。"

    return "\n".join(sorted(results))

def search_text_in_files(
    keyword: str,
    base_dir: str = ".",
    max_results: int = 30,
) -> str:
    from pathlib import Path

    root = Path(base_dir).resolve()

    ignore_dirs = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "build",
        "dist",
        "VOICEVOX",
    }

    results = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if any(part in ignore_dirs for part in path.parts):
            continue

        try:
            text = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if keyword not in text:
                continue

            line_no = 0

            for line in text.splitlines():
                line_no += 1

                if keyword in line:
                    rel = path.relative_to(root)

                    results.append(
                        f"{rel}:{line_no}: {line.strip()}"
                    )

                    if len(results) >= max_results:
                        return "\n".join(results)

        except Exception:
            pass

    if not results:
        return f"検索結果なし: {keyword}"

    return "\n".join(results)

