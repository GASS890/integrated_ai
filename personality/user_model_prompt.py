from personality.user_model import UserModel
from personality.user_model_manager import load_user_model


def _format_scores(
    values: dict[str, float],
    minimum_score: float = 0.0,
) -> str:
    if not values:
        return "- 未設定"

    filtered = [
        (key, float(score))
        for key, score in values.items()
        if float(score) >= minimum_score
    ]

    if not filtered:
        return "- 該当なし"

    filtered.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return "\n".join(
        f"- {key}: {score:.2f}"
        for key, score in filtered
    )


def build_user_model_prompt(
    model: UserModel | None = None,
) -> str:
    if model is None:
        model = load_user_model()

    return f"""
以下は、会話から蓄積されたユーザー理解です。
人格そのものではなく、回答内容・説明形式・話題の優先順位を調整するために使用してください。

【関心分野】
{_format_scores(model.interests)}

【好み】
{_format_scores(model.preferences)}

【推定知識レベル】
{_format_scores(model.knowledge_level)}

【会話スタイル】
{_format_scores(model.conversation_style)}

【利用規則】
- スコアが高い項目ほど、回答形式や関連話題の候補として優先する
- ユーザーの現在の質問を最優先し、関心分野だけで内容を決めつけない
- 知識レベルが高い分野では、基礎説明を短くしてよい
- 知識レベルが低い分野では、専門用語を補足する
- 好みは回答形式の調整に使い、事実や結論を歪めない
- スコアは推定値であり、明示された現在の要望と矛盾する場合は現在の要望を優先する
""".strip()
