from datetime import datetime


_STATE = {
    "last_text": "",
    "last_output_file": "",
    "last_error": "",
    "last_spoken_at": "",
    "last_played_file": "",
    "last_played_at": "",
    "speak_count": 0,
    "play_count": 0,
}


def get_speaker_state() -> dict:
    return dict(_STATE)


def update_speaker_success(text: str, output_file: str):
    _STATE["last_text"] = text
    _STATE["last_output_file"] = output_file
    _STATE["last_error"] = ""
    _STATE["last_spoken_at"] = datetime.now().isoformat(timespec="seconds")
    _STATE["speak_count"] = int(_STATE.get("speak_count", 0)) + 1


def update_speaker_played(output_file: str):
    _STATE["last_played_file"] = output_file
    _STATE["last_played_at"] = datetime.now().isoformat(timespec="seconds")
    _STATE["play_count"] = int(_STATE.get("play_count", 0)) + 1


def update_speaker_error(text: str, error: str):
    _STATE["last_text"] = text
    _STATE["last_error"] = error
    _STATE["last_spoken_at"] = datetime.now().isoformat(timespec="seconds")
