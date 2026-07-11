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

### v0.77.00
- Long-term Preference Learning を導入
- personality/preference_history.py を追加
- UserModelのスナップショット履歴を保存可能に変更
- 好みの長期的な増減傾向を算出可能に変更
- 長期傾向をUser Model Promptへ統合


### v0.76.00
- Memory Importance Engine を導入
- memory/importance_engine.py を追加
- memory/importance_store.py を追加
- 記憶へimportanceと判定理由を付与可能に変更
- 重要度順に記憶を取得可能に変更
- importance_memories.jsonをGit管理対象外へ変更


### v0.75.00
- User Preference Detector を導入
- personality/preference_detector.py を追加
- User Modelのスコアから回答形式・説明方法・優先分野を推定可能に変更
- 推定された回答方針をUser Model Promptへ統合
- 現在の明示指示を推定傾向より優先する規則を追加


### v0.74.00
- Growth Rules を導入
- personality/growth_rules.py を追加
- Growth Engineの学習規則を外部ファイルへ分離
- 挨拶 / 短文 / 一時的な応答を学習対象外に変更
- 1発言あたりの最大更新数を制限


### v0.73.00
- Growth Engine を導入
- personality/growth_engine.py を追加
- ユーザー発言から関心 / 好み / 知識レベル / 会話スタイルを更新可能に変更
- キーワード検出による安全なルールベース学習を追加


### v0.72.00
- User Model Prompt Builder を導入
- personality/user_model_prompt.py を追加
- 関心 / 好み / 知識レベル / 会話スタイルをPromptへ反映
- Prompt RouterとPrompt DebuggerへUser Modelを統合


### v0.71.00
- User Model基盤を導入
- personality/user_model.py を追加
- personality/user_model_manager.py を追加
- interests / preferences / knowledge_level / conversation_style をスコア管理可能に変更
- 観測回数を observations に保存可能に変更
- user_model.json をGit管理対象外へ変更


### v0.60.00
- Prompt Debugger API を導入
- prompt/debugger.py を追加
- /prompt/debug で人格Prompt / Memory Prompt / 最終System Contextを確認可能に変更
- LLM送信前のmessages構造を確認可能に変更
- Prompt統合処理の検証基盤を整備


### v0.59.00
- Conversation Context Builder を導入
- prompt/conversation_builder.py を追加
- System Context / History / User Messageの生成処理を分離
- 不正な会話履歴を除外するnormalize_historyを追加
- PromptManagerにbuild_routed_messagesを追加


### v0.58.00
- Prompt Router を導入
- prompt/prompt_router.py を追加
- Rules / Personality / Memory / RuntimeState を一つのPromptBundleへ統合
- LLMへ渡す最終System Contextの生成窓口を追加


### v0.57.00
- Memory Prompt Builder を導入
- memory/prompt_builder.py を追加
- 長期記憶 / 会話要約 / 学習結果 / ユーザー設定を統合可能に変更
- 関係する記憶だけを利用するための指示を追加


### v0.55.00
- Initial Setup Wizard 完全版の入口を導入
- setup_questions.py の質問項目を大幅拡張
- identity / speech / personality / relationship / emotion / growth / advanced / voice を初期設定対象に追加
- choices付き質問に対応
- Setup Wizard UIで input / select を自動切替可能に変更


### v0.54.01
- Profile Editor 保存後の再読込を追加
- /profile/editor/save 後に /profile/editor を再取得
- サーバー側で補正されたProfile内容をGUIへ再反映


### v0.54.00
- Profile Editor GUI 編集フォームを追加
- 人格の基本項目をGUIから編集可能に変更
- 名前 / 役割 / 概要 / 口調 / 一人称 / 学習速度 / 音声設定を編集可能に変更
- /profile/editor/save とGUI保存ボタンを接続


### v0.52.01
- Profile Editor GUI 表示を追加
- 設定パネルから現在の人格Profileを確認可能に変更
- /profile/editor とGUIを接続
- まだ編集保存は行わず、閲覧専用として実装


### v0.52.00
- Profile Editor API を導入
- personality/profile_editor_api.py を追加
- /profile/editor で現在の人格Profileを取得可能に変更
- /profile/editor/save で現在の人格Profileを保存可能に変更
- 人格GUIエディタ導入前のAPI基盤を整備


### v0.51.03
- Setup Wizard UI を導入
- static/index.html に初期設定画面を追加
- 起動時に /setup を確認し、未完了ならWizardを表示
- Wizard中はチャット入力欄とサイドバーを一時非表示化
- /setup/preview / /setup/complete とGUIを接続


### v0.51.02
- Setup API を導入
- personality/setup_api.py を追加
- main.py に /setup API を追加
- /setup で初期設定状態と質問一覧を取得可能に変更
- /setup/preview で回答内容のプレビューを取得可能に変更
- /setup/complete で初期設定を完了可能に変更


### v0.51.01
- Initial Setup Session を導入
- personality/setup_session.py を追加
- personality/setup_questions.py を追加
- personality/setup_validator.py を追加
- personality/setup_engine.py を追加
- Wizardの一問一答方式を実装
- Setup内容のプレビュー機能を追加
- runtime_state.json / setup_status.json をGit管理対象外へ変更


### v0.51.00
- Initial Setup Wizard の基盤を導入
- personality/setup_manager.py を追加
- personality/setup_wizard.py を追加
- personality/templates/default_profile.json を追加
- 初期人格テンプレートをJSONファイルとして分離
- 初期設定状態を setup_status.json で管理可能に変更


### v0.50.02
- ProfileManager を導入
- personality/profiles/default.json を追加
- personality/active_profile.json を追加
- personality/profile_manager.py を追加
- 複数人格・人格切替・人格ごとの音声設定に備えた構造へ変更
- 既存 personality_profile.json を default profile として移行


### v0.50.01
- PersonalityManager を導入
- personality/personality_manager.py を追加
- Profile / RuntimeState の取得窓口を統一
- persona_manager.py を PersonalityManager 経由へ整理
- Initial Setup Wizard 導入前の人格管理基盤を整備


### v0.50.00
- Runtime State Manager を導入
- 既存の personality/state_manager.py は人格学習用として維持
- personality/runtime_state.py を追加
- personality/runtime_manager.py を追加
- mood / energy / confidence / user_tone / conversation_mode を runtime_state.json で管理
- persona_manager.py を RuntimeManager 経由へ更新


### v0.49.07
- PromptManager を導入
- prompt/prompt_manager.py を追加
- PromptContext を追加
- prompts.py をPromptManager経由の互換入口へ整理
- Provider / ContextBuilder / MessageBuilder の統合窓口を追加


### v0.49.06
- Prompt Provider方式へ移行
- prompt/providers を追加
- safety / rule / personality / memory / summary をProvider化
- context_builder.py をProvider集約方式へ整理


### v0.49.05
- Prompt Package化
- prompt/context_builder.py を追加
- prompt/message_builder.py を追加
- prompt/sections.py と prompt/formatter.py を追加
- prompts.py を互換用の薄い入口に整理


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

