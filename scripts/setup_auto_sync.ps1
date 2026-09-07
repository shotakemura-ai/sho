# Git 自動同期タスクスケジューラ設定スクリプト
# 5分おきにリポジトリの変更を検出し、自動で git add + commit + push する
#
# 実行方法: PowerShell を管理者で開いて .\scripts\setup_auto_sync.ps1
# 削除方法: Unregister-ScheduledTask -TaskName "Git-Auto-Sync" -Confirm:$false

$scriptDir = $PSScriptRoot
$batFile = Join-Path $scriptDir "auto_sync.bat"
$taskName = "Git-Auto-Sync"

# バッチファイルの存在確認
if (-not (Test-Path $batFile)) {
    Write-Host "[ERROR] バッチファイルが見つかりません: $batFile" -ForegroundColor Red
    exit 1
}

# 既存タスクがあれば削除
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# タスク設定
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batFile`"" -WorkingDirectory (Split-Path $scriptDir)

# 5分おきに繰り返すトリガー（ログオン後、無期限で繰り返し）
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 3) `
    -RunOnlyIfNetworkAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "リポジトリの変更を5分おきに自動で git add + commit + push する" | Out-Null

Write-Host ""
Write-Host "タスクスケジューラに登録しました: $taskName" -ForegroundColor Green
Write-Host "  実行間隔: 5分おき" -ForegroundColor Cyan
Write-Host "  対象バッチ: $batFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "--- 操作コマンド ---"
Write-Host "  今すぐ実行:   Start-ScheduledTask -TaskName '$taskName'"
Write-Host "  状態確認:     Get-ScheduledTask -TaskName '$taskName' | Select-Object State"
Write-Host "  タスク削除:   Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
Write-Host ""
