import time

from speaker.speaker_service import (
    speaker_say,
    speaker_queue_add,
    speaker_worker_start,
    speaker_worker_status,
)


print("start worker:")
print(speaker_worker_start())

result = speaker_say(
    "こんにちは。Speaker Workerの自動再生テストです。",
    auto_play=False,
)

print("say result:")
print(result)

print("queue add:")
print(speaker_queue_add(result["output_file"]))

print("worker status after add:")
print(speaker_worker_status())

time.sleep(3)

print("worker status after wait:")
print(speaker_worker_status())
