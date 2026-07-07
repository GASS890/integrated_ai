def validate_answer(question: dict, answer) -> tuple[bool, str]:
    if answer is None or str(answer).strip() == "":
        if question.get("required", False):
            return False, f"{question.get('label', '項目')} は必須です。"
        return True, ""

    choices = question.get("choices")
    if choices and answer not in choices:
        return False, f"{question.get('label', '項目')} は {choices} から選んでください。"

    return True, ""


def validate_answers(questions: list[dict], answers: dict) -> tuple[bool, list[str]]:
    errors = []

    for question in questions:
        key = question.get("key")
        answer = answers.get(key, question.get("default"))
        ok, message = validate_answer(question, answer)

        if not ok:
            errors.append(message)

    return len(errors) == 0, errors
