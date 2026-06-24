from speaker.speaker_service import (
    speaker_say,
    speaker_queue_add,
    speaker_queue_clear,
    speaker_queue_status,
    speaker_queue_play_next,
)

print("initial:")
print(speaker_queue_status())

speaker_queue_clear()

result = speaker_say(
    "こんにちは。これはSpeaker Queueのテストです。",
    auto_play=False,
)

print("say result:")
print(result)

print("add:")
print(speaker_queue_add(result["output_file"]))

print("status after add:")
print(speaker_queue_status())

print("play next:")
print(speaker_queue_play_next())

print("status after play:")
print(speaker_queue_status())
