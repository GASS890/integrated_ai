import re


def analyze_tone(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return default_tone_features()

    length = len(text)
    sentences = re.split(r"[。！？!?\\n]+", text)
    sentences = [s for s in sentences if s.strip()]
    sentence_count = max(len(sentences), 1)

    polite_markers = [
        "です", "ます", "ください", "お願いします", "でしょうか",
        "でしょう", "いただけ", "頂け", "くださいませ"
    ]
    casual_markers = [
        "だよ", "だね", "だな", "じゃん", "して", "やって",
        "かな", "かも", "よね", "だろ"
    ]
    command_markers = [
        "して", "やって", "出して", "提示して", "修正して",
        "追加して", "実行して", "お願い"
    ]

    polite_count = sum(text.count(w) for w in polite_markers)
    casual_count = sum(text.count(w) for w in casual_markers)
    command_count = sum(text.count(w) for w in command_markers)

    question_count = text.count("?") + text.count("？")
    exclamation_count = text.count("!") + text.count("！")
    comma_count = text.count("、") + text.count(",")

    avg_sentence_length = length / sentence_count

    if polite_count > casual_count:
        formality = "polite"
    elif casual_count > polite_count:
        formality = "casual"
    else:
        formality = "neutral"

    if avg_sentence_length >= 45:
        detail_level = "detailed"
    elif avg_sentence_length <= 18:
        detail_level = "concise"
    else:
        detail_level = "normal"

    if command_count >= 2:
        request_style = "direct"
    elif question_count >= 1:
        request_style = "question"
    else:
        request_style = "neutral"

    return {
        "formality": formality,
        "detail_level": detail_level,
        "request_style": request_style,
        "length": length,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "polite_count": polite_count,
        "casual_count": casual_count,
        "command_count": command_count,
        "question_count": question_count,
        "exclamation_count": exclamation_count,
        "comma_count": comma_count,
    }


def default_tone_features() -> dict:
    return {
        "formality": "neutral",
        "detail_level": "normal",
        "request_style": "neutral",
        "length": 0,
        "sentence_count": 0,
        "avg_sentence_length": 0,
        "polite_count": 0,
        "casual_count": 0,
        "command_count": 0,
        "question_count": 0,
        "exclamation_count": 0,
        "comma_count": 0,
    }
