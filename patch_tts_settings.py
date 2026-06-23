from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

old_import = "from voice.tts_router import synthesize_voice, get_tts_status\n"
new_import = "from voice.tts_router import synthesize_voice, get_tts_status, update_tts_settings\n"

if old_import in text and new_import not in text:
    text = text.replace(old_import, new_import)

insert_before = '''@app.get("/tts/status")
def tts_status():
    return get_tts_status()
'''

api_code = '''@app.post("/tts/settings")
def tts_settings_update(settings: dict):
    try:
        return update_tts_settings(settings)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


'''

if '@app.post("/tts/settings")' not in text:
    text = text.replace(insert_before, api_code + insert_before)

path.write_text(text, encoding="utf-8")
print("tts settings patched.")
