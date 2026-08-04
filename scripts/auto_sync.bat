@echo off
chcp 65001 >nul
REM ============================================================
REM auto_sync.bat — リポジトリの変更を自動で git add + commit + push
REM ダブルクリックで手動実行も可能
REM ============================================================

REM リポジトリのルートに移動（このスクリプトは scripts/ 内にある想定）
cd /d "%~dp0\.."

REM git が使えるか確認
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] git がインストールされていないか、PATH に含まれていません
    pause
    exit /b 1
)

REM git リポジトリかどうか確認
git rev-parse --is-inside-work-tree >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] このディレクトリは git リポジトリではありません
    pause
    exit /b 1
)

REM 変更があるかチェック（untracked + modified + deleted）
git status --porcelain > "%TEMP%\auto_sync_status.tmp"
for %%A in ("%TEMP%\auto_sync_status.tmp") do (
    if %%~zA==0 (
        echo [%date% %time%] 変更なし — スキップします
        del "%TEMP%\auto_sync_status.tmp" >nul 2>&1
        exit /b 0
    )
)
del "%TEMP%\auto_sync_status.tmp" >nul 2>&1

REM タイムスタンプを生成（YYYY-MM-DD HH:MM 形式）
for /f "tokens=1-6 delims=/ " %%a in ('powershell -NoProfile -Command "Get-Date -Format 'yyyy MM dd HH mm ss'"') do (
    set YEAR=%%a
    set MONTH=%%b
    set DAY=%%c
    set HOUR=%%d
    set MINUTE=%%e
    set SECOND=%%f
)
set TIMESTAMP=%YEAR%-%MONTH%-%DAY% %HOUR%:%MINUTE%

echo [%TIMESTAMP%] 変更を検出しました。同期を開始します...

REM 全変更をステージ
git add -A
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] git add に失敗しました
    pause
    exit /b 1
)

REM コミット
git commit -m "auto: sync changes %TIMESTAMP%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] git commit に失敗しました
    pause
    exit /b 1
)

REM 現在のブランチ名を取得して push
for /f "tokens=*" %%b in ('git symbolic-ref --short HEAD') do set BRANCH=%%b
echo [%TIMESTAMP%] ブランチ "%BRANCH%" に push します...

git push origin %BRANCH%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] git push に失敗しました
    echo   ネットワーク接続を確認してください
    echo   次回実行時にリトライされます
    pause
    exit /b 1
)

echo [%TIMESTAMP%] 同期完了 (%BRANCH%)
