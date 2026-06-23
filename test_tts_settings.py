from voice.tts_router import get_tts_status, update_tts_settings
from voice.piper_plus_client import synthesize_piper_plus

print("before:", get_tts_status())

update_tts_settings({
    "backend": "piper_plus",
    "fallback_backend": "voicevox",
    "speaker": 1,
    "auto_fallback": True,
})

print("after:", get_tts_status())

wav = synthesize_piper_plus("こんにちは。Piper Plusを既定音声として使うテストです。")
print("wav bytes:", len(wav))

with open("outputs/tts/piper_plus_default_test.wav", "wb") as f:
    f.write(wav)

print("saved: outputs/tts/piper_plus_default_test.wav")
