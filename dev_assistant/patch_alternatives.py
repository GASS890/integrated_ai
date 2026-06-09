from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PatchAlternative:
    name: str
    strategy: str
    instruction_suffix: str
    priority: int

    def render(self) -> str:
        return (
            f"{self.name}\n"
            f"- Strategy: {self.strategy}\n"
            f"- Priority: {self.priority}/10"
        )


def generate_patch_alternatives(
    goal: str,
) -> list[PatchAlternative]:
    alternatives = [
        PatchAlternative(
            name="案A: 最小変更",
            strategy=(
                "既存構造をできるだけ維持し、"
                "影響範囲を最小にして目的へ近づける。"
            ),
            instruction_suffix=(
                "最小変更を優先してください。"
                "新規ファイル追加や大規模リファクタは避けてください。"
            ),
            priority=9,
        ),
        PatchAlternative(
            name="案B: 保守性重視",
            strategy=(
                "多少の構造整理を許可し、"
                "今後の拡張や読みやすさを重視する。"
            ),
            instruction_suffix=(
                "保守性を重視してください。"
            ),
            priority=8,
        ),
        PatchAlternative(
            name="案C: 安全性重視",
            strategy=(
                "例外処理、確認手順、ロールバック可能性を重視し、"
                "危険な変更を避ける。"
            ),
            instruction_suffix=(
                "安全性を最優先してください。"
                "失敗時の影響を小さくし、承認前に確認しやすい変更にしてください。"
            ),
            priority=8,
        ),
    ]

    if _contains_any(goal, ["ui", "画面", "表示", "ボタン", "設定画面"]):
        alternatives.append(
            PatchAlternative(
                name="案D: UI整合性重視",
                strategy=(
                    "UI表示とAPIレスポンスの整合性を重視し、"
                    "画面側とサーバー側のズレを避ける。"
                ),
                instruction_suffix=(
                    "UIとAPIの整合性を重視してください。"
                    "表示だけでなく関連するAPI応答も確認してください。"
                ),
                priority=7,
            )
        )

    if _contains_any(goal, ["人格", "性格", "親密度", "mood", "affinity"]):
        alternatives.append(
            PatchAlternative(
                name="案E: 人格安定性重視",
                strategy=(
                    "人格、親密度、気分の一貫性を重視し、"
                    "プロンプトと状態管理の破綻を避ける。"
                ),
                instruction_suffix=(
                    "人格の一貫性を重視してください。"
                    "affinity、mood、personality_promptの関係を壊さない変更にしてください。"
                ),
                priority=8,
            )
        )

    if _contains_any(goal, ["記憶", "memory", "長期記憶", "思い出す"]):
        alternatives.append(
            PatchAlternative(
                name="案F: 記憶精度重視",
                strategy=(
                    "記憶の保存、検索、プロンプト注入の精度を重視し、"
                    "既存記憶の破損や過剰注入を避ける。"
                ),
                instruction_suffix=(
                    "記憶精度を重視してください。"
                    "memory_store.pyとprompts.pyの流れを壊さない変更にしてください。"
                ),
                priority=8,
            )
        )

    if _contains_any(goal, ["developer", "開発", "変更提案", "変更承認", "自律開発"]):
        alternatives.append(
            PatchAlternative(
                name="案G: 開発安全性重視",
                strategy=(
                    "提案、承認、適用、検証、レビューの流れを維持し、"
                    "承認なしの実ファイル変更を避ける。"
                ),
                instruction_suffix=(
                    "開発安全性を重視してください。"
                    "承認なしで実ファイルを変更しないフローを維持してください。"
                ),
                priority=9,
            )
        )

    return _sort_and_limit(alternatives)


def choose_best_alternative(
    alternatives: list[PatchAlternative],
) -> PatchAlternative:
    if not alternatives:
        raise ValueError("No patch alternatives were generated.")

    return sorted(
        alternatives,
        key=lambda item: item.priority,
        reverse=True,
    )[0]


def render_alternatives(
    alternatives: list[PatchAlternative],
) -> str:
    if not alternatives:
        return "No patch alternatives."

    return "\n\n".join(
        alternative.render()
        for alternative in alternatives
    )


def _sort_and_limit(
    alternatives: list[PatchAlternative],
    limit: int = 4,
) -> list[PatchAlternative]:
    return sorted(
        alternatives,
        key=lambda item: item.priority,
        reverse=True,
    )[:limit]


def _contains_any(
    text: str,
    keywords: list[str],
) -> bool:
    lowered = text.lower()

    return any(
        keyword.lower() in lowered
        for keyword in keywords
    )