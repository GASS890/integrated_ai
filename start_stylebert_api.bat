@echo off
chcp 65001 > nul

cd /d C:\Users\uji_g\Desktop\integrated_ai

call .\.venv_stylebert\Scripts\activate.bat

cd .\tools\Style-Bert-VITS2

echo ========================================
echo Style-Bert-VITS2 API Server
echo ========================================
echo.
echo URL:
echo http://127.0.0.1:5000
echo.

python server_fastapi.py

pause
