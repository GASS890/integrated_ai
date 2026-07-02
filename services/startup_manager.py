import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def start_ollama():
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
    except Exception as e:
        print("Ollama start failed:", e)


def start_voicevox():
    exe = os.path.join(BASE_DIR, "VOICEVOX", "VOICEVOX.exe")

    if os.path.exists(exe):
        try:
            subprocess.Popen(
                [exe],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print("VOICEVOX start failed:", e)


def start_stylebert():
    script = os.path.join(
        BASE_DIR,
        "tools",
        "Style-Bert-VITS2",
        "Server.bat"
    )

    if os.path.exists(script):
        try:
            subprocess.Popen(
                [script],
                cwd=os.path.dirname(script),
                shell=True
            )
        except Exception as e:
            print("Style-Bert-VITS2 start failed:", e)
    else:
        print("Style-Bert-VITS2 Server.bat not found:", script)


def start_startup_services():
    start_ollama()
    start_stylebert()

    try:
        from voice.tts_settings import load_tts_settings
        if load_tts_settings().get("voicevox_enabled", False):
            start_voicevox()
    except Exception as e:
        print("VOICEVOX optional startup skipped:", e)
