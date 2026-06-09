from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PatchScore:
    safety: int
    maintainability: int
    scope: int
    total: float
    reason: str

    def render(self) -> str:
        return (
            "Patch score\n"
            f"- Safety: {self.safety}/10\n"
            f"- Maintainability: {self.maintainability}/10\n"
            f"- Scope control: {self.scope}/10\n"
            f"- Total: {self.total:.1f}/10\n\n"
            f"Reason:\n{self.reason}"
        )


def score_patch(
    purpose: str,
    before_code: str,
    after_code: str,
) -> PatchScore:
    safety = 10
    maintainability = 10
    scope = 10
    reasons: list[str] = []

    before_len = len(before_code)
    after_len = len(after_code)
    size_diff = abs(after_len - before_len)

    if not before_code.strip():
        safety -= 2
        reasons.append("Before code is empty.")

    if not after_code.strip():
        safety -= 4
        maintainability -= 2
        reasons.append("After code is empty.")

    if size_diff > 2000:
        scope -= 3
        reasons.append("Patch size difference is large.")

    elif size_diff > 800:
        scope -= 1
        reasons.append("Patch size difference is moderate.")

    risky_keywords = [
        "eval(",
        "exec(",
        "subprocess.run",
        "os.system",
        "shutil.rmtree",
        "delete",
        "remove",
        "api_key",
        "password",
        "secret",
        "token",
    ]

    added_text = _diff_added_text(
        before_code=before_code,
        after_code=after_code,
    )

    for keyword in risky_keywords:
        if keyword.lower() in added_text.lower():
            safety -= 2
            reasons.append(f"Risky keyword added: {keyword}")

    if _line_count(after_code) > _line_count(before_code) + 80:
        scope -= 2
        maintainability -= 1
        reasons.append("Patch adds many lines.")

    if _has_large_indentation_change(before_code, after_code):
        maintainability -= 2
        reasons.append("Indentation structure changed significantly.")

    if _contains_broad_exception(after_code) and not _contains_broad_exception(before_code):
        maintainability -= 1
        reasons.append("Broad exception handling was added.")

    safety = _clamp_score(safety)
    maintainability = _clamp_score(maintainability)
    scope = _clamp_score(scope)

    total = round(
        (safety + maintainability + scope) / 3,
        1,
    )

    if not reasons:
        reasons.append("No obvious risk was detected by the local heuristic scorer.")

    return PatchScore(
        safety=safety,
        maintainability=maintainability,
        scope=scope,
        total=total,
        reason="\n".join(f"- {reason}" for reason in reasons),
    )


def _diff_added_text(
    before_code: str,
    after_code: str,
) -> str:
    before_lines = set(before_code.splitlines())
    added_lines = [
        line
        for line in after_code.splitlines()
        if line not in before_lines
    ]

    return "\n".join(added_lines)


def _line_count(text: str) -> int:
    return len(text.splitlines())


def _has_large_indentation_change(
    before_code: str,
    after_code: str,
) -> bool:
    before_indent = _average_indent(before_code)
    after_indent = _average_indent(after_code)

    return abs(after_indent - before_indent) >= 4


def _average_indent(text: str) -> float:
    lines = [
        line
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return 0.0

    indents = [
        len(line) - len(line.lstrip(" "))
        for line in lines
    ]

    return sum(indents) / len(indents)


def _contains_broad_exception(text: str) -> bool:
    return (
        "except Exception" in text
        or "except:" in text
    )


def _clamp_score(score: int) -> int:
    return max(1, min(10, score))