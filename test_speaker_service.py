from speaker.speaker_service import get_speaker_status, speaker_say

print("status:")
print(get_speaker_status())

result = speaker_say("こんにちは。これはSpeaker Service分離準備のテストです。")
print("say result:")
print(result)
