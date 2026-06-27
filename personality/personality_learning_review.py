import json
from datetime import datetime
from pathlib import Path

from personality.character_profile import get_character_profile
from personality.tone_learning_review import get_tone_review


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "personality_learning" / "personality_learning_review_1.json"


def build_personality_learning_review() -> dict:
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "stage": "39-personality-learning-review-1",
        "summary": "デモ会話テスト後の第1回人格学習レビュー",
        "current_profile": get_character_profile(),
        "current_tone_review": get_tone_review(),
        "learning_result": {
            "tone": {
                "strength": "high",
                "result": "短い指示に対して、余計な前置きを減らし、すぐ実行手順を提示する方針を維持する。"
            },
            "format": {
                "strength": "high",
                "result": "実装依頼ではPowerShellで1回コピペできる形式を最優先する。"
            },
            "explanation": {
                "strength": "medium-low",
                "result": "説明は必要最小限にし、目的・成功条件・次の段階を短く示す。"
            },
            "values": {
                "strength": "low",
                "result": "日本語、丁寧さ、安全性、不確実性の明示は固定する。"
            },
            "character": {
                "strength": "high",
                "result": "看板キャラ兼開発補助AIとして、落ち着いた実用補助寄りの人格を維持する。"
            }
        },
        "next_policy": [
            "人格を直接書き換えず、まずJSONとして保存する",
            "次段階でJSON保存方式を正式化する",
            "その後、人格プロンプトをJSON参照方式に変更する"
        ]
    }


def save_personality_learning_review() -> dict:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = build_personality_learning_review()
    OUTPUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "status": "ok",
        "path": str(OUTPUT_PATH),
        "created_at": data["created_at"],
    }


if __name__ == "__main__":
    print(save_personality_learning_review())
