from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

target = "def queue_assistant_reply_to_speaker(assistant_text: str):"
pos = text.find(target)

if pos == -1:
    raise RuntimeError("queue_assistant_reply_to_speaker not found")

insert = '''def queue_assistant_reply_to_speaker(assistant_text: str):
    print("[STYLEBERT DEBUG] queue_assistant_reply_to_speaker called")
'''

start = pos
line_end = text.find("\n", pos)
text = text[:start] + insert + text[line_end+1:]

path.write_text(text, encoding="utf-8")
print("debug log inserted")
