import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dev_assistant.git_tools import (
    get_git_status,
    get_git_diff_for_files,
    commit_all_changes,
    push_to_origin,
    create_git_tag,
    push_git_tag,
    git_tag_exists,
    get_current_commit_hash,
    delete_git_tag,
    suggest_next_version,
)


@dataclass
class ManualPatch:
    target_file: str
    purpose: str
    before_code: str
    after_code: str


def apply_manual_change_plan(plan_text: str) -> str:
    version = parse_version(plan_text)
    patches = parse_manual_change_plan(plan_text)

    backups: list[tuple[str, str]] = []
    target_files = [patch.target_file for patch in patches]
    status_before = get_git_status()

    try:
        _validate_patches(patches)
        backups = _apply_patches_with_backup(patches)

        compile_result = _compile_changed_files(patches)

        if "FAILED" in compile_result:
            _rollback_backups(backups)
            raise RuntimeError(
                "py_compile failed. Changes were rolled back.\n\n"
                + compile_result
            )

    except Exception as e:
        if backups:
            _rollback_backups(backups)

        detail = _build_failure_detail(
            patches=patches,
            backups=backups,
            error=e,
        )

        raise RuntimeError(detail) from e

    diff = get_git_diff_for_files(target_files)

    if git_tag_exists(version):
        suggested = suggest_next_version(version)
        raise ValueError(
            f"指定されたバージョンタグは既に存在します: {version}\n"
            f"代替候補: {suggested}"
        )

    commit_message = f"{version}: " + " / ".join(
        patch.purpose for patch in patches
    )

    commit_result = commit_all_changes(commit_message)

    if "failed" in commit_result.lower():
        raise RuntimeError(
            "Git commit failed. GitHub upload was stopped.\n\n"
            + commit_result
        )

    commit_hash = get_current_commit_hash()

    tag_result = create_git_tag(version)

    if "failed" in tag_result.lower() or "already exists" in tag_result.lower():
        raise RuntimeError(
            "Git tag creation failed. GitHub upload was stopped.\n\n"
            + tag_result
        )

    push_result = push_to_origin()

    if "failed" in push_result.lower():
        tag_delete_result = delete_git_tag(version)

        raise RuntimeError(
            "Git push failed. Tag push was stopped.\n\n"
            + push_result
            + "\n\n===== Local Tag Cleanup =====\n"
            + tag_delete_result
        )

    tag_push_result = push_git_tag(version)

    if "failed" in tag_push_result.lower():
        raise RuntimeError(
            "Git tag push failed.\n\n"
            + tag_push_result
        )

    history_path = _save_change_history(
        version=version,
        commit_hash=commit_hash,
        patches=patches,
        compile_result=compile_result,
        commit_result=commit_result,
        tag_result=tag_result,
        push_result=push_result,
        tag_push_result=tag_push_result,
        status_before=status_before,
        diff=diff,
    )

    release_note_path = _save_release_note(
        version=version,
        commit_hash=commit_hash,
        patches=patches,
        compile_result=compile_result,
        diff=diff,
    )

    return (
        "手動改善案を適用し、GitHubへアップロードしました。\n\n"
        "===== Git Status Before =====\n"
        f"{status_before or '(clean)'}\n\n"
        "===== 適用・動作確認結果 =====\n"
        f"{compile_result}\n\n"
        "===== Git Diff Target Files Only =====\n"
        f"{diff}\n\n"
        "===== Git Commit =====\n"
        f"{commit_result}\n\n"
        "===== Git Tag =====\n"
        f"{tag_result}\n\n"
        "===== Git Push =====\n"
        f"{push_result}\n\n"
        "===== Git Tag Push =====\n"
        f"{tag_push_result}\n\n"
        "===== Change History =====\n"
        f"{history_path}\n\n"
        "===== Release Note =====\n"
        f"{release_note_path}"
    )


def parse_version(plan_text: str) -> str:
    version = _extract_section(
        plan_text,
        "6. バージョン",
        "7. 備考",
        allow_missing_end=True,
    ).strip()

    if not version:
        raise ValueError("6. バージョン が指定されていません。")

    return version


