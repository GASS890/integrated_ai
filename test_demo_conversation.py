import time

from main import queue_assistant_reply_to_speaker
from speaker.speaker_config import load_speaker_config, save_speaker_config
from speaker.speaker_service import (
    speaker_queue_clear,
    speaker_queue_status,
    speaker_worker_start,
    speaker_worker_status,
)


print("=== Demo Conversation Test ===")

config = load_speaker_config()
print("config before:", config)

save_speaker_config({
    "auto_enqueue_ai_response": True,
    "tts_backend": "piper_plus",
})

print("config after:", load_speaker_config())

print("clear queue:")
print(speaker_queue_clear())

print("start worker:")
print(speaker_worker_start())

print("queue before:")
print(speaker_queue_status())

result = queue_assistant_reply_to_speaker(
    "こんにちは。これはデモ会話テストです。AI応答が自動で音声キューに入り、スピーカーワーカーで再生されるか確認しています。"
)

print("enqueue result:")
print(result)

print("queue after enqueue:")
print(speaker_queue_status())

print("worker after enqueue:")
print(speaker_worker_status())

time.sleep(5)

print("queue after wait:")
print(speaker_queue_status())

print("worker after wait:")
print(speaker_worker_status())

print("=== Demo Conversation Test Finished ===")
