from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

# import追加
target = "from voice.tts_router import synthesize_voice, get_tts_status, update_tts_settings, get_available_tts_backends\n"
replacement = target + "from speaker.speaker_service import speaker_say, get_speaker_status, update_speaker_config\n"

if "from speaker.speaker_service import speaker_say" not in text:
    text = text.replace(target, replacement)

insert_before = '''@app.get("/tts/backends")
def tts_backends():
'''

api = '''@app.get("/speaker/status")
def speaker_status():
    return get_speaker_status()


@app.post("/speaker/settings")
def speaker_settings_update(settings: dict):
    return update_speaker_config(settings)


@app.post("/speaker/say")
def speaker_say_api(req: TTSRequest):
    try:
        return speaker_say(req.text, backend=None)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


'''

if '@app.get("/speaker/status")' not in text:
    text = text.replace(insert_before, api + insert_before)

path.write_text(text, encoding="utf-8")
print("speaker service api patched.")
