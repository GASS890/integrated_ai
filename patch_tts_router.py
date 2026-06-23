from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

old = "from voicevox_client import synthesize_voice\n"
new = "from voice.tts_router import synthesize_voice, get_tts_status\n"

if old in text and new not in text:
    text = text.replace(old, new)

# TTS状態APIを追加
insert_before = '''@app.post("/tts")
def tts(req: TTSRequest):
'''

api_code = '''@app.get("/tts/status")
def tts_status():
    return get_tts_status()


'''

if '@app.get("/tts/status")' not in text:
    text = text.replace(insert_before, api_code + insert_before)

path.write_text(text, encoding="utf-8")
print("tts router patched.")
