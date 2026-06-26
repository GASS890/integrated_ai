# Demo Startup

## start_demo_ai.bat

デモ用起動ファイル。

実行内容:

1. Python確認
2. Ollama状態確認
3. Piper Plus確認
4. demo/status確認案内
5. FastAPI起動

## check_demo_status.bat

FastAPI起動後に状態確認するためのbat。

確認対象:

- /demo/status
- /speaker/status
- /tts/status

## Usage

1. start_demo_ai.bat を起動
2. ブラウザで http://127.0.0.1:8000 を開く
3. 必要なら check_demo_status.bat を起動

## Notes

- Ollamaは別途起動済みが望ましい。
- Piper Plusは .venv_piper_plus と tools/piper-plus が必要。
- VOICEVOXはフォールバック用。
