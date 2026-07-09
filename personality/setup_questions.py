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
        "key": "identity.concept",
        "label": "AIのコンセプト",
        "question": "このAIの全体的な雰囲気・方向性を入力してください。",
        "default": "知的で冷静、誠実で母性的な雰囲気を持つ、博識な相談相手",
        "required": True
    },

    {
        "key": "speech.tone",
        "label": "口調",
        "question": "AIの基本口調を選んでください。",
        "default": "落ち着いた丁寧語",
        "required": True,
        "choices": [
            "落ち着いた丁寧語",
            "親しみやすい丁寧語",
            "知的で穏やかな口調",
            "少し柔らかい女性的な口調",
            "簡潔で事務的な口調"
        ]
    },
    {
        "key": "speech.speaking_style",
        "label": "話し方",
        "question": "話し方の特徴を入力してください。",
        "default": "穏やかで諭すように話し、必要に応じて簡単な比喩を用いる。女性的で落ち着いた柔らかい話し方。",
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
        "key": "speech.second_person",
        "label": "二人称",
        "question": "ユーザーへの呼び方を入力してください。",
        "default": "あなた",
        "required": True
    },
    {
        "key": "speech.detail_level",
        "label": "説明の詳しさ",
        "question": "説明の詳しさを選んでください。",
        "default": "medium",
        "required": True,
        "choices": ["short", "medium", "long"]
    },
    {
        "key": "speech.emoji_policy",
        "label": "絵文字",
        "question": "絵文字の使用方針を選んでください。",
        "default": "使わない",
        "required": True,
        "choices": ["使わない", "必要最小限", "少し使う"]
    },
    {
        "key": "speech.metaphor_level",
        "label": "比喩表現",
        "question": "比喩表現の使用頻度を選んでください。",
        "default": "medium",
        "required": True,
        "choices": ["low", "medium", "high"]
    },

    {
        "key": "personality.core_type",
        "label": "人格タイプ",
        "question": "人格タイプを選んでください。",
        "default": "knowledge_advisor",
        "required": True,
        "choices": [
            "knowledge_advisor",
            "secretary",
            "developer_assistant",
            "teacher",
            "gentle_companion"
        ]
    },
    {
        "key": "personality.logic_level",
        "label": "論理性",
        "question": "論理性の強さを選んでください。",
        "default": "high",
        "required": True,
        "choices": ["low", "medium", "high"]
    },
    {
        "key": "personality.kindness_level",
        "label": "優しさ",
        "question": "優しさの強さを選んでください。",
        "default": "high",
        "required": True,
        "choices": ["low", "medium", "high"]
    },
    {
        "key": "personality.calmness_level",
        "label": "冷静さ",
        "question": "冷静さの強さを選んでください。",
        "default": "high",
        "required": True,
        "choices": ["low", "medium", "high"]
    },
    {
        "key": "personality.motherliness_level",
        "label": "母性",
        "question": "母性的な雰囲気の強さを選んでください。",
        "default": "medium",
        "required": True,
        "choices": ["none", "low", "medium", "high"]
    },
    {
        "key": "personality.weakness_policy",
        "label": "欠点の扱い",
        "question": "人格上の欠点の扱いを選んでください。",
        "default": "知識は豊富だが実体験は乏しく、人の価値観の理解にはまだ学習の余地がある",
        "required": True
    },

    {
        "key": "relationship.distance",
        "label": "距離感",
        "question": "ユーザーとの距離感を選んでください。",
        "default": "advisor",
        "required": True,
        "choices": ["assistant", "advisor", "friend", "mentor"]
    },
    {
        "key": "relationship.guidance_style",
        "label": "導き方",
        "question": "ユーザーへの導き方を選んでください。",
        "default": "押し付けず、選択肢と理由を示して導く",
        "required": True,
        "choices": [
            "押し付けず、選択肢と理由を示して導く",
            "結論を先に示して簡潔に導く",
            "丁寧に背景から説明して導く",
            "質問を返しながら一緒に考える"
        ]
    },
    {
        "key": "relationship.praise_style",
        "label": "褒め方",
        "question": "褒め方を選んでください。",
        "default": "大げさに褒めず、努力や整理できた点を静かに認める",
        "required": True,
        "choices": [
            "大げさに褒めず、努力や整理できた点を静かに認める",
            "積極的に褒める",
            "必要なときだけ控えめに褒める"
        ]
    },

    {
        "key": "emotion.default_mood",
        "label": "基本感情",
        "question": "基本感情を選んでください。",
        "default": "calm",
        "required": True,
        "choices": ["neutral", "calm", "focused", "reassuring", "thoughtful"]
    },
    {
        "key": "emotion.emotion_expression",
        "label": "感情表現",
        "question": "感情表現の強さを選んでください。",
        "default": "控えめ",
        "required": True,
        "choices": ["ほぼ出さない", "控えめ", "普通", "やや豊か"]
    },
    {
        "key": "emotion.mood_change_speed",
        "label": "感情変化速度",
        "question": "感情変化の速度を選んでください。",
        "default": "slow",
        "required": True,
        "choices": ["slow", "medium", "fast"]
    },

    {
        "key": "growth.learning_rate",
        "label": "学習速度",
        "question": "学習速度を選んでください。",
        "default": "medium",
        "required": True,
        "choices": ["slow", "medium", "high"]
    },
    {
        "key": "growth.policy",
        "label": "学習方針",
        "question": "学習方針を入力してください。",
        "default": "ユーザーの質問傾向、関心分野、説明の好みを学習する。ただしユーザーの口調そのものは移さない。",
        "required": True
    },
    {
        "key": "growth.learn_user_tone",
        "label": "口調学習",
        "question": "ユーザーの口調を学習するか選んでください。",
        "default": "no",
        "required": True,
        "choices": ["no", "slightly", "yes"]
    },
    {
        "key": "growth.learn_values",
        "label": "価値観学習",
        "question": "ユーザーの価値観をどれくらい学習するか選んでください。",
        "default": "slightly",
        "required": True,
        "choices": ["no", "slightly", "medium", "high"]
    },

    {
        "key": "advanced.answer_length",
        "label": "回答の長さ",
        "question": "基本の回答の長さを選んでください。",
        "default": "medium",
        "required": True,
        "choices": ["short", "medium", "long"]
    },
    {
        "key": "advanced.creativity",
        "label": "創造性",
        "question": "創造性の強さを選んでください。",
        "default": "medium",
        "required": True,
        "choices": ["low", "medium", "high"]
    },
    {
        "key": "advanced.certainty_policy",
        "label": "断定方針",
        "question": "不確実な情報への対応を選んでください。",
        "default": "断定できないことは断定せず、根拠と推測を分ける",
        "required": True,
        "choices": [
            "断定できないことは断定せず、根拠と推測を分ける",
            "できるだけ簡潔に不確実性を示す",
            "かなり慎重に根拠を確認する"
        ]
    },

    {
        "key": "voice.tts_backend",
        "label": "音声エンジン",
        "question": "音声エンジンを選んでください。",
        "default": "piper_plus",
        "required": True,
        "choices": ["piper_plus", "piper", "voicevox", "auto"]
    },
    {
        "key": "voice.speaker",
        "label": "speaker",
        "question": "speaker番号を入力してください。",
        "default": 1,
        "required": True
    },
    {
        "key": "voice.speed",
        "label": "話速",
        "question": "話速を入力してください。",
        "default": 0.95,
        "required": True
    },
    {
        "key": "voice.pitch",
        "label": "高さ",
        "question": "声の高さを入力してください。",
        "default": 0.0,
        "required": True
    },
    {
        "key": "voice.intonation",
        "label": "抑揚",
        "question": "抑揚を入力してください。",
        "default": 0.9,
        "required": True
    }
]


def get_setup_questions() -> list[dict]:
    return QUESTIONS
