# file_ops.py
import os

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

# ===== 行削除 =====
def delete_line(path: str, line_no: int) -> str:
    full = _safe_path(path)
    lines = _read_lines(full)
    if line_no < 1 or line_no > len(lines):
        raise ValueError("行番号が不正です")

    del lines[line_no - 1]
    lines = _renumber(lines)
    _write_lines(full, lines)

    return f"{line_no}行目を削除しました"