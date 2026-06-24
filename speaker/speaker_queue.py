from collections import deque
from threading import Lock


_QUEUE = deque()
_LOCK = Lock()

_STATE = {
    "currently_playing": False,
    "queue_size": 0,
    "total_played": 0,
}


def enqueue(item: dict):
    with _LOCK:
        _QUEUE.append(item)
        _STATE["queue_size"] = len(_QUEUE)


def dequeue():
    with _LOCK:
        if not _QUEUE:
            return None

        item = _QUEUE.popleft()
        _STATE["queue_size"] = len(_QUEUE)
        return item


def clear_queue():
    with _LOCK:
        _QUEUE.clear()
        _STATE["queue_size"] = 0


def get_queue_state():
    with _LOCK:
        return {
            **_STATE,
            "queue_size": len(_QUEUE),
        }


def set_playing(flag: bool):
    with _LOCK:
        _STATE["currently_playing"] = bool(flag)


def increment_played():
    with _LOCK:
        _STATE["total_played"] = int(_STATE.get("total_played", 0)) + 1
