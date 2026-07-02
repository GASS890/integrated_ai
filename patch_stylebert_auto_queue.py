from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

start = text.find("def queue_assistant_reply_to_speaker(assistant_text: str):")
if start == -1:
    raise RuntimeError("queue_assistant_reply_to_speaker が見つかりません")

end = text.find("def finalize_interaction(", start)
if end == -1:
    raise RuntimeError("finalize_interaction が見つかりません")

new_func = '''def queue_assistant_reply_to_speaker(assistant_text: str):
    text = (assistant_text or "").strip()
    if not text:
        return None

    try:
        from speaker.speaker_config import load_speaker_config

        config = load_speaker_config()
        backend = config.get("tts_backend", "")

        if backend == "style_bert_vits2":
            from voice.stylebert_vits2_client import stylebert_say

            result = stylebert_say(
                text,
                model_id=int(config.get("stylebert_model_id", 0)),
                speaker_id=int(config.get("stylebert_speaker_id", 0)),
                style=config.get("stylebert_style", "Neutral"),
                style_weight=float(config.get("stylebert_style_weight", 5.0)),
                length=float(config.get("stylebert_length", 1.0)),
            )
            speaker_queue_add(result["output_file"])
            return result

        result = speaker_say(
            text,
            backend=None,
            auto_play=False,
        )
        speaker_queue_add(result["output_file"])
        return result

    except Exception as e:
        print("assistant speaker queue error:", e)
        return None


'''

text = text[:start] + new_func + text[end:]

path.write_text(text, encoding="utf-8")
print("main.py updated: Style-Bert-VITS2 auto queue support")
