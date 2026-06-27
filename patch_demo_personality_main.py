from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

# import追加
import_line = "from personality.demo_personality_prompt import build_short_demo_personality_prompt\n"

if import_line not in text:
    marker = "from personality.character_profile import"
    if marker in text:
        text = text.replace(marker, import_line + marker, 1)
    else:
        marker = "from personality.state_schema import normalize_sessions_personality\n"
        text = text.replace(marker, marker + import_line, 1)

# ask() 内の memories_text にデモ人格プロンプトを追加
old = '''        memories_text = "\\n\\n".join(
            part for part in [memory_db_text, embedding_text]
            if part and part.strip()
        )
'''

new = '''        demo_personality_text = build_short_demo_personality_prompt()

        memories_text = "\\n\\n".join(
            part for part in [demo_personality_text, memory_db_text, embedding_text]
            if part and part.strip()
        )
'''

if "demo_personality_text = build_short_demo_personality_prompt()" not in text:
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("demo personality prompt wired into main.py")
