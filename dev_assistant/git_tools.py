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

def commit_all_changes(message: str) -> str:
    try:
        subprocess.run(
            ["git", "add", "."],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        commit_hash = result.stdout.strip()

        return (
            "Git commit completed.\n"
            f"Commit: {commit_hash}"
        )

    except subprocess.CalledProcessError as e:
        return (
            "Git commit failed.\n"
            f"{e.stderr}"
        )

    except Exception as e:
        return (
            "Git commit failed.\n"
            f"{type(e).__name__}: {e}"
        )