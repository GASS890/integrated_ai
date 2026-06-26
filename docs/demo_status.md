# integrated_ai Demo Status

## Current Demo Version

v0.99-test-34-1-demo-status

## Current Goal

一旦、ローカル環境AIを「動くデモ形態」として整理する。

## Current Focus

- 会話できる
- 長期記憶を使える
- Piper Plusで音声生成できる
- Speaker Service経由で音声再生できる
- Queue / Workerでスピーカー処理を分離できる
- 人格・口調学習の基礎がある

## Device Role Plan

### Speaker

耳と口。

- マイク入力
- ウェイクワード検出
- Piper Plus / TTS
- 音声再生
- Speaker Queue
- Speaker Worker

### Camera

目。

- 人・物・表情・姿勢の検出
- 部屋状況の認識
- QR/文字読み取り
- 防犯・見守り用途

### Smartphone

脳・人格・短期記憶・UI。

- 質疑応答LLM
- 人格・口調制御
- 感情状態
- 短期記憶
- 会話状態管理
- 通知・予定
- UI表示

### PC

作業場・長期記憶・重い処理。

- 長期記憶DB
- Embedding検索
- 記憶整理・反省
- ファイル生成
- コード修正AI
- 重いLLM処理
- 音声学習

### Cloud

バックアップ・同期。

- 長期バックアップ
- 複数端末同期
- 外部API
- 復元用データ保存

## Completed Features

### Chat

- FastAPIベースのチャットAPI
- 通常応答
- ストリーミング応答
- セッション管理
- Developer Chat基礎

### Long-term Memory

- Embedding長期記憶
- Ollama Embedding対応
- 類似記憶検索
- 記憶反省処理
- デバッグAPI

### Personality

- 学習強度設定
- 口調学習
- キャラクター成長
- 経験から性格パラメータ変化
- 今後、人格スナップショットと口調レビューを追加予定

### TTS

- VOICEVOX対応
- Piper Plus導入
- Piper Plus専用Python 3.11環境
- tsukuyomiモデル導入
- TTS Router
- TTS Settings
- TTS Status
- UIからTTS切替

### Speaker

- Speaker Service
- Speaker Config
- Speaker State
- Speaker Audio Player
- Speaker Queue
- Speaker Worker
- /speaker/status
- /speaker/say
- /speaker/play
- /speaker/queue
- /speaker/worker

### Demo

- /demo/status
- 現在状態の一括確認
- Git hash / latest tag 確認
- TTS / Speaker / Memory / Personality 状態確認

## Current Demo Check

Use:

Invoke-RestMethod http://127.0.0.1:8000/demo/status

Expected important values:

- demo_ready: True
- tts.default_backend: piper_plus
- tts.backends.piper_plus.ready: True
- memory.embedding_memory_ready: True
- speaker.worker exists

## Near-term Roadmap

### 34-3 start_demo_ai.bat

デモ起動を簡単にする。

### 35-1 character_profile.py

AIの基本人格を整理する。

### 35-2 personality_snapshot.py

現在の人格状態を保存・比較できるようにする。

### 35-3 tone_learning_review.py

ユーザーの口調に合わせる学習結果を確認する。

### 35-4 demo_personality_prompt.py

デモ用の人格プロンプトを整理する。

### 36 AI response to Speaker Queue

AI応答を自動で音声化し、Speaker Queueへ投入する。

### 37 Voice Training Preparation

Style-Bert-VITS2で高品質教師音声を作る準備。

### 38 Piper Plus Custom Voice Training

Piper Plus用の独自音声学習へ進む。

## Current Policy

一旦形にすることを優先する。

そのため、直近では以下を優先する。

1. デモ状態を見える化
2. 起動方法を整理
3. 人格・口調を安定化
4. 音声出力をAI応答に接続
5. その後、音声学習へ進む

## Notes

- 音声学習サンプルはまだ不要。
- Style-Bert-VITS2学習は、人格・口調が安定してから行う。
- Piper Plusは現時点の主力TTS。
- VOICEVOXはフォールバックとして残す。
- 将来はSpeakerを別端末化する。
