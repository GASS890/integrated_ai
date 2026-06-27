from personality.personality_snapshot import (
    save_personality_snapshot,
    list_personality_snapshots,
)

result = save_personality_snapshot("35-2 initial personality snapshot")
print(result)

items = list_personality_snapshots()
print("snapshot count:", len(items))
print(items[-1] if items else None)
