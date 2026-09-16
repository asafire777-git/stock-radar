Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  [Stock Radar] AI 주식 급등주 및 신규상장 분석기" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "가상환경을 활성화하고 대시보드를 실행합니다..." -ForegroundColor Yellow

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

& "$scriptDir\venv\Scripts\Activate.ps1"
& "$scriptDir\venv\Scripts\streamlit.exe" run app.py
