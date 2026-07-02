import os
import time
import threading
import subprocess
import webview
import uvicorn
from services.startup_manager import start_startup_services


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def start_server():
    os.chdir(BASE_DIR)

    import main

    uvicorn.run(
        main.app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    start_startup_services()

    server_thread = threading.Thread(
        target=start_server,
        daemon=True
    )
    server_thread.start()

    time.sleep(3)

    webview.create_window(
        "統合AI",
        "http://127.0.0.1:8000/",
        width=1100,
        height=760,
        resizable=True,
    )

    webview.start()