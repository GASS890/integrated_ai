from voice.stylebert_vits2_client import stylebert_say

result = stylebert_say(
    "こんにちは。これはStyle-Bert-VITS2接続テストです。",
    model_id=0,
    speaker_id=0,
)

print(result)
