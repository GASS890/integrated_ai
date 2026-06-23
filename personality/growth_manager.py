from personality.tone_profile import summarize_tone_profile


DEFAULT_GROWTH_STATE = {
    "experience_count": 0,
    "development_assist": 0.0,
    "politeness": 0.0,
    "conciseness": 0.0,
    "detail_orientation": 0.0,
    "stability": 0.0,
    "last_growth_reason": "",
}


def ensure_growth_state(session: dict) -> dict:
    if not isinstance(session, dict):
        return dict(DEFAULT_GROWTH_STATE)

    state = session.get("growth_state")
    if not isinstance(state, dict):
        state = dict(DEFAULT_GROWTH_STATE)
        session["growth_state"] = state

    for key, value in DEFAULT_GROWTH_STATE.items():
        state.setdefault(key, value)

    return state


def _clamp(value: float, min_value: float = 0.0, max_value: float = 10.0) -> float:
    return max(min_value, min(max_value, float(value)))


def _contains_any(text: str, words: list[str]) -> bool:
    return any(w in (text or "") for w in words)


def update_growth_state(session: dict, user_text: str, assistant_text: str = "") -> dict:
    state = ensure_growth_state(session)
    tone = summarize_tone_profile(session)

    user_text = user_text or ""
    assistant_text = assistant_text or ""

    reasons = []

    state["experience_count"] = int(state.get("experience_count", 0)) + 1

    dev_words = [
        "integrated_ai", "ローカルAI", "実装", "改善", "修正", "開発",
        "main.py", "memory", "embedding", "Ollama", "GitHub", "PowerShell"
    ]
    detail_words = [
        "詳しく", "詳細", "理由", "仕組み", "解説", "比較", "手順", "変更箇所"
    ]
    concise_words = [
        "簡潔", "短く", "要点", "次", "結論"
    ]

    if _contains_any(user_text, dev_words):
        state["development_assist"] = _clamp(state.get("development_assist", 0.0) + 0.2)
        reasons.append("開発支援会話が増えた")

    if _contains_any(user_text, detail_words):
        state["detail_orientation"] = _clamp(state.get("detail_orientation", 0.0) + 0.15)
        reasons.append("詳細説明の需要が増えた")

    if _contains_any(user_text, concise_words) or tone.get("detail_level") == "concise":
        state["conciseness"] = _clamp(state.get("conciseness", 0.0) + 0.12)
        reasons.append("簡潔な応答傾向が強まった")

    if tone.get("formality") == "polite":
        state["politeness"] = _clamp(state.get("politeness", 0.0) + 0.1)
        reasons.append("丁寧な会話傾向が強まった")

    state["stability"] = _clamp(state.get("stability", 0.0) + 0.05)

    state["last_growth_reason"] = " / ".join(reasons) if reasons else "通常会話経験を蓄積"

    return state


def summarize_growth_state(session: dict) -> dict:
    state = ensure_growth_state(session)
    return dict(state)


def build_growth_prompt(session: dict) -> str:
    state = ensure_growth_state(session)

    if int(state.get("experience_count", 0)) <= 0:
        return ""

    lines = [
        "【キャラクター成長状態】",
        f"- 会話経験: {int(state.get('experience_count', 0))}",
        f"- 開発補助性: {float(state.get('development_assist', 0.0)):.1f}/10",
        f"- 丁寧さ: {float(state.get('politeness', 0.0)):.1f}/10",
        f"- 簡潔さ: {float(state.get('conciseness', 0.0)):.1f}/10",
        f"- 詳細説明傾向: {float(state.get('detail_orientation', 0.0)):.1f}/10",
        f"- 安定性: {float(state.get('stability', 0.0)):.1f}/10",
        f"- 直近の成長理由: {state.get('last_growth_reason', '')}",
        "",
        "【成長反映ルール】",
        "- 急に人格を変えず、小さく一貫した変化として反映する。",
        "- 価値観や思想は強く変化させない。",
        "- 開発補助性が高い場合、実装手順・安全確認・差分確認を優先する。",
        "- 簡潔さが高い場合、余計な説明を減らす。",
        "- 詳細説明傾向が高い場合、必要な理由や注意点を補う。",
    ]

    return "\\n".join(lines)
