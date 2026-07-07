from personality.setup_engine import complete_initial_setup, preview_initial_setup
from personality.setup_questions import get_setup_questions
from personality.setup_validator import validate_answer


class SetupSession:
    def __init__(self):
        self.questions = get_setup_questions()
        self.index = 0
        self.answers = {}
        self.completed = False

    def current_question(self) -> dict | None:
        if self.completed:
            return None

        if self.index >= len(self.questions):
            return None

        return self.questions[self.index]

    def progress(self) -> dict:
        return {
            "current": min(self.index + 1, len(self.questions)),
            "total": len(self.questions),
            "completed": self.completed,
        }

    def answer(self, value) -> dict:
        question = self.current_question()

        if question is None:
            return {
                "ok": False,
                "error": "質問はすでに完了しています。",
                "next_question": None,
                "progress": self.progress(),
            }

        ok, message = validate_answer(question, value)
        if not ok:
            return {
                "ok": False,
                "error": message,
                "next_question": question,
                "progress": self.progress(),
            }

        self.answers[question["key"]] = value
        self.index += 1

        next_question = self.current_question()

        if next_question is None:
            self.completed = True

        return {
            "ok": True,
            "error": "",
            "next_question": next_question,
            "progress": self.progress(),
        }

    def preview(self) -> dict:
        return preview_initial_setup(self.answers)

    def complete(self) -> dict:
        if not self.completed:
            return {
                "ok": False,
                "errors": ["初期設定の質問がまだ完了していません。"],
                "profile": None,
            }

        return complete_initial_setup(self.answers)
