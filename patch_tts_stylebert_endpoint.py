from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

old = '''@app.post("/tts")
def tts(req: TTSRequest):
    try:
        audio = synthesize_voice(
            req.text,
            speaker=req.speaker,
            speed=req.speed,
            pitch=req.pitch,
            intonation=req.intonation
        )

        return StreamingResponse(
            BytesIO(audio),
            media_type="audio/wav"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

new = '''@app.post("/tts")
def tts(req: TTSRequest):
    try:
        config = load_speaker_config()
        backend = config.get("tts_backend", "")

        if backend == "style_bert_vits2":
            from voice.stylebert_vits2_client import stylebert_say

            result = stylebert_say(
                req.text,
                model_id=int(config.get("stylebert_model_id", 0)),
                speaker_id=int(config.get("stylebert_speaker_id", 0)),
                style=config.get("stylebert_style", "Neutral"),
                style_weight=float(config.get("stylebert_style_weight", 5.0)),
                length=float(config.get("stylebert_length", 1.0)),
            )

            audio = Path(result["output_file"]).read_bytes()

            return StreamingResponse(
                BytesIO(audio),
                media_type="audio/wav"
            )

        audio = synthesize_voice(
            req.text,
            speaker=req.speaker,
            speed=req.speed,
            pitch=req.pitch,
            intonation=req.intonation
        )

        return StreamingResponse(
            BytesIO(audio),
            media_type="audio/wav"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

if old not in text:
    raise RuntimeError("/tts endpoint block not found")

text = text.replace(old, new)

# debugログを消す
text = text.replace(
    '    print("[STYLEBERT DEBUG] queue_assistant_reply_to_speaker called")\n',
    ''
)

path.write_text(text, encoding="utf-8")
print("updated /tts endpoint for Style-Bert-VITS2")
