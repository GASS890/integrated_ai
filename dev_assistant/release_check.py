from dev_assistant.check_tools import py_compile_all
from dev_assistant.git_tools import (
    get_git_status,
)


def release_check() -> str:
    result = []

    result.append("===== PY_COMPILE =====")
    result.append(py_compile_all())

    result.append("")
    result.append("===== GIT STATUS =====")
    result.append(get_git_status())

    return "\n".join(result)