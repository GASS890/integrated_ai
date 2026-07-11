from personality.user_model import UserModel
from personality.user_model_manager import load_user_model


PREFERENCE_THRESHOLD = 0.65
HIGH_SCORE_THRESHOLD = 0.8


def _score(
    values: dict[str, float],
    key: str,
) -> float:
    return float(values.get(key, 0.0))


def detect_response_preferences(
    model: UserModel | None = None,
) -> dict:
    if model is None:
        model = load_user_model()

    preferred_formats = []
    style_instructions = []
    priority_topics = []
    familiar_topics = []

    if (
        _score(
            model.preferences,
            "PowerShell形式",
        )
        >= PREFERENCE_THRESHOLD
    ):
        preferred_formats.append("PowerShell")

    if (
        _score(
            model.preferences,
            "コード全文",
        )
        >= PREFERENCE_THRESHOLD
    ):
        style_instructions.append(
            "実行可能なコードは省略せず提示する"
        )

    if (
        _score(
            model.preferences,
            "手順を細かく",
        )
        >= PREFERENCE_THRESHOLD
    ):
        style_instructions.append(
            "処理を小さな手順に分ける"
        )

    if (
        _score(
            model.preferences,
            "バージョン管理",
        )
        >= PREFERENCE_THRESHOLD
    ):
        style_instructions.append(
            "必要に応じてGitの確認・コミット・タグ手順を含める"
        )

    if (
        _score(
            model.conversation_style,
            "詳細さ",
        )
        >= PREFERENCE_THRESHOLD
    ):
        style_instructions.append(
            "重要な前提と注意点を省略しすぎない"
        )

    if (
        _score(
            model.conversation_style,
            "構造化",
        )
        >= PREFERENCE_THRESHOLD
    ):
        style_instructions.append(
            "見出しと段階を使って整理する"
        )

    if (
        _score(
            model.conversation_style,
            "理由付き説明",
        )
        >= PREFERENCE_THRESHOLD
    ):
        style_instructions.append(
            "提案には短い理由を添える"
        )

    for key, score in model.interests.items():
        if float(score) >= HIGH_SCORE_THRESHOLD:
            priority_topics.append(key)

    for key, score in model.knowledge_level.items():
        if float(score) >= HIGH_SCORE_THRESHOLD:
            familiar_topics.append(key)

    return {
        "preferred_formats": preferred_formats,
        "style_instructions": style_instructions,
        "priority_topics": priority_topics,
        "familiar_topics": familiar_topics,
    }


def build_user_response_policy_prompt(
    model: UserModel | None = None,
) -> str:
    detected = detect_response_preferences(model)

    lines = [
        "【推定された回答最適化方針】",
    ]

    preferred_formats = detected["preferred_formats"]
    style_instructions = detected["style_instructions"]
    priority_topics = detected["priority_topics"]
    familiar_topics = detected["familiar_topics"]

    if preferred_formats:
        lines.append(
            "- 優先形式: "
            + ", ".join(preferred_formats)
        )

    for instruction in style_instructions:
        lines.append(f"- {instruction}")

    if priority_topics:
        lines.append(
            "- 関連する場合に優先して検討する分野: "
            + ", ".join(priority_topics)
        )

    if familiar_topics:
        lines.append(
            "- 基礎説明を簡略化できる可能性がある分野: "
            + ", ".join(familiar_topics)
        )

    if len(lines) == 1:
        lines.append(
            "- まだ十分な傾向がないため、現在の質問内容を基準に回答する"
        )

    lines.extend([
        "",
        "【適用上の注意】",
        "- 現在のユーザー指示が最優先",
        "- 関心分野と質問内容を混同しない",
        "- 推定知識レベルを断定しない",
        "- 回答の正確性・安全性・中立性は変更しない",
    ])

    return "\n".join(lines)
