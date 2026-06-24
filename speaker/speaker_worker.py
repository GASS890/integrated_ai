import threading
import time

from speaker.speaker_queue import (
    dequeue,
    get_queue_state,
    set_playing,
    increment_played,
)
from speaker.speaker_player import play_wav


_worker_thread = None
_worker_running = False


def worker_status() -> dict:
    return {
        "running": _worker_running,
        **get_queue_state(),
    }


def _worker_loop():
    global _worker_running

    while _worker_running:
        item = dequeue()

        if not item:
            time.sleep(0.5)
            continue

        path = item.get("path")

        if not path:
            continue

        try:
            set_playing(True)
            play_wav(path)
            increment_played()

        except Exception as e:
            print("speaker worker error:", e)

        finally:
            set_playing(False)


def start_worker() -> dict:
    global _worker_thread
    global _worker_running

    if _worker_running:
        return worker_status()

    _worker_running = True

    _worker_thread = threading.Thread(
        target=_worker_loop,
        daemon=True,
    )

    _worker_thread.start()

    return worker_status()


def stop_worker() -> dict:
    global _worker_running

    _worker_running = False

    return worker_status()
