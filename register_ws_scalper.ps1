# N-Stock 0.1초 실시간 WebSocket 초단타 엔진 - Windows 백그라운드 자동 시작 등록 스크립트
# 사용법 (PowerShell): .\register_ws_scalper.ps1
# 해제법 (PowerShell): Unregister-ScheduledTask -TaskName "NStock_WS_Scalper_VTS" -Confirm:$false

$TaskName = "NStock_WS_Scalper_VTS"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonW = Join-Path $ProjectDir "venv\Scripts\pythonw.exe"
$ScriptPath = Join-Path $ProjectDir "ws_scalper_engine.py"

if (-not (Test-Path $PythonW)) {
    Write-Host "❌ venv\Scripts\pythonw.exe 를 찾을 수 없습니다: $PythonW" -ForegroundColor Red
    exit 1
}

$Action = New-ScheduledTaskAction -Execute $PythonW -Argument "`"$ScriptPath`"" -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Days 0)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "N-Stock KIS VTS 0.1s Real-Time WebSocket Scalper Engine (Paper Trading Only)" `
    -Force | Out-Null

Write-Host "✅ Windows 백그라운드 상시 실행 등록 완료! (작업명: $TaskName)" -ForegroundColor Green
Write-Host "   • 로그 확인: $ProjectDir\data\ws_scalper.log" -ForegroundColor Cyan
Write-Host "   • 지금 즉시 백그라운드 실행하려면: Start-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor Yellow
Write-Host "   • 중지하려면: Stop-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor Yellow
