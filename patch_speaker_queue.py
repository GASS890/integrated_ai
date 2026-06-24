from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

old_import = "from speaker.speaker_service import speaker_say, speaker_play, get_speaker_status, update_speaker_config\n"
new_import = """from speaker.speaker_service import (
    speaker_say,
    speaker_play,
    speaker_queue_add,
    speaker_queue_clear,
    speaker_queue_status,
    speaker_queue_play_next,
    get_speaker_status,
    update_speaker_config,
)
"""

if old_import in text and "speaker_queue_add" not in text:
    text = text.replace(old_import, new_import)

insert_before = '''@app.post("/speaker/play")
def speaker_play_api(req: dict):
'''

api = '''@app.get("/speaker/queue")
def speaker_queue_get():
    return speaker_queue_status()


@app.post("/speaker/queue/add")
def speaker_queue_add_api(req: dict):
    path = (req or {}).get("path", "")
    try:
        return speaker_queue_add(path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/speaker/queue/clear")
def speaker_queue_clear_api():
    return speaker_queue_clear()


@app.post("/speaker/queue/play_next")
def speaker_queue_play_next_api():
    try:
        return speaker_queue_play_next()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


'''

if '@app.get("/speaker/queue")' not in text:
    text = text.replace(insert_before, api + insert_before)

path.write_text(text, encoding="utf-8")
print("speaker queue api patched.")
