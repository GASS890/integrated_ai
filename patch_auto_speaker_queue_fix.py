from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

# -------------------------------------------------
# import確認・追加
# -------------------------------------------------

old_import = """from speaker.speaker_service import (
    speaker_say,
    speaker_play,
    speaker_queue_add,
"""

if old_import not in text:
    old_import_2 = """from speaker.speaker_service import (
    speaker_say,
    speaker_play,
"""
    new_import_2 = """from speaker.speaker_service import (
    speaker_say,
    speaker_play,
    speaker_queue_add,
"""
    text = text.replace(old_import_2, new_import_2)

# -------------------------------------------------
# helper追加
# -------------------------------------------------

helper_marker = '''def queue_assistant_reply_to_speaker(assistant_text: str):
'''

helper_code = '''def queue_assistant_reply_to_speaker(assistant_text: str):
    text = (assistant_text or "").strip()
    if not text:
        return None

    try:
        result = speaker_say(
            text,
            backend=None,
            auto_play=False,
        )
        speaker_queue_add(result["output_file"])
        return result
    except Exception as e:
        print("assistant speaker queue error:", e)
        return None


'''

insert_before = '''def finalize_interaction(
'''

if helper_marker not in text:
    text = text.replace(insert_before, helper_code + insert_before, 1)

# -------------------------------------------------
# finalize_interaction 内に投入処理を追加
# -------------------------------------------------

old = '''    maybe_store_long_term_memory(user_text, intent=intent)

    try:
        reflect_conversation_to_memory(user_text, assistant_text)
    except Exception as e:
        print("embedding memory reflection error:", e)

'''

new = '''    maybe_store_long_term_memory(user_text, intent=intent)

    try:
        queue_assistant_reply_to_speaker(assistant_text)
    except Exception as e:
        print("assistant speaker queue hook error:", e)

    try:
        reflect_conversation_to_memory(user_text, assistant_text)
    except Exception as e:
        print("embedding memory reflection error:", e)

'''

if "queue_assistant_reply_to_speaker(assistant_text)" not in text:
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("AI response speaker queue fix applied.")
