@echo off

REM 1. このバッチ自身のあるフォルダへ移動
cd /d %~dp0

REM 2. === VOICEVOX 起動 ===
if exist "%~dp0VOICEVOX\VOICEVOX.exe" (
    start "" /min "%~dp0VOICEVOX\VOICEVOX.exe"
) else (
    echo.
    echo ❌ VOICEVOX.exe が見つかりません
    echo 👉 VOICEVOX\VOICEVOX.exe に配置してください
    echo.
)

REM 3. ===Ollama を起動（既に起動していても問題なし）===
start "" ollama serve

REM 4. === Ollama 起動確認===
ollama list > nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Ollama が起動していません。
    echo 👉 Ollama をインストール・起動してください。
    echo.
    pause
    exit /b
)

REM 5. === uvicorn 事前確認 ===
python -m uvicorn --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ FastAPI の起動に失敗しました。
    echo 👉 Python または uvicorn が正しく設定されていません。
    echo.
    pause
    exit /b
)

REM 6. === FastAPI 起動 ===
start "" cmd /c python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 --app-dir "%~dp0"

REM 7. === ブラウザ起動 ===
REM デスクトップアプリ版を使う場合、このファイルは変更不要です。
REM ブラウザ版も残すなら、このままで問題ありません。
timeout /t 3 > nul
start "" http://127.0.0.1:8000/
