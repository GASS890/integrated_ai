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
## 変更履歴

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

