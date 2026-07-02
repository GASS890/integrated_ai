from speaker.speaker_config import load_speaker_config, save_speaker_config
from speaker.speaker_service import (
    speaker_queue_clear,
    speaker_queue_status,
    speaker_worker_start,
    speaker_worker_status,
)
from main import queue_assistant_reply_to_speaker

config = load_speaker_config()
config["tts_backend"] = "style_bert_vits2"
config["stylebert_model_id"] = 0
config["stylebert_speaker_id"] = 0
config["stylebert_style"] = "Neutral"
config["stylebert_style_weight"] = 5.0
config["stylebert_length"] = 1.0
save_speaker_config(config)

print("config:", load_speaker_config())
print("clear:", speaker_queue_clear())
print("worker:", speaker_worker_start())
print("before:", speaker_queue_status())

result = queue_assistant_reply_to_speaker(
    "こんにちは。これはAI応答をStyle-Bert-VITS2で自動読み上げするテストです。"
)

print("result:", result)
print("after:", speaker_queue_status())
print("worker status:", speaker_worker_status())
