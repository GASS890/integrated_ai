from personality.setup_manager import is_setup_complete, load_setup_status
from personality.setup_questions import get_setup_questions
from personality.setup_engine import preview_initial_setup, complete_initial_setup


def get_setup_info() -> dict:
    return {
        "setup_complete": is_setup_complete(),
        "status": load_setup_status(),
        "questions": get_setup_questions(),
    }


def preview_setup_answers(answers: dict | None = None) -> dict:
    return preview_initial_setup(answers or {})


def complete_setup_answers(answers: dict | None = None) -> dict:
    return complete_initial_setup(answers or {})
