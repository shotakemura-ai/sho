@echo off
chcp 65001 >nul
echo ======================================
echo  Sanko Local MCP Server セットアップ
echo ======================================
echo.

REM Node.js 確認
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js が見つかりません。
    echo         https://nodejs.org からインストールしてください。
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do echo [OK] Node.js %%v

REM npm install
echo.
echo [INFO] パッケージをインストール中...
call npm install
if errorlevel 1 (
    echo [ERROR] npm install に失敗しました。
    pause & exit /b 1
)
echo [OK] パッケージインストール完了

REM 認証トークン生成
if not exist mcp-token.txt (
    echo.
    echo [INFO] 認証トークンを生成中...
    node -e "const c=require('crypto');const t=c.randomBytes(32).toString('hex');require('fs').writeFileSync('mcp-token.txt',t,'utf8');console.log('[OK] トークン生成: '+t);"
) else (
    echo [OK] 認証トークンは既に存在します
    set /p EXISTING_TOKEN=<mcp-token.txt
    echo      値: %EXISTING_TOKEN%
)

REM cloudflared ダウンロード
echo.
if not exist cloudflared.exe (
    echo [INFO] cloudflared をダウンロード中...
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'" 2>nul
    if exist cloudflared.exe (
        echo [OK] cloudflared ダウンロード完了
    ) else (
        echo [WARN] cloudflared のダウンロードに失敗しました。
        echo        手動で https://github.com/cloudflare/cloudflared/releases からダウンロードし
        echo        このフォルダに cloudflared.exe として配置してください。
    )
) else (
    echo [OK] cloudflared は既に存在します
)

echo.
echo ======================================
echo  セットアップ完了！
echo  start.bat でサーバーを起動してください。
echo ======================================
echo.
pause
