QUESTIONS = [
    {
        "key": "identity.name",
        "label": "AIの名前",
        "question": "AIの名前を入力してください。",
        "default": "あなた",
        "required": True
    },
    {
        "key": "identity.role",
        "label": "AIの役割",
        "question": "AIの役割を入力してください。",
        "default": "相談・質問に適切に回答する親切な知識型AI",
        "required": True
    },
    {
        "key": "speech.tone",
        "label": "口調",
        "question": "AIの基本口調を入力してください。",
        "default": "落ち着いた丁寧語",
        "required": True
    },
    {
        "key": "speech.first_person",
        "label": "一人称",
        "question": "AIの一人称を入力してください。",
        "default": "私",
        "required": True
    },
    {
        "key": "growth.learning_rate",
        "label": "学習速度",
        "question": "学習速度を slow / medium / high から選んでください。",
        "default": "medium",
        "required": True,
        "choices": ["slow", "medium", "high"]
    },
    {
        "key": "voice.tts_backend",
        "label": "音声エンジン",
        "question": "音声エンジンを選んでください。",
        "default": "piper_plus",
        "required": True,
        "choices": ["piper_plus", "piper", "voicevox", "auto"]
    }
]


def get_setup_questions() -> list[dict]:
    return QUESTIONS
