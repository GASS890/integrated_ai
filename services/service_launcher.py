import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        script = os.path.join(
            BASE_DIR,
            "tools",
            "Style-Bert-VITS2",
            "Server.bat",
        )

        if os.path.exists(script):
            subprocess.Popen(
                [script],
                cwd=os.path.dirname(script),
                shell=True,
            )
        else:
            print("Style-Bert-VITS2 Server.bat not found:", script)

        return

    if name == "voicevox":
        exe = os.path.join(
            BASE_DIR,
            "VOICEVOX",
            "VOICEVOX.exe",
        )

        if os.path.exists(exe):
            subprocess.Popen(
                [exe],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            print("VOICEVOX.exe not found:", exe)

        return

    print("Unknown service:", name)
