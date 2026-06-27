from personality.tone_learning_review import get_tone_review, build_tone_review_prompt

review = get_tone_review()

print(review["user_instruction_style"])
print()
print(build_tone_review_prompt())
