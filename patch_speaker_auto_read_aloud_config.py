from pathlib import Path

path = Path("speaker/speaker_config.py")
text = path.read_text(encoding="utf-8")

old = '''    "auto_play": False,
    "output_dir": "outputs/tts",
'''

new = '''    "auto_play": False,
    "auto_enqueue_ai_response": True,
    "output_dir": "outputs/tts",
'''

if '"auto_enqueue_ai_response"' not in text:
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("speaker_config auto_enqueue_ai_response added.")
