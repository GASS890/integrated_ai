from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

insert_after = '''@app.get("/tts/status")
def tts_status():
    return get_tts_status()


'''

new_block = '''@app.get("/stylebert/models")
def stylebert_models():
    root = Path("tools/Style-Bert-VITS2/model_assets")
    models = []

    if root.exists():
        for i, item in enumerate(sorted(root.iterdir(), key=lambda p: p.name.lower())):
            if not item.is_dir():
                continue

            has_config = (item / "config.json").exists()
            has_style = (item / "style_vectors.npy").exists()
            model_files = list(item.glob("*.safetensors")) + list(item.glob("*.pth"))

            models.append({
                "model_id": i,
                "name": item.name,
                "path": str(item),
                "has_config": has_config,
                "has_style_vectors": has_style,
                "model_file_count": len(model_files),
                "ready": has_config and has_style and len(model_files) > 0,
            })

    config = load_speaker_config()

    return {
        "status": "ok",
        "selected_model_id": int(config.get("stylebert_model_id", 0)),
        "selected_model_name": config.get("stylebert_model_name", ""),
        "models": models,
    }


@app.post("/stylebert/select")
def stylebert_select(req: dict):
    config = load_speaker_config()
    models_info = stylebert_models()
    models = models_info.get("models", [])

    model_id = req.get("model_id", None)
    model_name = req.get("model_name", None)

    selected = None

    if model_name:
        for m in models:
            if m["name"] == model_name:
                selected = m
                break

    elif model_id is not None:
        model_id = int(model_id)
        for m in models:
            if int(m["model_id"]) == model_id:
                selected = m
                break

    if selected is None:
        raise HTTPException(status_code=404, detail="Style-Bert-VITS2 model not found")

    config["tts_backend"] = "style_bert_vits2"
    config["stylebert_model_id"] = int(selected["model_id"])
    config["stylebert_model_name"] = selected["name"]
    config["stylebert_speaker_id"] = int(req.get("speaker_id", config.get("stylebert_speaker_id", 0)))
    config["stylebert_style"] = req.get("style", config.get("stylebert_style", "Neutral"))
    config["stylebert_style_weight"] = float(req.get("style_weight", config.get("stylebert_style_weight", 5.0)))
    config["stylebert_length"] = float(req.get("length", config.get("stylebert_length", 1.0)))

    update_speaker_config(config)

    return {
        "status": "ok",
        "selected": selected,
        "config": load_speaker_config(),
    }


'''

if insert_after not in text:
    raise RuntimeError("insert point not found")

text = text.replace(insert_after, insert_after + new_block)

path.write_text(text, encoding="utf-8")
print("Style-Bert model switch API added")
