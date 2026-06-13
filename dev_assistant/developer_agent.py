from dev_assistant.project_reader import build_context
from dev_assistant.openai_advisor import ask_chatgpt_advisor
from dev_assistant.dev_mode import DevMode, describe_dev_mode
from dev_assistant.archive_manager import read_archive
from dev_assistant.pending_archive import save_pending_update
from dev_assistant.git_tools import get_git_status, get_git_diff
from dev_assistant.patch_parser import parse_patch_response
from dev_assistant.pending_patch import save_pending_patch, load_pending_patch
from dev_assistant.file_selector import select_related_files
from dev_assistant.patch_scorer import score_patch
from dev_assistant.improvement_store import (
    clear_pending_improvement,
    load_pending_improvement,
    save_pending_improvement,
)
from dev_assistant.autonomous_planner import (
    build_autonomous_plan,
    build_developer_instruction_from_plan,
)
from dev_assistant.autonomous_history import (
    render_recent_autonomous_history,
    save_autonomous_history,
    is_similar_autonomous_work,
)
from app_settings import get_autonomous_level

DEFAULT_RELATED_FILES = [
    "llm_client.py",
    "llm/router.py",
    "llm/models.py",
    "llm/ollama_backend.py",
    "llm/openai_backend.py",
    "main.py",
]


def ask_developer_agent(
    instruction: str,
    related_files: list[str] | None = None,
    mode: DevMode = DevMode.REPAIR,
) -> str:
    files = related_files or select_related_files(instruction)

    archive_text = read_archive()
    git_status = get_git_status()
    git_diff = get_git_diff()
    project_context = build_context(files)
    
    context = (
        "===== DEVELOPMENT ARCHIVE =====\n"
        f"{archive_text}\n\n"
        "===== GIT STATUS =====\n"
        f"{git_status}\n\n"
        "===== GIT DIFF =====\n"
        f"{git_diff}\n\n"
        "===== PROJECT FILES =====\n"
        f"{project_context}"
    )

    mode_text = describe_dev_mode(mode)

    return ask_chatgpt_advisor(
        instruction=(
            f"開発モード: {mode.value}\n"
            f"モード説明: {mode_text}\n\n"
            f"依頼内容:\n{instruction}"
        ),
        context=context,
    )
def propose_archive_update(
    completed_work: str,
) -> str:
    archive_text = read_archive()

    proposal = ask_chatgpt_advisor(
        instruction=(
            "以下の完了作業をもとに、"
            "docs/development_archive.md に追記すべき内容を作成してください。\n\n"
            "条件:\n"
            "- 実装済み内容だけを書く\n"
            "- 未確認の内容は書かない\n"
            "- 不採用にした方針があれば分けて書く\n"
            "- Markdown形式で出力する\n"
            "- そのまま追記できる形にする\n\n"
            f"完了作業:\n{completed_work}"
        ),
        context=(
            "===== CURRENT DEVELOPMENT ARCHIVE =====\n"
            f"{archive_text}"
        ),
    )

    save_pending_update(proposal)

    return proposal

def propose_pending_patch(
    instruction: str,
    related_files: list[str] | None = None,
    mode: DevMode = DevMode.FEATURE,
) -> str:
    response = ask_developer_agent(
        instruction=instruction,
        related_files=related_files,
        mode=mode,
    )

    patch = parse_patch_response(response)

    if patch is None:
        return (
            "変更案の解析に失敗しました。\n\n"
            "Developer Agentの出力に以下が含まれているか確認してください。\n"
            "- 変更対象ファイル\n"
            "- 変更目的\n"
            "- 変更前コード\n"
            "- 変更後コード\n\n"
            "===== Developer Agent response =====\n"
            f"{response}"
        )

    save_pending_patch(patch)

    score = score_patch(
        purpose=patch.purpose,
        before_code=patch.before_code,
        after_code=patch.after_code,
    )

    return (
        "変更案を pending_patch.json に保存しました。\n\n"
        f"対象ファイル: {patch.target_file}\n"
        f"目的: {patch.purpose}\n\n"
        "===== patch score =====\n"
        f"{score.render()}\n\n"
        "チャット欄で「変更案確認」と入力して確認できます。"
    )

