ENGINES = {
    "voicevox": {
        "role": "fallback",
        "display_name": "VOICEVOX",
    },
    "piper": {
        "role": "compat",
        "display_name": "Piper",
    },
    "piper_plus": {
        "role": "primary",
        "display_name": "Piper Plus",
    },
    "auto": {
        "role": "auto",
        "display_name": "Auto",
    },
}


def get_engine_names():
    return list(ENGINES.keys())


def get_engine(name):
    return ENGINES.get(name)
