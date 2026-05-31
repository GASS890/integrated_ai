FAST_MODEL = "gemma2:2b"
SMART_MODEL = "qwen2.5:14b"

OPENAI_MODEL_FAST = "gpt-4.1-mini"
OPENAI_MODEL_SMART = "gpt-4.1"

OPTIONS = {
    "fast_chat": {
        "temperature": 0.4,
        "top_p": 0.9,
        "num_predict": 256,
    },
    "smart_chat": {
        "temperature": 0.5,
        "top_p": 0.9,
        "num_predict": 1024,
    },
    "format": {
        "temperature": 0.2,
        "top_p": 0.9,
        "num_predict": 400,
    },
    "summarize": {
        "temperature": 0.2,
        "top_p": 0.9,
        "num_predict": 500,
    },
    "title": {
        "temperature": 0.2,
        "top_p": 0.9,
        "num_predict": 40,
    },
}