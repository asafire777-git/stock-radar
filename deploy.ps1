$env:Path = "$env:Path;C:\Users\Iremaster\AppData\Local\Programs\Git\cmd"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  [Stock Radar] 원클릭 클라우드 자동 배포 (Deploy)" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. 변경 파일 확인 및 스테이징..." -ForegroundColor Yellow
git add .

Write-Host "2. 커밋 생성..." -ForegroundColor Yellow
$msg = if ($args.Count -gt 0) { $args[0] } else { "Auto deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" }
git commit -m $msg

Write-Host "3. 깃허브로 전송 중..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===================================================" -ForegroundColor Green
    Write-Host "  [성공] 깃허브 전송 완료!" -ForegroundColor Green
    Write-Host "  Streamlit Cloud가 10초 내에 자동 재배포합니다." -ForegroundColor Green
    Write-Host "===================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[알림] 전송 결과 확인 필요 (최신 상태이거나 인증 필요)" -ForegroundColor DarkYellow
}
