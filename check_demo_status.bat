@echo off
chcp 65001 > nul

echo ========================================
echo integrated_ai Demo Check
echo ========================================
echo.

echo [1] demo/status
powershell -Command "try { Invoke-RestMethod http://127.0.0.1:8000/demo/status } catch { Write-Host 'demo/status確認失敗。先に start_demo_ai.bat を起動してください。' }"

echo.
echo [2] speaker/status
powershell -Command "try { Invoke-RestMethod http://127.0.0.1:8000/speaker/status } catch { Write-Host 'speaker/status確認失敗。' }"

echo.
echo [3] tts/status
powershell -Command "try { Invoke-RestMethod http://127.0.0.1:8000/tts/status } catch { Write-Host 'tts/status確認失敗。' }"

pause
