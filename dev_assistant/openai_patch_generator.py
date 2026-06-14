import re

from dev_assistant.pending_patch import PendingPatch
from dev_assistant.project_reader import build_context
from openai_client import chat


PATCH_SYSTEM = """
You are a safe Python code patch generator.

Return ONLY:

target_file:
...

purpose:
...

before_code:
...

after_code:
...

Rules:
- before_code must be copied exactly from the current file.
- after_code must be the replacement for before_code only.
- Change only code directly related to the user request.
- Do not perform formatting-only changes.
- Do not refactor unrelated imports.
- Do not rewrite unrelated code.
- Do not return the whole file.
- Minimize changed lines.
- before_code should be 3 to 80 lines.
- Do not use omitted text.
- Do not use "...".
- Do not use "省略".
- Do not use Markdown.
- Do not use diff format.
- Do not include line numbers such as "1:" in before_code or after_code.
- before_code and after_code must not be identical.
- If there are no duplicate imports, return purpose: no change needed and do not invent changes.
- If the requested change is already done, return the smallest unchanged block and set purpose to "no change needed".
"""

def generate_patch_request(user_request: str, file_paths: list[str]) -> PendingPatch:
    context = build_context(
        file_paths,
        user_request=user_request,
    )

    prompt = f"""
User request:
{user_request}

Target files:
{file_paths}

Current code:
{context}

Return ONLY:

target_file:
...

purpose:
...

before_code:
...

after_code:
...
"""

    result = chat(
        [
            {"role": "system", "content": PATCH_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    print("===== RAW GPT RESPONSE =====")
    print(result)
    print("============================")

    return _parse_patch_text(result)

def _clean_code(text: str) -> str:
    text = text.strip()

    if text.startswith("```python"):
        text = text[len("```python"):].strip()

    if text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        cleaned_line = re.sub(r"^\s*\d+:\s?", "", line)
        cleaned_lines.append(cleaned_line)

    return "\n".join(cleaned_lines).strip()

def _parse_patch_text(text: str) -> PendingPatch:
    if "変更前コード" in text or "変更後コード" in text or "例として" in text:
        raise ValueError("Patch generation failed. Explanation detected.")

    target_file = _extract_between(text, "target_file:", "purpose:").strip()
    purpose = _extract_between(text, "purpose:", "before_code:").strip()

    before_code = _clean_code(
        _extract_between(text, "before_code:", "after_code:")
    )

    after_code = _clean_code(
        text.split("after_code:", 1)[1]
    )

    return PendingPatch(
        target_file=target_file,
        purpose=purpose,
        before_code=before_code,
        after_code=after_code,
        created_by="chatgpt_api",
    )


def _extract_between(text: str, start: str, end: str) -> str:
    if start not in text or end not in text:
        raise ValueError(f"Patch generation failed. Missing marker: {start} or {end}")

    return text.split(start, 1)[1].split(end, 1)[0]