SERVICES = {
    "ollama": {
        "enabled": True,
        "autostart": True,
        "type": "command",
    },
    "stylebert": {
        "enabled": True,
        "autostart": True,
        "type": "bat",
    },
    "voicevox": {
        "enabled": True,
        "autostart": True,
        "type": "exe",
        "enabled_setting": "voicevox_enabled",
    },
}


def get_services():
    return SERVICES


def get_service(name):
    return SERVICES.get(name)


def is_service_enabled(name, settings=None):
    service = get_service(name)
    if not service:
        return False

    if not service.get("enabled", False):
        return False

    enabled_setting = service.get("enabled_setting")
    if enabled_setting:
        return bool((settings or {}).get(enabled_setting, False))

    return True


def get_autostart_services(settings=None):
    result = []
    for name, service in SERVICES.items():
        if service.get("autostart", False) and is_service_enabled(name, settings):
            result.append(name)
    return result
