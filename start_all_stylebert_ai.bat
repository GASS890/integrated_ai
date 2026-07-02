@echo off
cd /d %~dp0

echo Starting Style-Bert-VITS2 API...
start "Style-Bert API" cmd /k "cd /d tools\Style-Bert-VITS2 && python server_fastapi.py"

timeout /t 5 /nobreak > nul

echo Starting integrated_ai desktop...
call start_desktop_ai.bat
