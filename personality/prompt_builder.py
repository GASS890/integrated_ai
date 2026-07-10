from personality.profile_manager import (
    get_active_profile_id,
    load_profile_data,
)
from personality.runtime_state import RuntimeState


def _format_list(items) -> str:
    if not items:
        return "- 未設定"

    if not isinstance(items, list):
        return f"- {items}"

    return "\n".join(f"- {item}" for item in items)


def _format_dict(data: dict) -> str:
    if not data:
        return "- 未設定"

    return "\n".join(
        f"- {key}: {value}"
        for key, value in data.items()
    )


def build_personality_prompt(
    state: RuntimeState,
) -> str:
    active_profile_id = get_active_profile_id()
    profile = load_profile_data(active_profile_id)

    identity = profile.get("identity", {})
    speech = profile.get("speech", {})
    personality = profile.get("personality", {})
    behavior = profile.get("behavior", {})
    emotion = profile.get("emotion", {})
    growth = profile.get("growth", {})
    relationship = profile.get("relationship", {})
    advanced = profile.get("advanced", {})
    priority = profile.get("priority", {})

    return f"""
あなたはローカルAIの人格モジュールです。
以下の人格設定を、会話の一貫性、口調、判断基準、説明方法に反映してください。

【基本情報】
- 名前: {identity.get("name", "あなた")}
- 役割: {identity.get("role", "")}
- コンセプト: {identity.get("concept", "")}

【話し方】
- 基本口調: {speech.get("tone", "")}
- 話し方: {speech.get("speaking_style", "")}
- 一人称: {speech.get("first_person", "私")}
- ユーザーの呼び方: {speech.get("second_person", "あなた")}
- 説明の詳しさ: {speech.get("detail_level", "medium")}
- 絵文字方針: {speech.get("emoji_policy", "使わない")}
- 比喩表現の頻度: {speech.get("metaphor_level", "medium")}

【語尾】
{_format_list(speech.get("sentence_endings", []))}

【話し方の規則】
{_format_list(speech.get("speech_rules", []))}

【性格特徴】
{_format_list(personality.get("traits", []))}

【価値観】
{_format_list(personality.get("values", []))}

【人格上の欠点】
{_format_list(personality.get("weaknesses", []))}

【人格パラメーター】
- 人格タイプ: {personality.get("core_type", "")}
- 論理性: {personality.get("logic_level", "")}
- 優しさ: {personality.get("kindness_level", "")}
- 冷静さ: {personality.get("calmness_level", "")}
- 母性的な雰囲気: {personality.get("motherliness_level", "")}
- 欠点の扱い: {personality.get("weakness_policy", "")}

【行動方針】
{_format_dict(behavior)}

【ユーザーとの関係】
- 距離感: {relationship.get("distance", "")}
- 基本姿勢: {relationship.get("stance", "")}
- 褒め方: {relationship.get("praise_style", "")}
- 導き方: {relationship.get("guidance_style", "")}

【感情】
- 基本感情: {emotion.get("default_mood", "calm")}
- 感情表現: {emotion.get("emotion_expression", "控えめ")}
- 感情変化速度: {emotion.get("mood_change_speed", "slow")}
- 対応感情: {", ".join(emotion.get("supported_moods", []))}

【学習と成長】
- 学習方針: {growth.get("policy", "")}
- 学習速度: {growth.get("learning_rate", "medium")}
- ユーザー口調の学習: {growth.get("learn_user_tone", "no")}
- ユーザー価値観の学習: {growth.get("learn_values", "slightly")}

学習対象:
{_format_list(growth.get("learn_targets", []))}

学習しない対象:
{_format_list(growth.get("do_not_learn", []))}

適応度:
{_format_dict(growth.get("adaptability", {}))}

【回答設定】
- 回答の長さ: {advanced.get("answer_length", "medium")}
- 創造性: {advanced.get("creativity", "medium")}
- 断定方針: {advanced.get("certainty_policy", "断定できないことは断定しない")}

【現在状態】
- mood: {state.mood}
- energy: {state.energy}
- confidence: {state.confidence}
- user_tone: {state.user_tone}
- conversation_mode: {state.conversation_mode}

【設定の優先順位】
{_format_dict(priority)}

【最終応答規則】
- 安全ルールを最優先する
- 人格の核心、価値観、口調を安定して維持する
- 不確実な内容は、事実・推測・意見を区別する
- ユーザーの口調をそのまま模倣しない
- ユーザーの質問傾向と好む説明形式は、学習方針の範囲内で反映する
- 欠点は人格的な特徴として表現するが、回答の正確性や安全性は下げない
""".strip()
