from personality.character_profile import build_character_profile_prompt
from personality.tone_learning_review import build_tone_review_prompt
from personality.personality_learning_store import build_learning_results_prompt


def build_demo_personality_prompt() -> str:
    learning_prompt = build_learning_results_prompt(limit=5)

    parts = [
        "【デモ用人格プロンプト】",
        build_character_profile_prompt(),
        build_tone_review_prompt(),
    ]

    if learning_prompt:
        parts.append(learning_prompt)

    parts.extend([
        "【現在のデモ方針】",
        "- 一旦、動くローカルAIとして形にする",
        "- TTSと人格を優先して安定化する",
        "- 実装は一つずつ確認しながら進める",
        "- 将来はスマホ=脳、スピーカー=耳と口、PC=長期記憶へ分割する",
        "- 音声学習は人格・口調が安定してから行う",
    ])

    return "\n\n".join(parts)


def build_short_demo_personality_prompt() -> str:
    learning_prompt = build_learning_results_prompt(limit=3)

    lines = [
        "あなたは看板キャラ兼開発補助AI。",
        "丁寧・簡潔・落ち着いた日本語で答える。",
        "実装指示はPowerShellで実行できる形式を優先する。",
        "ユーザーは一つずつ順番に進めることを好む。",
        "口調は高く適応し、好みは中程度、価値観は低く学習する。",
        "不確実な点は明示する。",
    ]

    if learning_prompt:
        lines.append(learning_prompt)

    return "\n".join(lines)
