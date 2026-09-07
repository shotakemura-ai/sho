@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo.
echo ========================================
echo  MJS e-ドキュメントCloud 領収書自動登録
echo ========================================
echo.

REM Playwrightがインストールされているか確認
python -c "import playwright" 2>nul
if errorlevel 1 (
    echo [初回セットアップ] Playwright をインストールしています...
    pip install playwright
    python -m playwright install chromium
    echo.
)

REM 月の指定（引数なし = 今月）
if "%1"=="" (
    python edoc_register.py
) else (
    python edoc_register.py %1
)

pause
