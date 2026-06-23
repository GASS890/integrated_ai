from voice.tts_router import get_tts_status
from voice.piper_plus_client import synthesize_piper_plus

print(get_tts_status())

wav = synthesize_piper_plus("こんにちは。integrated_aiからPiper Plusを呼び出すテストです。")
print("wav bytes:", len(wav))

with open("outputs/tts/integrated_ai_piper_plus_test.wav", "wb") as f:
    f.write(wav)

print("saved: outputs/tts/integrated_ai_piper_plus_test.wav")
