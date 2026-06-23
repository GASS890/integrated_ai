from voice.tts_router import get_tts_status, get_available_tts_backends

print("status:")
print(get_tts_status())

print("backends:")
print(get_available_tts_backends())
