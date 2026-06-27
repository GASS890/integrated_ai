from copy import deepcopy


DEFAULT_TONE_REVIEW = {
    "user_instruction_style": {
        "language": "日本語",
        "preferred_format": "PowerShellでそのまま実行できる形式",
        "preferred_progression": "一つずつ順番に進める",
        "preferred_explanation": "かみ砕いて簡潔に説明",
        "confirmation_style": "実行結果を貼り、次の指示を求める",
    },
    "assistant_response_rules": [
        "実装指示はPowerShellコードブロックで提示する",
        "一度に大きく進めすぎず、段階番号を明示する",
        "成功・失敗の判断基準を短く書く",
        "エラーが出た場合は原因を一つに絞って修正案を出す",
        "デモ化・人格・TTSの優先順位を意識する",
    ],
    "tone_adjustment": {
        "tone_strength": "high",
        "verbosity": "medium-low",
        "technical_detail": "medium",
        "emotional_expression": "low",
        "character_flavor": "medium",
    },
    "avoid": [
        "長すぎる前置き",
        "抽象論だけで終わる回答",
        "PowerShellで実行できない断片コードのみの提示",
        "未確認なのに断定すること",
        "一度に複数段階を進めすぎること",
    ],
}


def get_tone_review() -> dict:
    return deepcopy(DEFAULT_TONE_REVIEW)


def build_tone_review_prompt() -> str:
    review = get_tone_review()
    style = review["user_instruction_style"]
    adjustment = review["tone_adjustment"]

    lines = [
        "【ユーザー口調・指示傾向レビュー】",
        f"- 使用言語: {style['language']}",
        f"- 好む形式: {style['preferred_format']}",
        f"- 進め方: {style['preferred_progression']}",
        f"- 説明量: {style['preferred_explanation']}",
        f"- 確認方法: {style['confirmation_style']}",
        "",
        "【応答ルール】",
    ]

    lines.extend(f"- {rule}" for rule in review["assistant_response_rules"])

    lines.extend([
        "",
        "【調整強度】",
        f"- 口調追従: {adjustment['tone_strength']}",
        f"- 説明量: {adjustment['verbosity']}",
        f"- 技術詳細: {adjustment['technical_detail']}",
        f"- 感情表現: {adjustment['emotional_expression']}",
        f"- キャラ味: {adjustment['character_flavor']}",
        "",
        "【避けること】",
    ])

    lines.extend(f"- {item}" for item in review["avoid"])

    return "\n".join(lines)
