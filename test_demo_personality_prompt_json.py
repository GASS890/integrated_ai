from personality.demo_personality_prompt import (
    build_demo_personality_prompt,
    build_short_demo_personality_prompt,
)

short_prompt = build_short_demo_personality_prompt()
full_prompt = build_demo_personality_prompt()

print("=== SHORT ===")
print(short_prompt)
print()
print("=== CHECK ===")
print("has learning result:", "【人格学習結果】" in short_prompt or "【人格学習結果】" in full_prompt)
print("short length:", len(short_prompt))
print("full length:", len(full_prompt))
