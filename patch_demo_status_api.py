from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

import_line = "from demo.demo_status import get_demo_status\n"

if import_line not in text:
    marker = "from speaker.speaker_service import (\n"
    text = text.replace(marker, import_line + marker, 1)

insert_before = '''@app.get("/speaker/worker")
def speaker_worker_get():
'''

api = '''@app.get("/demo/status")
def demo_status():
    return get_demo_status()


'''

if '@app.get("/demo/status")' not in text:
    text = text.replace(insert_before, api + insert_before)

path.write_text(text, encoding="utf-8")
print("demo status api patched.")
