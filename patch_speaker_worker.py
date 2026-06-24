from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

old_import = """from speaker.speaker_service import (
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

new_import = """from speaker.speaker_service import (
    speaker_say,
    speaker_play,
    speaker_queue_add,
    speaker_queue_clear,
    speaker_queue_status,
    speaker_queue_play_next,
    speaker_worker_status,
    speaker_worker_start,
    speaker_worker_stop,
    get_speaker_status,
    update_speaker_config,
)
"""

if old_import in text and "speaker_worker_start" not in text:
    text = text.replace(old_import, new_import)

insert_before = '''@app.get("/speaker/queue")
def speaker_queue_get():
'''

api = '''@app.get("/speaker/worker")
def speaker_worker_get():
    return speaker_worker_status()


@app.post("/speaker/worker/start")
def speaker_worker_start_api():
    return speaker_worker_start()


@app.post("/speaker/worker/stop")
def speaker_worker_stop_api():
    return speaker_worker_stop()


'''

if '@app.get("/speaker/worker")' not in text:
    text = text.replace(insert_before, api + insert_before)

# 起動時にworkerを自動開始
startup_marker = '''@app.on_event("startup")
def startup_event():
'''

startup_code = '''@app.on_event("startup")
def startup_event():
    try:
        speaker_worker_start()
        print("speaker worker started")
    except Exception as e:
        print("speaker worker start error:", e)
'''

if startup_marker in text and "speaker worker started" not in text:
    text = text.replace(startup_marker, startup_code, 1)

path.write_text(text, encoding="utf-8")
print("speaker worker api patched.")
