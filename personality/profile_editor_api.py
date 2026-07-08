from personality.profile_manager import (
    get_active_profile_id,
    load_profile_data,
    save_profile_data,
    list_profile_ids,
)


def get_profile_editor_info() -> dict:
    active_profile_id = get_active_profile_id()

    return {
        "active_profile_id": active_profile_id,
        "profile_ids": list_profile_ids(),
        "profile": load_profile_data(active_profile_id),
    }


def save_active_profile(profile_data: dict) -> dict:
    profile_id = get_active_profile_id()
    return save_profile_data(profile_id, profile_data or {})