def propose_autonomous_development(
    goal: str,
) -> str:
    level = get_autonomous_level()
    recent_history = render_recent_autonomous_history()

    plan = build_autonomous_plan(
        f"{goal}\n\nRecent autonomous history:\n{recent_history}"
    )

    if level <= 1:
        return (
            f"{plan.render()}\n\n"
            "===== autonomous level =====\n"
            "Level 1: plan only. pending_patch was not created."
        )

    instruction = build_developer_instruction_from_plan(plan)

    result = propose_pending_patch(
        instruction=instruction,
        related_files=plan.related_files,
        mode=DevMode.FEATURE,
    )

    duplicate_warning = ""

    try:
        patch = load_pending_patch()

        if is_similar_autonomous_work(
            goal=goal,
            target_file=patch.target_file,
            purpose=patch.purpose,
        ):
            duplicate_warning = (
                "===== duplicate warning =====\n"
                "Similar autonomous development work was found in recent history.\n"
                "Please check carefully before approving this patch.\n\n"
            )

        save_autonomous_history(
            goal=goal,
            selected_strategy=plan.selected_strategy,
            related_files=plan.related_files,
            target_file=patch.target_file,
            purpose=patch.purpose,
        )
    except Exception:
        pass

    pending_patch_preview = ""

    if level >= 3:
        try:
            patch = load_pending_patch()
            pending_patch_preview = (
                "\n\n"
                "===== pending patch preview =====\n"
                f"対象ファイル: {patch.target_file}\n\n"
                f"目的: {patch.purpose}\n\n"
                "----- 変更前 -----\n"
                f"{patch.before_code}\n\n"
                "----- 変更後 -----\n"
                f"{patch.after_code}"
            )
        except Exception as e:
            pending_patch_preview = (
                "\n\n"
                "===== pending patch preview =====\n"
                f"Failed to load pending patch: {type(e).__name__}: {e}"
            )

    return (
        f"{plan.render()}\n\n"
        "===== autonomous level =====\n"
        f"Level {level}\n\n"
        "===== recent autonomous history =====\n"
        f"{recent_history}\n\n"
        f"{duplicate_warning}"
        "===== autonomous patch proposal =====\n"
        f"{result}"
        f"{pending_patch_preview}"
    )

def normalize_improvement_text(
    text: str,
) -> str:
    return (
        text.replace("1. 変更対象ファイル", "変更対象ファイル")
        .replace("2. 変更目的", "変更目的")
        .replace("3. 変更前コード", "変更前コード")
        .replace("4. 変更後コード", "変更後コード")
        .replace("5. 動作確認コマンド", "動作確認コマンド")
        .replace("6. 注意点", "注意点")
    )

def reflect_improvement_to_pending_patch(
    improvement_text: str,
) -> str:
    normalized_text = normalize_improvement_text(
        improvement_text
    )

    patch = parse_patch_response(
        normalized_text
    )

    if patch is None:
        return (
            "改善案の解析に失敗しました。\n\n"
            "以下の形式が含まれているか確認してください。\n"
            "- 変更対象ファイル\n"
            "- 変更目的\n"
            "- 変更前コード\n"
            "- 変更後コード\n\n"
            "===== normalized improvement text head =====\n"
            f"{normalized_text[:1000]}"
        )

    save_pending_patch(patch)

    score = score_patch(
        purpose=patch.purpose,
        before_code=patch.before_code,
        after_code=patch.after_code,
    )

    return (
        "改善案を pending_patch.json に反映しました。\n\n"
        f"対象ファイル: {patch.target_file}\n"
        f"目的: {patch.purpose}\n\n"
        "===== patch score =====\n"
        f"{score.render()}\n\n"
        "次に「変更案確認」→「変更承認」で適用できます。"
    )

def save_improvement_text(
    improvement_text: str,
) -> str:
    if not improvement_text.strip():
        return "保存する改善案の内容が空です。"

    save_pending_improvement(improvement_text)

    return (
        "改善案を保存しました。\n\n"
        "次に「改善案反映」と入力すると、"
        "保存済みの改善案を pending_patch.json に反映します。"
    )


def reflect_saved_improvement_to_pending_patch() -> str:
    improvement_text = load_pending_improvement()

    result = reflect_improvement_to_pending_patch(
        improvement_text
    )

    clear_pending_improvement()

    return result