@echo off
chcp 65001 > nul

echo ========================================
echo Style-Bert-VITS2 Launcher
echo ========================================
echo.

cd /d C:\Users\uji_g\Desktop\integrated_ai

echo [1/5] Python環境
call .\.venv_stylebert\Scripts\activate.bat

echo.
echo [2/5] Python確認
python --version

echo.
echo [3/5] Style-Bert-VITS2へ移動
cd .\tools\Style-Bert-VITS2

echo.
echo [4/5] pyopenjtalk Workerは自動起動します

echo.
echo [5/5] Gradio起動
echo.
echo URL:
echo http://127.0.0.1:7860
echo.

python app.py

pause
