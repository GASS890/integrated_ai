from personality.tone_analyzer import analyze_tone


def _empty_profile() -> dict:
    return {
        "samples": 0,
        "formality": {
            "polite": 0,
            "casual": 0,
            "neutral": 0,
        },
        "detail_level": {
            "detailed": 0,
            "normal": 0,
            "concise": 0,
        },
        "request_style": {
            "direct": 0,
            "question": 0,
            "neutral": 0,
        },
        "avg_sentence_length_total": 0.0,
        "last_features": {},
    }


def ensure_tone_profile(session: dict) -> dict:
    if not isinstance(session, dict):
        return _empty_profile()

    profile = session.get("tone_profile")
    if not isinstance(profile, dict):
        profile = _empty_profile()
        session["tone_profile"] = profile

    return profile


def update_tone_profile(session: dict, user_text: str) -> dict:
    profile = ensure_tone_profile(session)
    features = analyze_tone(user_text)

    profile["samples"] = int(profile.get("samples", 0)) + 1

    for key in ["formality", "detail_level", "request_style"]:
        value = features.get(key, "neutral")
        bucket = profile.get(key, {})
        bucket[value] = int(bucket.get(value, 0)) + 1
        profile[key] = bucket

    profile["avg_sentence_length_total"] = float(
        profile.get("avg_sentence_length_total", 0.0)
    ) + float(features.get("avg_sentence_length", 0.0))

    profile["last_features"] = features

    return profile


def _dominant(bucket: dict, default: str) -> str:
    if not isinstance(bucket, dict) or not bucket:
        return default
    return max(bucket.items(), key=lambda x: x[1])[0]


def summarize_tone_profile(session: dict) -> dict:
    profile = ensure_tone_profile(session)
    samples = max(int(profile.get("samples", 0)), 1)

    return {
        "samples": int(profile.get("samples", 0)),
        "formality": _dominant(profile.get("formality", {}), "neutral"),
        "detail_level": _dominant(profile.get("detail_level", {}), "normal"),
        "request_style": _dominant(profile.get("request_style", {}), "neutral"),
        "avg_sentence_length": float(profile.get("avg_sentence_length_total", 0.0)) / samples,
        "last_features": profile.get("last_features", {}),
    }


def build_tone_prompt(session: dict) -> str:
    summary = summarize_tone_profile(session)

    if summary["samples"] <= 0:
        return ""

    lines = [
        "【相手の口調プロファイル】",
        f"- 丁寧さ: {summary['formality']}",
        f"- 詳細度: {summary['detail_level']}",
        f"- 依頼スタイル: {summary['request_style']}",
        f"- 平均文長: {summary['avg_sentence_length']:.1f}",
        "",
        "【応答調整方針】",
        "- 親密度ではなく、相手の話し方・会話内容に合わせて自然に調整する。",
        "- ただし価値観や思想は強く模倣しない。",
    ]

    if summary["formality"] == "polite":
        lines.append("- 相手が丁寧寄りなので、丁寧で落ち着いた口調を優先する。")
    elif summary["formality"] == "casual":
        lines.append("- 相手がフランク寄りなので、硬すぎない自然な口調に寄せる。")

    if summary["detail_level"] == "concise":
        lines.append("- 相手は短めのやり取りを好む傾向があるため、必要以上に長くしない。")
    elif summary["detail_level"] == "detailed":
        lines.append("- 相手は詳細な説明を扱えるため、必要な根拠や手順を省略しすぎない。")

    if summary["request_style"] == "direct":
        lines.append("- 相手は直接的な依頼が多いため、結論と実行手順を先に出す。")

    return "\\n".join(lines)
