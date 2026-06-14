from pathlib import Path
from dev_assistant.context_locator import (
    find_import_block,
    find_duplicate_imports,
)

DEFAULT_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
}

MAX_FILE_SIZE = 30000


def read_text_file(path: str, max_chars: int = 12000) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")

    if file_path.is_dir():
        raise IsADirectoryError(f"ディレクトリは読めません: {path}")

    text = file_path.read_text(encoding="utf-8", errors="replace")

    if len(text) > MAX_FILE_SIZE:
        print(
            f"[project_reader] warning: {path} is large "
            f"({len(text)} chars). Only first {max_chars} chars will be used."
        )

    if len(text) > max_chars:
        text = text[:max_chars]

    return text


def build_context(
    file_paths: list[str],
    max_chars_per_file: int = 12000,
    user_request: str = "",
) -> str:
    parts = []

    for path in file_paths:
        is_import_request = (
            "import" in user_request.lower()
            or "インポート" in user_request
        )

        is_duplicate_request = (
            "重複" in user_request
            or "duplicate" in user_request.lower()
        )

        if is_import_request and is_duplicate_request:
            duplicates = find_duplicate_imports(path)

            if duplicates:
                text = (
                    "Duplicate import lines found:\n"
                    + duplicates
                )
            else:
                text = (
                    "No duplicate import lines found.\n"
                    "Do not propose any code change."
                )

        elif is_import_request:
            text = find_import_block(path)

        else:
            text = read_text_file(path, max_chars=max_chars_per_file)

        numbered = "\n".join(
            f"{i + 1}: {line}"
            for i, line in enumerate(text.splitlines())
        )

        parts.append(f"===== FILE: {path} =====\n{numbered}")

    return "\n\n".join(parts)