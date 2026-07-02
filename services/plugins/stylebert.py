import subprocess

from config.app_config import STYLEBERT_SERVER_BAT


def launch():
    if not STYLEBERT_SERVER_BAT.exists():
        print("Style-Bert-VITS2 Server.bat not found:", STYLEBERT_SERVER_BAT)
        return

    subprocess.Popen(
        [str(STYLEBERT_SERVER_BAT)],
        cwd=str(STYLEBERT_SERVER_BAT.parent),
        shell=True,
    )
