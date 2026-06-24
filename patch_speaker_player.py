from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

old_import = "from speaker.speaker_service import speaker_say, get_speaker_status, update_speaker_config\n"
new_import = "from speaker.speaker_service import speaker_say, speaker_play, get_speaker_status, update_speaker_config\n"

if old_import in text and new_import not in text:
    text = text.replace(old_import, new_import)

insert_before = '''@app.post("/speaker/say")
def speaker_say_api(req: TTSRequest):
'''

api = '''@app.post("/speaker/play")
def speaker_play_api(req: dict):
    path = (req or {}).get("path", "")
    if not path:
        raise HTTPException(status_code=400, detail="path is empty")
    try:
        return speaker_play(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


'''

if '@app.post("/speaker/play")' not in text:
    text = text.replace(insert_before, api + insert_before)

path.write_text(text, encoding="utf-8")
print("speaker player api patched.")
