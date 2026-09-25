@AGENTS.md

# Claude Code 固有の補足（このリポジトリの共通ルールは上の AGENTS.md が正本）

- セッション開始時の起動ルーティンは `.claude/hooks/session-start.sh` が自動指示する（me.md と ai_operations_flow.md と preferences.md を読む → handoff.md の未検品を報告 → 環境1行申告 → 今日の提案再掲 → 「準備完了」）
- 重ティアの並列実行はサブエージェント3班（`chosa-han` 調査・`kian-han` 起案・`kensan-han` 検算）。金額・数量・納期入りの成果物は提示前に必ず `kensan-han` を通す
- このリポジトリ専用スキルは `.claude/skills/`（`/mitsumori` `/shodan-mae` `/shodan-ato` `/oboete` `/codex` `/buntai` `/handan` `/kikaku` `/getsuji`。4分類のスキルマップは同フォルダの README.md）。全プロジェクト共通スキルは `~/.claude/skills/`
- 画像・バナー・図解の依頼は必ず `/codex` スキル経由。顧客情報・価格は渡してよい（2026-09-25 解禁）。認証情報・社員の繊細情報・顧客 IP は渡さない
