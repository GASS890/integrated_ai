import time
from speaker.speaker_config import load_speaker_config, save_speaker_config
from speaker.speaker_service import (
    speaker_queue_clear,
    speaker_queue_status,
    speaker_worker_start,
    speaker_worker_status,
)

from main import ask, queue_assistant_reply_to_speaker


config = load_speaker_config()
config["tts_backend"] = "style_bert_vits2"
config["auto_enqueue_ai_response"] = True
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

# LLM本体を使わず、通常チャット応答に近い形で確認
assistant_text = "はい。Style-Bert-VITS2による通常チャット応答の読み上げテストです。現在の音声経路は正常に動作しています。"

result = queue_assistant_reply_to_speaker(assistant_text)

print("tts result:", result)

for i in range(15):
    print(f"wait {i + 1}/15")
    print("queue:", speaker_queue_status())
    print("worker:", speaker_worker_status())
    time.sleep(1)

print("finished")
