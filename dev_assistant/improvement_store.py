from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMPROVEMENT_PATH = PROJECT_ROOT / "docs" / "pending_improvement.txt"


def save_pending_improvement(text: str) -> None:
    IMPROVEMENT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    IMPROVEMENT_PATH.write_text(
        text,
        encoding="utf-8",
    )


def load_pending_improvement() -> str:
    if not IMPROVEMENT_PATH.exists():
        raise FileNotFoundError(
            f"No pending improvement found: {IMPROVEMENT_PATH}"
        )

    return IMPROVEMENT_PATH.read_text(
        encoding="utf-8",
    )


def has_pending_improvement() -> bool:
    return IMPROVEMENT_PATH.exists()


def clear_pending_improvement() -> None:
    if IMPROVEMENT_PATH.exists():
        IMPROVEMENT_PATH.unlink()