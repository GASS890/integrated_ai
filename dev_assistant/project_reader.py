from pathlib import Path


DEFAULT_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
}


def read_text_file(path: str, max_chars: int = 12000) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")

    if file_path.is_dir():
        raise IsADirectoryError(f"ディレクトリは読めません: {path}")

    text = file_path.read_text(encoding="utf-8", errors="replace")

    if len(text) > max_chars:
        return text[:max_chars] + "\n\n...省略..."

    return text


def build_context(file_paths: list[str], max_chars_per_file: int = 12000) -> str:
    parts = []

    for path in file_paths:
        text = read_text_file(path, max_chars=max_chars_per_file)
        parts.append(
            f"===== FILE: {path} =====\n{text}"
        )

    return "\n\n".join(parts)