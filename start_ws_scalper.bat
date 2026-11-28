@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   N-Stock 0.1초 실시간 초단타 감시 엔진 (KIS VTS 모의투자)
echo ============================================================
echo.
"%~dp0venv\Scripts\python.exe" "%~dp0ws_scalper_engine.py" %*
pause
