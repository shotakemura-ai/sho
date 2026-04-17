@echo off
chcp 65001 >nul
echo ======================================
echo  Sanko Local MCP Server 起動
echo ======================================
echo.

if not exist mcp-token.txt (
    echo [ERROR] mcp-token.txt が見つかりません。先に setup.bat を実行してください。
    pause & exit /b 1
)
if not exist cloudflared.exe (
    echo [ERROR] cloudflared.exe が見つかりません。先に setup.bat を実行してください。
    pause & exit /b 1
)

REM MCP サーバーを別ウィンドウで起動
echo [INFO] MCP サーバーを起動中...
start "Sanko MCP Server" cmd /k "node server.js"
timeout /t 3 /nobreak >nul

REM cloudflared トンネルを別ウィンドウで起動
echo [INFO] Cloudflare トンネルを起動中...
echo.
echo ============================================================
echo  ↓ トンネルが起動したら表示される URL をコピーしてください
echo    例: https://xxxx-xxxx.trycloudflare.com
echo ============================================================
echo.
start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:3456"

echo.
echo トンネル URL が表示されたら：
echo.
echo 1. URL をコピー
echo 2. クラウドの Claude Code に以下を貼り付けて実行：
echo.
set /p TOKEN=<mcp-token.txt
echo    MCP サーバーに接続して。
echo    URL: https://（コピーした URL）/mcp
echo    Token: %TOKEN%
echo.
pause
