from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

old_import = "from voice.tts_router import synthesize_voice, get_tts_status, update_tts_settings\n"
new_import = "from voice.tts_router import synthesize_voice, get_tts_status, update_tts_settings, get_available_tts_backends\n"

if old_import in text and new_import not in text:
    text = text.replace(old_import, new_import)

insert_before = '''@app.post("/tts/settings")
def tts_settings_update(settings: dict):
'''

api_code = '''@app.get("/tts/backends")
def tts_backends():
    return get_available_tts_backends()


'''

if '@app.get("/tts/backends")' not in text:
    text = text.replace(insert_before, api_code + insert_before)

path.write_text(text, encoding="utf-8")
print("tts status api patched.")
