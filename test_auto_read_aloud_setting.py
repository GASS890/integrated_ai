from speaker.speaker_config import load_speaker_config, save_speaker_config
import main

print("main import ok")

before = load_speaker_config()
print("before:", before)

save_speaker_config({
    "auto_enqueue_ai_response": False
})
after_off = load_speaker_config()
print("after off:", after_off)

save_speaker_config({
    "auto_enqueue_ai_response": True
})
after_on = load_speaker_config()
print("after on:", after_on)

print("has helper:", hasattr(main, "queue_assistant_reply_to_speaker"))