def parse_manual_change_plan(plan_text: str) -> list[ManualPatch]:
    patch_blocks = _split_patch_blocks(plan_text)
    patches = []

    for block in patch_blocks:
        target_file = _extract_section(
            block,
            "1. 変更対象ファイル",
            "2. 変更目的",
        ).strip()

        purpose = _extract_section(
            block,
            "2. 変更目的",
            "3. 変更前コード",
        ).strip()

        before_code = _clean_code_block(
            _extract_section(
                block,
                "3. 変更前コード",
                "4. 変更後コード",
            )
        )

        after_code = _clean_code_block(
            _extract_section(
                block,
                "4. 変更後コード",
                "5. 動作確認",
                allow_missing_end=True,
            )
        )

        patches.append(
            ManualPatch(
                target_file=target_file,
                purpose=purpose,
                before_code=before_code,
                after_code=after_code,
            )
        )

    return patches


def restore_from_change_history(version: str) -> str:
    history_dir = Path("docs/change_history")

    if not history_dir.exists():
        raise FileNotFoundError("変更履歴ディレクトリがありません。")

    matches = sorted(history_dir.glob(f"*_{version}.json"))

    if not matches:
        raise FileNotFoundError(
            f"指定バージョンの変更履歴が見つかりません: {version}"
        )

    history_path = matches[-1]

    data = json.loads(
        history_path.read_text(encoding="utf-8")
    )

    patches = data.get("patches", [])

    if not patches:
        raise ValueError(
            f"変更履歴にpatch情報がありません: {history_path}"
        )

    restored = []

    for patch in patches:
        target_file = patch.get("target_file")

        if not target_file:
            continue

        safe_name = target_file.replace("/", "__").replace("\\", "__")
        backups = sorted(
            Path("docs/backups").glob(f"*__{safe_name}.bak")
        )

        if not backups:
            raise FileNotFoundError(
                f"バックアップが見つかりません: {target_file}"
            )

        latest_backup = backups[-1]
        shutil.copy2(latest_backup, target_file)
        restored.append(f"{target_file} <- {latest_backup}")

    compile_result = _compile_changed_files(
        [
            ManualPatch(
                target_file=item.get("target_file"),
                purpose=item.get("purpose", ""),
                before_code="",
                after_code="",
            )
            for item in patches
            if item.get("target_file")
        ]
    )

    return (
        f"{version} の変更履歴から復元しました。\n\n"
        "===== Restored Files =====\n"
        + "\n".join(restored)
        + "\n\n===== py_compile result =====\n"
        + compile_result
    )


def _split_patch_blocks(plan_text: str) -> list[str]:
    blocks = re.split(
        r"\n-{3,}\n|変更ブロック\s*\d+[:：]",
        plan_text,
    )

    result = [
        block.strip()
        for block in blocks
        if "1. 変更対象ファイル" in block
    ]

    if not result:
        raise ValueError("変更ブロックが見つかりません。")

    return result


def _extract_section(
    text: str,
    start: str,
    end: str,
    allow_missing_end: bool = False,
) -> str:
    if start not in text:
        raise ValueError(f"開始見出しが見つかりません: {start}")

    body = text.split(start, 1)[1]

    if end not in body:
        if allow_missing_end:
            return body
        raise ValueError(f"終了見出しが見つかりません: {end}")

    return body.split(end, 1)[0]


def _clean_code_block(text: str) -> str:
    text = text.strip()

    text = re.sub(r"^```[a-zA-Z0-9_+-]*\n", "", text)
    text = re.sub(r"\n```$", "", text)

    return text.strip()


def _validate_patches(patches: list[ManualPatch]) -> None:
    for patch in patches:
        path = Path(patch.target_file)

        if not path.exists():
            raise FileNotFoundError(
                f"対象ファイルが存在しません: {patch.target_file}"
            )

        current = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if patch.before_code not in current:
            raise ValueError(
                f"変更前コードが現在ファイルと一致しません: {patch.target_file}"
            )

        if patch.before_code.strip() == patch.after_code.strip():
            raise ValueError(
                f"変更前コードと変更後コードが同一です: {patch.target_file}"
            )


