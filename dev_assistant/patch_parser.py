from __future__ import annotations

import re

from dev_assistant.pending_patch import PendingPatch


def parse_patch_response(text: str) -> PendingPatch | None:
    target = _extract_section(
        text,
        "変更対象ファイル",
    )

    purpose = _extract_section(
        text,
        "変更目的",
    )

    before_code = _extract_code_block_after(
        text,
        "変更前コード",
    )

    after_code = _extract_code_block_after(
        text,
        "変更後コード",
    )

    if not (
        target
        and before_code
        and after_code
    ):
        return None

    return PendingPatch(
        target_file=target.strip(),
        purpose=purpose.strip(),
        before_code=before_code,
        after_code=after_code,
    )


def _extract_section(
    text: str,
    title: str,
) -> str:
    pattern = rf"{title}\s*[:：]?\s*(.+)"
    m = re.search(pattern, text)

    return m.group(1).strip() if m else ""


def _extract_code_block_after(
    text: str,
    title: str,
) -> str:
    pattern = (
        rf"{title}.*?```(?:python)?\n"
        rf"(.*?)```"
    )

    m = re.search(
        pattern,
        text,
        re.DOTALL,
    )

    return m.group(1).strip() if m else ""