from dev_assistant.openai_patch_generator import generate_patch_request
from dev_assistant.pending_patch import save_pending_patch
from dev_assistant.safe_apply import apply_pending_patch_with_compile_check
from dev_assistant.git_tools import get_git_status, get_git_diff


def propose_change(user_request: str, file_paths: list[str]) -> str:
    patch = generate_patch_request(user_request, file_paths)

    with open(
        patch.target_file,
        "r",
        encoding="utf-8"
    ) as f:
        current = f.read()

    if patch.before_code not in current:
        raise ValueError(
            "Generated before_code "
            "does not exist in target file."
        )

    if patch.before_code.strip() == patch.after_code.strip():
        raise ValueError(
            "Generated patch has no actual changes."
        )

    before_lines = patch.before_code.splitlines()
    after_lines = patch.after_code.splitlines()

    if len(before_lines) > 100 or len(after_lines) > 120:
        raise ValueError(
            "Generated patch is too large. "
            "Please generate a smaller localized patch."
        )

    if patch.before_code.strip() == patch.after_code.strip():
        raise ValueError(
            "Generated patch has no actual changes."
        )

    save_pending_patch(patch)

    return (
        "変更案を保存しました。\n\n"
        "次にユーザーが承認すると、自動適用＋動作確認を実行します。\n\n"
        "===== 変更概要 =====\n"
        f"{patch.purpose}\n\n"
        "===== 対象ファイル =====\n"
        f"{patch.target_file}\n\n"
        "===== Git Status =====\n"
        f"{get_git_status()}"
    )


def approve_change() -> str:
    apply_result = apply_pending_patch_with_compile_check()
    diff = get_git_diff()

    return (
        "承認された変更を処理しました。\n\n"
        "===== 適用・動作確認結果 =====\n"
        f"{apply_result}\n\n"
        "===== Git Diff =====\n"
        f"{diff}"
    )