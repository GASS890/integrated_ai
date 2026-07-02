import subprocess

from config.app_config import STYLEBERT_SERVER_BAT, VOICEVOX_EXE


def launch_service(name: str):

    if name == "ollama":
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        return

    if name == "stylebert":
        script = STYLEBERT_SERVER_BAT

        if script.exists():
            subprocess.Popen(
                [str(script)],
                cwd=str(script.parent),
                shell=True,
            )
        else:
            print("Style-Bert-VITS2 Server.bat not found:", script)

        return

    if name == "voicevox":
        exe = VOICEVOX_EXE

        if exe.exists():
            subprocess.Popen(
                [str(exe)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            print("VOICEVOX.exe not found:", exe)

        return

    print("Unknown service:", name)
