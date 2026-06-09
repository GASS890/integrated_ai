from __future__ import annotations

from pathlib import Path

from dev_assistant.backup_manager import create_backup, restore_backup
from dev_assistant.check_tools import py_compile_all
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


def rollback_patch(
    backup_path: str | Path,
    target_file: str,
) -> str:
    restored_path = restore_backup(
        backup_path=backup_path,
        target_file=target_file,
    )

    return (
        "Rollback completed.\n"
        f"Target file: {target_file}\n"
        f"Restored path: {restored_path}\n"
        f"Backup used: {backup_path}"
    )


def apply_pending_patch_with_compile_check() -> str:
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

    check_result = py_compile_all()

    if "FAIL" in check_result or "Error" in check_result or "SyntaxError" in check_result:
        rollback_result = rollback_patch(
            backup_path=backup_path,
            target_file=patch.target_file,
        )

        return (
            "Patch applied, but py_compile failed.\n"
            "Rollback was executed automatically.\n\n"
            f"===== py_compile result =====\n{check_result}\n\n"
            f"===== rollback result =====\n{rollback_result}"
        )

    clear_pending_patch()

    return (
        "Patch applied successfully.\n"
        f"Target file: {patch.target_file}\n"
        f"Backup: {backup_path}\n\n"
        f"===== py_compile result =====\n{check_result}"
    )
