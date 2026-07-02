# integrated_ai

## 実装済み
- FastAPI
- Ollama
- VoiceVox
- Long Memory
- Streaming
- Desktop Mode
- GitHub Version Control

## 次の実装
1. personality分離
2. embedding記憶
3. OpenAI API
4. thinking loop
5. AI同士会話学習

## アーキテクチャ

### config/
アプリ全体の設定値を管理する。FastAPI、Style-Bert、VOICEVOX、Ollamaなどのポート・パスを集約する。

### services/
外部サービスの起動管理を担当する。Service Registry、Service Launcher、Service Pluginで構成する。

### voice/
TTS音声合成を担当する。Voice Engine Registry、Voice Engine Plugin、TTS Routerで構成する。

### personality/
人格・性格・口調・状態の管理を担当する。今後の人格生成フェーズの中心となる。

### memory/
短期記憶・長期記憶・Embedding検索などを担当する。

### static/
GUIフロントエンドを担当する。

### dev_assistant/
Developer Agent関連の変更提案・適用・レビュー処理を担当する。


## 変更履歴

### v0.49.04
- Prompt Context Builder を導入
- rules / personality / memory / summary をラベル付きで統合
- build_messages 内の system context 生成を build_prompt_context に分離
- LLM入力直前の文脈統合を明確化


### v0.49.03
- Persona Manager を導入
- personality/persona_manager.py を追加
- 人格Profile / State / Prompt生成の窓口を統一
- ユーザー編集ファイルは personality_profile.json に統一したまま維持


### v0.49.02
- personality_profile.json を階層構造へ変更
- identity / speech / personality / growth に分割
- 一人称・二人称・語尾・学習速度をJSONで管理可能に変更
- loader.py / prompt_builder.py を階層JSON対応へ更新


### v0.49.01
- Personality JSON化
- personality_profile.json を追加
- loader.py を追加
- PersonalityProfile をJSON読込方式へ変更
- prompt_builder をJSONベースへ変更


### v0.49.00
- 人格生成フェーズを開始
- PersonalityProfile を看板キャラ兼開発補助AI向けに拡張
- PersonalityState に user_tone / conversation_mode を追加
- build_personality_prompt を日本語人格プロンプト形式へ更新


### v0.48.00
- AI基盤完成版として README にアーキテクチャを追加
- personality フォルダの骨組みを作成
- PersonalityProfile / PersonalityState / prompt_builder を追加
- 人格生成フェーズへ入るための土台を整備


### v0.47.05
- Voice Engine Plugin方式へ移行
- voice/engines を追加
- VOICEVOX / Piper / Piper Plus をエンジンプラグイン化
- tts_router.py をエンジンプラグイン経由の合成処理へ整理


### v0.47.04
- Service Plugin方式へ移行
- services/plugins を追加
- Ollama / Style-Bert / VOICEVOX をプラグイン化
- service_launcher.py をPlugin Dispatcherへ変更


### v0.47.03
- Config Registry を導入
- config/app_config.py を追加
- FastAPI / Style-Bert / VOICEVOX / Ollama の基本設定を一元管理
- services/service_launcher.py のパス参照を config 経由へ変更


### v0.47.02
- Startup Manager から Service Launcher を分離
- services/service_launcher.py を追加
- サービス起動処理を一元化
- Startup Manager を起動制御専用に整理

### v0.47.01
- Service Registry を導入
- サービス登録情報を一元管理
- Startup Manager を Registry ベースへ変更

