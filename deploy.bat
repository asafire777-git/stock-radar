@echo off
set "PATH=%PATH%;C:\Users\Iremaster\AppData\Local\Programs\Git\cmd"
cd /d "%~dp0"

echo ===================================================
echo   [Stock Radar] Auto Deploy to Streamlit Cloud
echo ===================================================
echo.

echo 1. Staging files...
git add .

echo 2. Committing changes...
git commit -m "Auto deploy update"

echo.
echo 3. Pushing to GitHub...
git push origin main

echo.
echo ===================================================
echo   Deployment sent to GitHub successfully!
echo   Streamlit Cloud will auto-update in ~10 seconds.
echo ===================================================
echo.
pause
