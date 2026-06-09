from __future__ import annotations


DEFAULT_FILES = [
    "main.py",
    "llm_client.py",
    "app_settings.py",
]


RULES = [
    {
        "keywords": [
            "ui",
            "画面",
            "表示",
            "ボタン",
            "チャット欄",
            "設定画面",
            "フロント",
        ],
        "files": [
            "static/index.html",
            "main.py",
        ],
    },
    {
        "keywords": [
            "人格",
            "性格",
            "親密度",
            "好感度",
            "態度",
            "気分",
            "mood",
            "affinity",
            "personality",
        ],
        "files": [
            "personality/types.py",
            "personality/state_manager.py",
            "personality/affinity.py",
            "personality/mood.py",
            "personality/attitude_analysis.py",
            "personality/personality_prompt.py",
            "main.py",
        ],
    },
    {
        "keywords": [
            "記憶",
            "メモリ",
            "memory",
            "長期記憶",
            "保存",
            "思い出す",
        ],
        "files": [
            "memory_store.py",
            "prompts.py",
            "main.py",
        ],
    },
    {
        "keywords": [
            "openai",
            "chatgpt",
            "api",
            "gpt",
        ],
        "files": [
            "openai_client.py",
            "llm/openai_backend.py",
            "llm/router.py",
            "llm_client.py",
            "app_settings.py",
        ],
    },
    {
        "keywords": [
            "ollama",
            "ローカルモデル",
            "qwen",
            "gemma",
            "llm",
            "モデル",
        ],
        "files": [
            "ollama_client.py",
            "llm/ollama_backend.py",
            "llm/router.py",
            "llm/models.py",
            "llm_client.py",
        ],
    },
    {
        "keywords": [
            "ファイル操作",
            "workspace",
            "保存",
            "追記",
            "読み込み",
            "削除",
        ],
        "files": [
            "file_ops.py",
            "main.py",
        ],
    },
    {
        "keywords": [
            "developer agent",
            "開発",
            "変更提案",
            "変更案",
            "変更承認",
            "safe_apply",
            "rollback",
            "ロールバック",
            "レビュー",
            "commit",
            "push",
        ],
        "files": [
            "dev_assistant/developer_agent.py",
            "dev_assistant/project_reader.py",
            "dev_assistant/pending_patch.py",
            "dev_assistant/patch_parser.py",
            "dev_assistant/safe_apply.py",
            "dev_assistant/backup_manager.py",
            "dev_assistant/code_reviewer.py",
            "dev_assistant/git_tools.py",
            "dev_assistant/commit_message_generator.py",
            "app_settings.py",
            "main.py",
        ],
    },
    {
        "keywords": [
            "アーカイブ",
            "development_archive",
            "pending_archive",
            "履歴",
        ],
        "files": [
            "dev_assistant/archive_manager.py",
            "dev_assistant/pending_archive.py",
            "docs/development_archive.md",
            "main.py",
        ],
    },
    {
        "keywords": [
            "音声",
            "voice",
            "voicevox",
            "読み上げ",
        ],
        "files": [
            "voicevox_client.py",
            "main.py",
        ],
    },
    {
        "keywords": [
            "設定",
            "settings",
            "app_settings",
            "on/off",
            "切替",
        ],
        "files": [
            "app_settings.py",
            "main.py",
            "static/index.html",
        ],
    },
]


def select_related_files(
    instruction: str,
    limit: int = 12,
) -> list[str]:
    text = instruction.lower()
    selected: list[str] = []

    for file_path in DEFAULT_FILES:
        _add_unique(selected, file_path)

    for rule in RULES:
        if _matches_any(text, rule["keywords"]):
            for file_path in rule["files"]:
                _add_unique(selected, file_path)

    return selected[:limit]


def _matches_any(
    text: str,
    keywords: list[str],
) -> bool:
    return any(
        keyword.lower() in text
        for keyword in keywords
    )


def _add_unique(
    items: list[str],
    item: str,
) -> None:
    if item not in items:
        items.append(item)