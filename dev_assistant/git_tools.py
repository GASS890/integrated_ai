import logging
import subprocess

logger = logging.getLogger(__name__)


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
        logger.error("git status error: %s", e, exc_info=True)
        return f"[git status error] {e}"


def get_git_diff(target_file: str | None = None) -> str:
    try:
        cmd = ["git", "diff"]

        if target_file:
            cmd += ["--", target_file]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    except Exception as e:
        logger.error("git diff error: %s", e, exc_info=True)
        return f"[git diff error] {e}"


def get_git_diff_for_files(file_paths: list[str]) -> str:
    parts = []

    for path in file_paths:
        diff = get_git_diff(path)
        parts.append(
            f"===== Git Diff: {path} =====\n"
            f"{diff or '(no diff)'}"
        )

    return "\n\n".join(parts)


def get_current_commit_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        logger.error("Get commit hash failed: %s", e.stderr, exc_info=True)
        return ""


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

        commit_hash = get_current_commit_hash()

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


def git_tag_exists(version: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "tag", "--list", version],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip() == version

    except subprocess.CalledProcessError:
        return False


def suggest_next_version(version: str) -> str:
    index = 1

    while git_tag_exists(f"{version}-{index}"):
        index += 1

    return f"{version}-{index}"


def create_git_tag(version: str) -> str:
    try:
        if git_tag_exists(version):
            return f"Git tag already exists: {version}"

        subprocess.run(
            ["git", "tag", version],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        return f"Git tag created: {version}"

    except subprocess.CalledProcessError as e:
        return (
            "Git tag failed.\n"
            f"{e.stderr}"
        )


def delete_git_tag(version: str) -> str:
    try:
        subprocess.run(
            ["git", "tag", "-d", version],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        return f"Git tag deleted locally: {version}"

    except subprocess.CalledProcessError as e:
        return (
            "Git tag delete failed.\n"
            f"{e.stderr}"
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

        return (
            "Git push completed.\n"
            f"{result.stdout.strip()}"
        )

    except subprocess.CalledProcessError as e:
        return (
            "Git push failed.\n"
            f"{e.stderr}"
        )

    except Exception as e:
        return (
            "Git push failed.\n"
            f"{type(e).__name__}: {e}"
        )


def push_git_tag(version: str) -> str:
    try:
        subprocess.run(
            ["git", "push", "origin", version],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        return f"Git tag pushed: {version}"

    except subprocess.CalledProcessError as e:
        return (
            "Git tag push failed.\n"
            f"{e.stderr}"
        )