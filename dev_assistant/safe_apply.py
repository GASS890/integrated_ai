from __future__ import annotations

from pathlib import Path

from dev_assistant.backup_manager import create_backup
from dev_assistant.pending_patch import clear_pending_patch, load_pending_patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def apply_pending_patch() -> str:
    patch = load_pending_patch()

    target_path = PROJECT_ROOT / patch.target_file

    if not target_path.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")

    current_text = target_path.read_text(encoding="utf-8")

    if patch.before_code not in current_text:
        raise ValueError(
            "Before code does not match current file content. "
            "Patch was not applied for safety."
        )

    backup_path = create_backup(patch.target_file)

    new_text = current_text.replace(patch.before_code, patch.after_code, 1)
    target_path.write_text(new_text, encoding="utf-8")

    clear_pending_patch()

    return (
        "Patch applied successfully.\n"
        f"Target file: {patch.target_file}\n"
        f"Backup: {backup_path}"
    )