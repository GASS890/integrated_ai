import os
import time
import threading
import subprocess
import webview
import uvicorn


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


def start_ollama():
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
    except Exception as e:
        print("Ollama起動失敗:", e)


def start_voicevox():
    exe = os.path.join(BASE_DIR, "VOICEVOX", "VOICEVOX.exe")

    if os.path.exists(exe):
        try:
            subprocess.Popen(
                [exe],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print("VOICEVOX起動失敗:", e)


if __name__ == "__main__":
    start_ollama()

    # VOICEVOX is optional.
    # start_voicevox()

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