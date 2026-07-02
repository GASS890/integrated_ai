from services.service_registry import get_autostart_services
from services.service_launcher import launch_service


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
