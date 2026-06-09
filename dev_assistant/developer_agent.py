from dev_assistant.project_reader import build_context
from dev_assistant.openai_advisor import ask_chatgpt_advisor
from dev_assistant.dev_mode import DevMode, describe_dev_mode
from dev_assistant.archive_manager import read_archive
from dev_assistant.pending_archive import save_pending_update
from dev_assistant.git_tools import get_git_status, get_git_diff


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
    files = related_files or DEFAULT_RELATED_FILES

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