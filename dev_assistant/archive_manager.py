from pathlib import Path


ARCHIVE_PATH = Path("docs/development_archive.md")


def read_archive() -> str:
    if not ARCHIVE_PATH.exists():
        return ""

    return ARCHIVE_PATH.read_text(
        encoding="utf-8",
        errors="replace",
    )


def append_archive(text: str) -> None:
    ARCHIVE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    current = read_archive()

    if current and not current.endswith("\n"):
        current += "\n"

    ARCHIVE_PATH.write_text(
        current + "\n" + text.strip() + "\n",
        encoding="utf-8",
    )