def _apply_patches_with_backup(
    patches: list[ManualPatch],
) -> list[tuple[str, str]]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("docs/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    backups = []

    for patch in patches:
        target = Path(patch.target_file)

        safe_name = patch.target_file.replace("\\", "__").replace("/", "__")
        backup_path = backup_dir / f"{timestamp}__{safe_name}.bak"

        shutil.copy2(target, backup_path)
        backups.append((patch.target_file, str(backup_path)))

        current = target.read_text(
            encoding="utf-8",
            errors="replace",
        )

        updated = current.replace(
            patch.before_code,
            patch.after_code,
            1,
        )

        target.write_text(
            updated,
            encoding="utf-8",
        )

    return backups


def _rollback_backups(backups: list[tuple[str, str]]) -> None:
    for target_file, backup_path in reversed(backups):
        shutil.copy2(backup_path, target_file)


def _compile_changed_files(patches: list[ManualPatch]) -> str:
    results = []

    for patch in patches:
        if not patch.target_file.endswith(".py"):
            results.append(f"SKIP: {patch.target_file}")
            continue

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                patch.target_file,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode == 0:
            results.append(f"OK: {patch.target_file}")
        else:
            results.append(
                f"FAILED: {patch.target_file}\n"
                f"{result.stderr or result.stdout}"
            )

    return "\n".join(results)


def _build_failure_detail(
    patches: list[ManualPatch],
    backups: list[tuple[str, str]],
    error: Exception,
) -> str:
    lines = [
        "手動改善案の適用に失敗しました。",
        "",
        "===== Error =====",
        f"{type(error).__name__}: {error}",
        "",
        "===== Target Files =====",
    ]

    for patch in patches:
        lines.append(f"- {patch.target_file}: {patch.purpose}")

    lines.extend(
        [
            "",
            "===== Rollback =====",
        ]
    )

    if backups:
        lines.append("ロールバックを実行しました。")
        for target_file, backup_path in backups:
            lines.append(f"- {target_file} <- {backup_path}")
    else:
        lines.append("変更適用前に失敗したため、ロールバック対象はありません。")

    return "\n".join(lines)


def _save_change_history(
    version: str,
    commit_hash: str,
    patches: list[ManualPatch],
    compile_result: str,
    commit_result: str,
    tag_result: str,
    push_result: str,
    tag_push_result: str,
    status_before: str,
    diff: str,
) -> str:
    history_dir = Path("docs/change_history")
    history_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = history_dir / f"{timestamp}_{version}.json"

    data = {
        "version": version,
        "commit_hash": commit_hash,
        "created_at": timestamp,
        "status_before": status_before,
        "patches": [
            {
                "target_file": patch.target_file,
                "purpose": patch.purpose,
            }
            for patch in patches
        ],
        "compile_result": compile_result,
        "diff": diff,
        "commit_result": commit_result,
        "tag_result": tag_result,
        "push_result": push_result,
        "tag_push_result": tag_push_result,
    }

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return str(path)


def _save_release_note(
    version: str,
    commit_hash: str,
    patches: list[ManualPatch],
    compile_result: str,
    diff: str,
) -> str:
    release_dir = Path("docs/releases")
    release_dir.mkdir(parents=True, exist_ok=True)

    path = release_dir / f"{version}.md"

    lines = [
        f"# {version}",
        "",
        f"- Commit: {commit_hash}",
        "",
        "## Summary",
        "",
        f"- Changed files: {len(patches)}",
        "- Applied by manual improvement flow",
        "",
        "## Changed Files",
        "",
    ]

    for patch in patches:
        lines.append(f"### {patch.target_file}")
        lines.append("")
        lines.append(f"- Purpose: {patch.purpose}")
        lines.append("")

    lines.extend(
        [
            "## Verification",
            "",
            "```text",
            compile_result,
            "```",
            "",
            "## Diff",
            "",
            "```diff",
            diff,
            "```",
            "",
            "## Rollback",
            "",
            "- Backups are stored under `docs/backups/`.",
            "- Change history is stored under `docs/change_history/`.",
            "",
        ]
    )

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return str(path)