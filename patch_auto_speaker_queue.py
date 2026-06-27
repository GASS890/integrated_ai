from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

# -------------------------------------------------
# import追加
# -------------------------------------------------

old_import = """from speaker.speaker_service import (
    speaker_say,
"""

new_import = """from speaker.speaker_service import (
    speaker_say,
    speaker_queue_add,
"""

if "speaker_queue_add," not in text:
    text = text.replace(old_import, new_import)

# -------------------------------------------------
# speaker_say() の直後にQueue投入
# -------------------------------------------------

old = """        result = speaker_say(
            answer_text,
            backend=None,
            auto_play=False,
        )

"""

new = """        result = speaker_say(
            answer_text,
            backend=None,
            auto_play=False,
        )

        try:
            speaker_queue_add(result["output_file"])
        except Exception as e:
            print("speaker queue add error:", e)

"""

if old in text:
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("AI response -> Speaker Queue patched.")
