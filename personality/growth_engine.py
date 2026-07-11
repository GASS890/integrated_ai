from personality.growth_rules import (
    GROWTH_RULES,
    IGNORE_EXACT_TEXTS,
    IGNORE_PREFIXES,
    MAX_UPDATES_PER_MESSAGE,
    MIN_TEXT_LENGTH,
)
from personality.user_model_manager import update_score


def _contains_any(
    text: str,
    keywords: list[str],
) -> bool:
    lowered = text.lower()

    return any(
        keyword.lower() in lowered
        for keyword in keywords
    )


def should_observe_text(
    user_text: str,
) -> tuple[bool, str]:
    text = str(user_text or "").strip()

    if not text:
        return False, "empty_text"

    if len(text) < MIN_TEXT_LENGTH:
        return False, "too_short"

    if text in IGNORE_EXACT_TEXTS:
        return False, "ignored_exact_text"

    if any(
        text.startswith(prefix)
        for prefix in IGNORE_PREFIXES
    ):
        return False, "ignored_greeting"

    return True, ""


def observe_user_text(
    user_text: str,
) -> dict:
    text = str(user_text or "").strip()

    should_observe, reason = should_observe_text(text)

    if not should_observe:
        return {
            "observed": False,
            "reason": reason,
            "updates": [],
        }

    updates = []

    for category, rule in GROWTH_RULES.items():
        amount = float(rule.get("amount", 0.01))
        keywords_map = rule.get("keywords", {})

        for key, keywords in keywords_map.items():
            if len(updates) >= MAX_UPDATES_PER_MESSAGE:
                break

            if not _contains_any(text, keywords):
                continue

            updates.append(
                update_score(
                    category=category,
                    key=key,
                    amount=amount,
                )
            )

        if len(updates) >= MAX_UPDATES_PER_MESSAGE:
            break

    return {
        "observed": True,
        "text_length": len(text),
        "updates": updates,
        "update_count": len(updates),
    }
