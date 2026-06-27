from personality.personality_learning_store import (
    add_learning_result,
    list_learning_results,
    get_latest_learning_result,
    build_learning_results_prompt,
)

item = add_learning_result(
    title="第1回人格学習レビュー",
    summary="短い指示には前置きを減らし、PowerShellで1回コピペできる形式を優先する。",
    category="tone_and_format",
    strength="high",
    source="stage_39_review",
    notes=[
        "説明量はmedium-low",
        "価値観はlowで固定",
        "開発補助AIとしての落ち着いた口調を維持",
    ],
)

print("added:", item)
print("count:", len(list_learning_results()))
print("latest:", get_latest_learning_result())
print()
print(build_learning_results_prompt())
