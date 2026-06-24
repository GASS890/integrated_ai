from speaker.speaker_service import get_speaker_status, speaker_say, speaker_play

print("status before:")
print(get_speaker_status())

result = speaker_say(
    "こんにちは。これはSpeaker Audio Playerのテストです。",
    auto_play=False,
)

print("say result:")
print(result)

play_result = speaker_play(result["output_file"])

print("play result:")
print(play_result)

print("status after:")
print(get_speaker_status())
