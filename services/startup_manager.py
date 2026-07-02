import os
import subprocess

from services.service_registry import get_autostart_services

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
        script = os.path.join(BASE_DIR, "tools", "Style-Bert-VITS2", "Server.bat")
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
        exe = os.path.join(BASE_DIR, "VOICEVOX", "VOICEVOX.exe")
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


def start_startup_services():
    settings = {}

    try:
        from voice.tts_settings import load_tts_settings
        settings = load_tts_settings()
    except Exception as e:
        print("TTS settings load skipped:", e)

    for name in get_autostart_services(settings):
        try:
            launch_service(name)
        except Exception as e:
            print(f"{name} start failed:", e)
