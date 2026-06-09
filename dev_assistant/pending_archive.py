from pathlib import Path


PENDING_ARCHIVE_FILE = Path(
    "docs/pending_archive_update.md"
)


def save_pending_update(text: str) -> None:
    PENDING_ARCHIVE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    PENDING_ARCHIVE_FILE.write_text(
        text,
        encoding="utf-8",
    )


def load_pending_update() -> str:
    if not PENDING_ARCHIVE_FILE.exists():
        return ""

    return PENDING_ARCHIVE_FILE.read_text(
        encoding="utf-8",
        errors="replace",
    )


def clear_pending_update() -> None:
    if PENDING_ARCHIVE_FILE.exists():
        PENDING_ARCHIVE_FILE.unlink()