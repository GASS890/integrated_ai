from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

import_line = "from speaker.speaker_config import load_speaker_config\n"

if import_line not in text:
    marker = "from demo.demo_status import get_demo_status\n"
    text = text.replace(marker, marker + import_line, 1)

old = '''def queue_assistant_reply_to_speaker(assistant_text: str):
    text = (assistant_text or "").strip()
    if not text:
        return None

    try:
        result = speaker_say(
'''

new = '''def queue_assistant_reply_to_speaker(assistant_text: str):
    text = (assistant_text or "").strip()
    if not text:
        return None

    try:
        config = load_speaker_config()
        if not config.get("auto_enqueue_ai_response", True):
            return {
                "status": "skipped",
                "reason": "auto_enqueue_ai_response is false",
            }
    except Exception as e:
        print("speaker config load error:", e)

    try:
        result = speaker_say(
'''

if 'auto_enqueue_ai_response is false' not in text:
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("main.py auto read aloud setting patched.")
