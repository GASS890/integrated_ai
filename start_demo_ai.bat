@echo off
chcp 65001 > nul

echo ========================================
echo integrated_ai Demo Start
echo ========================================
echo.

cd /d C:\Users\uji_g\Desktop\integrated_ai

echo [1/6] Python確認
python --version
echo.

echo [2/6] Ollama状態確認
powershell -Command "try { Invoke-RestMethod http://127.0.0.1:11434/api/tags | Out-Null; Write-Host 'Ollama: OK' } catch { Write-Host 'Ollama: NG - Ollamaを起動してください' }"
echo.

echo [3/6] Piper Plus確認
python test_piper_plus_client.py
echo.

echo [4/6] Demo Status確認
powershell -Command "Write-Host 'FastAPI起動後に確認できます: http://127.0.0.1:8000/demo/status'"
echo.

echo [5/6] integrated_ai 起動
echo FastAPIを起動します。
echo 終了する場合は Ctrl + C
echo.

python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause
