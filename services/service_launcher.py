from services.plugins import ollama
from services.plugins import stylebert
from services.plugins import voicevox


PLUGINS = {
    "ollama": ollama.launch,
    "stylebert": stylebert.launch,
    "voicevox": voicevox.launch,
}


def launch_service(name: str):
    launcher = PLUGINS.get(name)

    if launcher is None:
        print("Unknown service:", name)
        return

    launcher()
