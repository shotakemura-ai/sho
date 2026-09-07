# Asana 自動同期タスクスケジューラ設定スクリプト
# 実行方法: PowerShell を管理者で開いて .\scripts\setup_asana_scheduler.ps1

$scriptDir = Split-Path -Parent $PSScriptRoot
$batFile = Join-Path $scriptDir "Asana同期.bat"
$taskName = "Asana-Claude-Sync"

# 既存タスクがあれば削除
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# タスク設定
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batFile`""
$triggers = @(
    # 平日 朝8時
    New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "08:00",
    # 平日 昼12時
    New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "12:00",
    # 平日 夕18時
    New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "18:00"
)
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $triggers -Settings $settings -RunLevel Highest -Description "Asana タスクを Claude に定期同期" | Out-Null

Write-Host "✅ タスクスケジューラに登録しました: $taskName"
Write-Host "   平日 08:00 / 12:00 / 18:00 に自動実行されます"
Write-Host ""
Write-Host "今すぐ実行テスト:"
Write-Host "  Start-ScheduledTask -TaskName '$taskName'"
