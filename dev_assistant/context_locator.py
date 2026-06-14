import re
from pathlib import Path


def find_import_block(path: str) -> str:
    text = Path(path).read_text(
        encoding="utf-8",
        errors="replace"
    )

    lines = text.splitlines()
    result = []
    in_import_area = False

    for line in lines:
        stripped = line.strip()

        if line.startswith("import ") or line.startswith("from "):
            in_import_area = True
            result.append(line)
            continue

        if in_import_area:
            if stripped == "":
                result.append(line)
                continue

            if line.startswith(" ") or line.startswith("\t"):
                result.append(line)
                continue

            break

    return "\n".join(result).strip()


def find_duplicate_imports(path: str) -> str:
    import_block = find_import_block(path)
    lines = import_block.splitlines()

    seen = set()
    duplicates = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if not (
            stripped.startswith("import ")
            or stripped.startswith("from ")
        ):
            continue

        if stripped in seen:
            duplicates.append(line)
        else:
            seen.add(stripped)

    return "\n".join(duplicates)