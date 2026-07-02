ENGINES = {
    "voicevox": {
        "role": "fallback",
        "display_name": "VOICEVOX",
        "enabled_setting": "voicevox_enabled",
    },
    "piper": {
        "role": "compat",
        "display_name": "Piper",
        "enabled_setting": "piper_enabled",
    },
    "piper_plus": {
        "role": "primary",
        "display_name": "Piper Plus",
        "enabled_setting": "piper_plus_enabled",
    },
    "auto": {
        "role": "auto",
        "display_name": "Auto",
        "enabled_setting": None,
    },
}


def get_engine_names():
    return list(ENGINES.keys())


def get_engine(name):
    return ENGINES.get(name)


def get_engine_display_name(name):
    engine = get_engine(name)
    if not engine:
        return name
    return engine.get("display_name", name)


def get_engine_enabled_setting(name):
    engine = get_engine(name)
    if not engine:
        return None
    return engine.get("enabled_setting")


def is_engine_enabled(name, settings):
    setting_key = get_engine_enabled_setting(name)
    if setting_key is None:
        return True
    return bool((settings or {}).get(setting_key, False))
