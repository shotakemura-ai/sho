@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Asana タスクを同期中...
node asana_to_claude.mjs
if %ERRORLEVEL% NEQ 0 (
    echo エラーが発生しました
    pause
)
