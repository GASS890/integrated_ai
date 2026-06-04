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
def read_file(path: str, max_chars: int = 8000) -> str:
    full = _safe_path(path)
    text = "".join(_read_lines(full))

    if len(text) > max_chars:
        return (
            text[:max_chars]
            + "\n\n...省略...\n"
            + f"全文は {len(text)} 文字あります。"
        )

    return text

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
                errors="ignore",
            )

            if keyword not in text:
                continue

            for line_no, line in enumerate(text.splitlines(), start=1):
                if keyword in line:
                    rel = path.relative_to(root)
                    results.append(f"{rel}:{line_no}: {line.strip()}")

                    if len(results) >= max_results:
                        return "\n".join(results)

        except Exception:
            continue

    if not results:
        return f"検索結果なし: {keyword}"

    return "\n".join(results)


def search_function(function_name: str) -> str:
    """
    def 関数名 を検索する。
    """
    keyword = f"def {function_name}"

    return search_text_in_files(
        keyword,
        max_results=20,
    )

def search_function(function_name: str) -> str:
    """
    def 関数名 を検索する。
    """
    keyword = f"def {function_name}"

    return search_text_in_files(
        keyword,
        max_results=20,
    )


def search_import(keyword: str) -> str:
    """
    import 文を検索する。
    例:
    - import personality
    - import update_personality
    - import call_ollama_chat
    """

    patterns = [
        f"import {keyword}",
        f"from {keyword}",
        keyword,
    ]

    results = []

    for pattern in patterns:
        found = search_text_in_files(
            pattern,
            max_results=20,
        )

        if not found.startswith("検索結果なし"):
            results.append(f"【pattern: {pattern}】\n{found}")

    if not results:
        return f"import検索結果なし: {keyword}"

    return "\n\n".join(results)

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

def show_change_candidate(keyword: str, context_lines: int = 8) -> str:
    """
    変更候補の周辺コードを表示する。
    ファイルは変更しない。
    """

    root = Path(".").resolve()

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
            lines = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()

            for i, line in enumerate(lines):
                if keyword in line:
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)

                    rel = path.relative_to(root)

                    block = [
                        f"【候補】{rel}:{i + 1}",
                        "```python",
                    ]

                    for n in range(start, end):
                        block.append(f"{n + 1}: {lines[n]}")

                    block.append("```")
                    results.append("\n".join(block))

                    if len(results) >= 5:
                        return "\n\n".join(results)

        except Exception:
            continue

    if not results:
        return f"変更候補なし: {keyword}"

    return "\n\n".join(results)

def replace_text_in_file(path: str, old_text: str, new_text: str) -> str:
    """
    Replace old_text with new_text in a file.
    A backup file is created before writing.
    """

    if isinstance(path, str) and path.startswith("workspace/"):
        path = path.replace("workspace/", "", 1)

    full = _safe_path(path)

    text = Path(full).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if old_text not in text:
        return "置換対象の変更前コードが見つかりません。"

    backup_path = str(full) + ".bak"

    Path(backup_path).write_text(
        text,
        encoding="utf-8",
    )

    new_file_text = text.replace(old_text, new_text, 1)

    Path(full).write_text(
        new_file_text,
        encoding="utf-8",
    )

    return f"{path} を置換しました。バックアップ: {backup_path}"


def preview_replace_plan(plan_path: str) -> str:
    """
    Preview a JSON replace plan.
    """

    import json

    if isinstance(plan_path, str) and plan_path.startswith("workspace/"):
        plan_path = plan_path.replace("workspace/", "", 1)

    full_plan_path = _safe_path(plan_path)

    plan_text = Path(full_plan_path).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    plan = json.loads(plan_text)

    path = plan.get("path")
    old_text = plan.get("old_text")
    new_text = plan.get("new_text")

    if not path or old_text is None or new_text is None:
        return "置換指示ファイルの形式が不正です。path / old_text / new_text が必要です。"

    return (
        "置換プレビュー\n\n"
        f"対象ファイル:\n{path}\n\n"
        f"変更前:\n```text\n{old_text}\n```\n\n"
        f"変更後:\n```text\n{new_text}\n```"
    )


def replace_text_from_plan(plan_path: str) -> str:
    """
    Execute a JSON replace plan.
    """

    import json

    if isinstance(plan_path, str) and plan_path.startswith("workspace/"):
        plan_path = plan_path.replace("workspace/", "", 1)

    full_plan_path = _safe_path(plan_path)

    plan_text = Path(full_plan_path).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    plan = json.loads(plan_text)

    path = plan.get("path")
    old_text = plan.get("old_text")
    new_text = plan.get("new_text")

    if not path or old_text is None or new_text is None:
        return "置換指示ファイルの形式が不正です。path / old_text / new_text が必要です。"

    return replace_text_in_file(
        path=path,
        old_text=old_text,
        new_text=new_text,
    )


def replace_text_from_plan(plan_path: str) -> str:
    """
    Execute a JSON replace plan.
    """

    import json

    if isinstance(plan_path, str) and plan_path.startswith("workspace/"):
        plan_path = plan_path.replace("workspace/", "", 1)

    full_plan_path = _safe_path(plan_path)

    plan_text = Path(full_plan_path).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    plan = json.loads(plan_text)

    path = plan.get("path")
    old_text = plan.get("old_text")
    new_text = plan.get("new_text")

    if not path or old_text is None or new_text is None:
        return "置換指示ファイルの形式が不正です。path / old_text / new_text が必要です。"

    return replace_text_in_file(
        path=path,
        old_text=old_text,
        new_text=new_text,
    )


def py_compile_file(path: str) -> str:
    """
    Pythonファイルの構文チェックを実行する。
    """

    import subprocess
    import sys

    if isinstance(path, str) and path.startswith("workspace/"):
        path = path.replace("workspace/", "", 1)

    full = Path(path)

    if not full.exists():
        return f"ファイルが存在しません: {path}"

    if full.suffix != ".py":
        return f"Pythonファイルではありません: {path}"

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(full)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    if result.returncode == 0:
        return f"構文チェックOK: {path}"

    return (
        f"構文チェックNG: {path}\n\n"
        f"STDOUT:\n{result.stdout}\n\n"
        f"STDERR:\n{result.stderr}"
    )

def restore_backup(path: str) -> str:
    """
    .bak を復元する。
    """

    if isinstance(path, str) and path.startswith("workspace/"):
        path = path.replace("workspace/", "", 1)

    full = _safe_path(path)

    backup = str(full) + ".bak"

    if not Path(backup).exists():
        return f"バックアップが存在しません: {backup}"

    original_text = Path(backup).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    Path(full).write_text(
        original_text,
        encoding="utf-8",
    )

    return f"復元完了: {path}"