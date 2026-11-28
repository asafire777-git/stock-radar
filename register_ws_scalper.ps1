# N-Stock 0.1초 실시간 WebSocket 초단타 엔진 - Windows 백그라운드 자동 시작 등록 스크립트 (관리자 권한 불필요)
# 사용법 (PowerShell): .\register_ws_scalper.ps1
# 해제법 (PowerShell): Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\NStock_WS_Scalper_VTS.lnk" -Force

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonW = Join-Path $ProjectDir "venv\Scripts\pythonw.exe"
$ScriptPath = Join-Path $ProjectDir "ws_scalper_engine.py"
$StartupDir = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupDir "NStock_WS_Scalper_VTS.lnk"

if (-not (Test-Path $PythonW)) {
    Write-Host "❌ venv\Scripts\pythonw.exe 를 찾을 수 없습니다: $PythonW" -ForegroundColor Red
    exit 1
}

# 1. Windows 시작프로그램 폴더에 백그라운드 자동 실행 바로가기 등록 (관리자 권한 불필요)
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonW
$Shortcut.Arguments = "`"$ScriptPath`""
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.WindowStyle = 7  # Minimized / Hidden
$Shortcut.Description = "N-Stock KIS VTS 0.1s Real-Time WebSocket Scalper Engine"
$Shortcut.Save()

# 2. 기존 실행 중인 동일 프로세스가 없으면 즉시 백그라운드 구동
$existing = Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe'" | Where-Object { $_.CommandLine -like "*ws_scalper_engine.py*" }
if (-not $existing) {
    Start-Process -FilePath $PythonW -ArgumentList "`"$ScriptPath`"" -WorkingDirectory $ProjectDir -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

$running = Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe'" | Where-Object { $_.CommandLine -like "*ws_scalper_engine.py*" }
if ($running) {
    Write-Host "✅ Windows 백그라운드 상시 실행 등록 & 즉시 구동 완료! (PID: $($running.ProcessId))" -ForegroundColor Green
} else {
    Write-Host "⚠️ 바로가기는 등록되었으나 프로세스 확인이 필요합니다." -ForegroundColor Yellow
}
Write-Host "   • 자동시작 경로: $ShortcutPath" -ForegroundColor Cyan
Write-Host "   • 실시간 로그:   $ProjectDir\data\ws_scalper.log" -ForegroundColor Cyan
