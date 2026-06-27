import main

print("main import ok")

with open("main.py", "r", encoding="utf-8") as f:
    text = f.read()

print("has helper:", "def queue_assistant_reply_to_speaker" in text)
print("has hook:", "queue_assistant_reply_to_speaker(assistant_text)" in text)
print("has speaker_queue_add:", "speaker_queue_add" in text)
