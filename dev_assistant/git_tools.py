import subprocess


def get_git_status() -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        return result.stdout.strip()

    except Exception as e:
        return f"[git status error] {e}"


def get_git_diff() -> str:
    try:
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        return result.stdout.strip()

    except Exception as e:
        return f"[git diff error] {e}"