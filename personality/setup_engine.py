from copy import deepcopy

from personality.setup_questions import get_setup_questions
from personality.setup_validator import validate_answers
from personality.setup_wizard import get_default_setup_template, apply_initial_setup


def _set_nested_value(data: dict, dotted_key: str, value):
    keys = dotted_key.split(".")
    current = data

    for key in keys[:-1]:
        current = current.setdefault(key, {})

    current[keys[-1]] = value


def build_profile_from_answers(answers: dict) -> dict:
    profile = deepcopy(get_default_setup_template())
    questions = get_setup_questions()

    for question in questions:
        key = question["key"]
        value = answers.get(key, question.get("default"))
        _set_nested_value(profile, key, value)

    return profile


def preview_initial_setup(answers: dict | None = None) -> dict:
    answers = answers or {}
    questions = get_setup_questions()
    ok, errors = validate_answers(questions, answers)

    if not ok:
        return {
            "ok": False,
            "errors": errors,
            "profile": None,
        }

    return {
        "ok": True,
        "errors": [],
        "profile": build_profile_from_answers(answers),
    }


def complete_initial_setup(answers: dict | None = None) -> dict:
    preview = preview_initial_setup(answers)

    if not preview["ok"]:
        return preview

    profile = apply_initial_setup(preview["profile"])

    return {
        "ok": True,
        "errors": [],
        "profile": profile,
    }
