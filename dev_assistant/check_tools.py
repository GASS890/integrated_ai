import py_compile
from pathlib import Path


IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "build",
    "dist",
    "venv",
    ".venv",
}


def should_skip(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def py_compile_all(base_dir: str = ".") -> str:
    results = []

    for path in Path(base_dir).rglob("*.py"):
        if should_skip(path):
            continue

        try:
            py_compile.compile(
                str(path),
                doraise=True,
            )
            results.append(f"OK: {path}")
        except Exception as e:
            results.append(f"NG: {path}\n{e}")

    return "\n".join(results)