@echo off
pushd "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { Write-Host '=== Plaud 新規録音を同期中... ===' -ForegroundColor Cyan; node plaud_sync.mjs; Write-Host ''; Write-Host '=== Plaud -> Asana タスク登録 ===' -ForegroundColor Cyan; node plaud_to_asana.mjs }"
popd
pause
