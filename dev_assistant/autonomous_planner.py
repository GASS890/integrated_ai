from __future__ import annotations

from dataclasses import dataclass

from dev_assistant.file_selector import select_related_files
from dev_assistant.patch_alternatives import (
    choose_best_alternative,
    generate_patch_alternatives,
    render_alternatives,
)

@dataclass
class AutonomousPlan:
    goal: str
    analysis: str
    proposal: str
    steps: list[str]
    related_files: list[str]
    alternatives_text: str
    selected_strategy: str

    def render(self) -> str:
        return (
            "Autonomous development plan\n\n"
            f"Goal:\n{self.goal}\n\n"
            f"Analysis:\n{self.analysis}\n\n"
            f"Proposal:\n{self.proposal}\n\n"
            f"Alternatives:\n{self.alternatives_text}\n\n"
            f"Selected strategy:\n{self.selected_strategy}\n\n"
            "Steps:\n"
            + "\n".join(f"- {step}" for step in self.steps)
            + "\n\n"
            "Related files:\n"
            + "\n".join(f"- {file_path}" for file_path in self.related_files)
        )

def build_autonomous_plan(goal: str) -> AutonomousPlan:
    related_files = select_related_files(goal)

    alternatives = generate_patch_alternatives(goal)
    best_alternative = choose_best_alternative(alternatives)

    analysis = _build_analysis(goal, related_files)
    proposal = _build_proposal(goal)
    steps = _build_steps(goal)

    return AutonomousPlan(
        goal=goal,
        analysis=analysis,
        proposal=proposal,
        steps=steps,
        related_files=related_files,
        alternatives_text=render_alternatives(alternatives),
        selected_strategy=best_alternative.render(),
    )

def build_developer_instruction_from_plan(plan: AutonomousPlan) -> str:
    return (
        "以下の自律開発計画にもとづいて、変更案を1つ作成してください。\n\n"
        "必ず次の形式で出力してください。\n"
        "- 変更対象ファイル\n"
        "- 変更目的\n"
        "- 変更前コード\n"
        "- 変更後コード\n"
        "- 確認コマンド\n\n"
        "重要条件:\n"
        "- 変更は1ファイル・1箇所に絞る\n"
        "- 既存機能を壊さない\n"
        "- APIキーや個人情報を含めない\n"
        "- 変更前コードは現在のファイル内容と完全一致する範囲にする\n"
        "- 大きすぎる変更は避ける\n\n"
        "採用する方針:\n"
        f"{plan.selected_strategy}\n\n"
        f"{plan.render()}"
    )


def _build_analysis(
    goal: str,
    related_files: list[str],
) -> str:
    if not goal.strip():
        return "開発目標が空です。具体的な改善対象が必要です。"

    if _contains_any(goal, ["人格", "性格", "親密度", "mood", "affinity"]):
        return (
            "人格・親密度・気分に関係する改善です。"
            "状態管理、プロンプト生成、UI表示の連携を壊さないように、"
            "小さな変更から進める必要があります。"
        )

    if _contains_any(goal, ["記憶", "memory", "長期記憶", "思い出す"]):
        return (
            "記憶システムに関係する改善です。"
            "保存、検索、プロンプト注入の流れに影響するため、"
            "既存のmemory_store.pyとprompts.pyの整合性確認が重要です。"
        )

    if _contains_any(goal, ["ui", "画面", "表示", "ボタン", "設定画面"]):
        return (
            "UIまたは設定画面に関係する改善です。"
            "static/index.htmlとmain.pyのAPI側の整合性を確認しながら、"
            "表示変更と設定保存を分けて進める必要があります。"
        )

    if _contains_any(goal, ["developer", "変更提案", "変更承認", "自律開発", "開発"]):
        return (
            "Developer Agentの開発支援機能に関係する改善です。"
            "提案、保存、承認、適用、検証、レビューの安全フローを維持しながら、"
            "新機能を追加する必要があります。"
        )

    if _contains_any(goal, ["openai", "api", "chatgpt", "llm", "ollama"]):
        return (
            "LLM連携に関係する改善です。"
            "backend分離構造を維持し、OpenAI/Ollama固有処理を混在させないことが重要です。"
        )

    return (
        "開発目標に関連するファイルを選定し、影響範囲を小さく保ちながら"
        "安全な単一変更案として進めるのが適切です。"
    )


def _build_proposal(goal: str) -> str:
    if _contains_any(goal, ["自律開発", "自立開発"]):
        return (
            "まずは自律的に計画を作成し、pending_patch保存まで進める機能を追加します。"
            "実ファイル変更は既存の変更承認フローに任せます。"
        )

    if _contains_any(goal, ["設定", "on/off", "切替"]):
        return (
            "設定項目をapp_settings.pyに追加し、main.pyまたはUIから参照できるようにします。"
        )

    if _contains_any(goal, ["レビュー", "スコア", "評価"]):
        return (
            "変更案の評価結果を表示し、危険な変更を承認前に見つけやすくします。"
        )

    return (
        "既存構造に合わせて、最小変更で目的に近づく変更案を作成します。"
    )


def _build_steps(goal: str) -> list[str]:
    base_steps = [
        "関連ファイルを選定する",
        "既存コードの該当箇所を確認する",
        "最小単位の変更案を作成する",
        "変更前コードと変更後コードを提示する",
        "pending_patch.jsonに保存する",
        "ユーザーの変更案確認と変更承認を待つ",
    ]

    if _contains_any(goal, ["自律開発", "自立開発"]):
        return [
            "開発目標を分析する",
            "改善方針を1つに絞る",
            "関連ファイルを選定する",
            "Developer Agent用の具体的な変更依頼に変換する",
            "変更案を生成してpending_patch.jsonに保存する",
            "変更承認までは実ファイルを変更しない",
        ]

    return base_steps


def _contains_any(
    text: str,
    keywords: list[str],
) -> bool:
    lowered = text.lower()

    return any(
        keyword.lower() in lowered
        for keyword in keywords
    )