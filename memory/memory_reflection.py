from memory.embedding_store import add_embedding_memory


def classify_memory_category(user_text: str, ai_text: str = "") -> str:
    text = ((user_text or "") + "\n" + (ai_text or "")).strip()

    tone_keywords = [
        "口調", "話し方", "語尾", "丁寧", "くだけた", "フランク",
        "敬語", "タメ口", "文体", "喋り方"
    ]
    value_keywords = [
        "価値観", "信念", "思想", "考え方", "人生観", "倫理観",
        "正義", "大切にしている"
    ]
    preference_keywords = [
        "好き", "嫌い", "好み", "苦手", "優先", "気に入っている",
        "おすすめ", "選びたい"
    ]
    personality_keywords = [
        "性格", "人格", "キャラ", "キャラクター", "成長", "振る舞い",
        "態度", "雰囲気"
    ]
    dev_keywords = [
        "integrated_ai", "ローカルAI", "実装", "改善", "開発",
        "main.py", "memory", "embedding", "Ollama", "GitHub"
    ]

    if any(k in text for k in tone_keywords):
        return "口調"
    if any(k in text for k in value_keywords):
        return "価値観"
    if any(k in text for k in preference_keywords):
        return "好み"
    if any(k in text for k in personality_keywords):
        return "性格"
    if any(k in text for k in dev_keywords):
        return "開発方針"

    return "conversation_reflection"


def should_store_long_term(user_text: str, ai_text: str = ""):
    text = (user_text or "").strip()
    if len(text) < 8:
        return False

    keywords = [
        "覚えて", "記憶", "今後", "これから", "好み", "好き", "嫌い",
        "設定", "方針", "優先", "目標", "名前", "性格", "口調",
        "ローカルAI", "integrated_ai", "価値観", "話し方", "学習強度"
    ]

    return any(k in text for k in keywords)


def reflect_conversation_to_memory(user_text: str, ai_text: str = "", source: str = "chat"):
    if not should_store_long_term(user_text, ai_text):
        return None

    category = classify_memory_category(user_text, ai_text)

    return add_embedding_memory(
        user_text,
        {
            "source": source,
            "importance": 0.7,
            "type": "conversation_reflection",
            "category": category,
            "embedding_backend": "ollama",
        }
    )
