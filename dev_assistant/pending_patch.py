from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PENDING_PATCH_PATH = PROJECT_ROOT / "docs" / "pending_patch.json"


@dataclass
class PendingPatch:
    target_file: str
    purpose: str
    before_code: str
    after_code: str
    created_by: str = "developer_agent"


def save_pending_patch(patch: PendingPatch) -> Path:
    PENDING_PATCH_PATH.parent.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any] = asdict(patch)

    PENDING_PATCH_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return PENDING_PATCH_PATH


def load_pending_patch() -> PendingPatch:
    if not PENDING_PATCH_PATH.exists():
        raise FileNotFoundError(
            f"No pending patch found: {PENDING_PATCH_PATH}"
        )

    data = json.loads(PENDING_PATCH_PATH.read_text(encoding="utf-8"))

    return PendingPatch(
        target_file=data["target_file"],
        purpose=data["purpose"],
        before_code=data["before_code"],
        after_code=data["after_code"],
        created_by=data.get("created_by", "developer_agent"),
    )


def clear_pending_patch() -> None:
    if PENDING_PATCH_PATH.exists():
        PENDING_PATCH_PATH.unlink()


def has_pending_patch() -> bool:
    return PENDING_PATCH_PATH.exists()