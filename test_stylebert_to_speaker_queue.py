from voice.stylebert_vits2_client import stylebert_say
from speaker.speaker_service import (
    speaker_queue_add,
    speaker_queue_status,
    speaker_worker_start,
    speaker_worker_status,
)


def stylebert_say_to_queue(text: str) -> dict:
    result = stylebert_say(text)

    output_file = result.get("output_file")
    if not output_file:
        raise RuntimeError("Style-Bert-VITS2 output_file not found")

    queue_result = speaker_queue_add(output_file)

    return {
        "status": "ok",
        "tts_result": result,
        "queue_result": queue_result,
    }


if __name__ == "__main__":
    print("start worker:")
    print(speaker_worker_start())

    print("worker status:")
    print(speaker_worker_status())

    print("queue before:")
    print(speaker_queue_status())

    result = stylebert_say_to_queue(
        "こんにちは。これはStyle-Bert-VITS2からSpeaker Queueへ投入するテストです。"
    )

    print("result:")
    print(result)

    print("queue after:")
    print(speaker_queue_status())
