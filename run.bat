@echo off
chcp 65001 > nul
echo ===================================================
echo   [Stock Radar] AI 주식 급등주 및 신규상장 분석기
echo ===================================================
echo.
echo 가상환경을 활성화하고 대시보드를 실행합니다...
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

python -m streamlit run app.py

pause
