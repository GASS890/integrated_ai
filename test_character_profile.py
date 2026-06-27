from personality.character_profile import get_character_profile, build_character_profile_prompt

profile = get_character_profile()

print(profile["name"])
print(profile["role"])
print(profile["learning_policy"])
print()
print(build_character_profile_prompt())
