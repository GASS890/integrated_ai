import subprocess
import logging

logger = logging.getLogger(__name__)


def get_git_status() -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        logger.debug("git status output: %s", result.stdout.strip())
        return result.stdout.strip()

    except Exception as e:
        logger.error("git status error: %s", e, exc_info=True)
        return f"[git status error] {e}"


def get_git_diff() -> str:
    try:
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        logger.debug("git diff output: %s", result.stdout.strip())
        return result.stdout.strip()

    except Exception as e:
        logger.error("git diff error: %s", e, exc_info=True)
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
        logger.info("git add . executed successfully")

        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        logger.info("git commit executed successfully with message: %s", message)

        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        commit_hash = result.stdout.strip()
        logger.info("git commit hash: %s", commit_hash)

        return (
            "Git commit completed.\n"
            f"Commit: {commit_hash}"
        )

    except subprocess.CalledProcessError as e:
        logger.error("Git commit failed: %s", e.stderr, exc_info=True)
        return (
            "Git commit failed.\n"
            f"{e.stderr}"
        )

    except Exception as e:
        logger.error("Git commit failed: %s", e, exc_info=True)
        return (
            "Git commit failed.\n"
            f"{type(e).__name__}: {e}"
        )


def push_to_origin() -> str:
    try:
        result = subprocess.run(
            ["git", "push"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        logger.info("git push executed successfully")
        logger.debug("git push output: %s", result.stdout.strip())

        return (
            "Git push completed.\n"
            f"{result.stdout.strip()}"
        )

    except subprocess.CalledProcessError as e:
        logger.error("Git push failed: %s", e.stderr, exc_info=True)
        return (
            "Git push failed.\n"
            f"{e.stderr}"
        )

    except Exception as e:
        logger.error("Git push failed: %s", e, exc_info=True)
        return (
            "Git push failed.\n"
            f"{type(e).__name__}: {e}"
        )