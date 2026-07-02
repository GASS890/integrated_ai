import subprocess

from config.app_config import VOICEVOX_EXE


def launch():
    if not VOICEVOX_EXE.exists():
        print("VOICEVOX.exe not found:", VOICEVOX_EXE)
        return

    subprocess.Popen(
        [str(VOICEVOX_EXE)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
