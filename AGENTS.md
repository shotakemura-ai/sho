# AGENTS.md — Codex 用の入口（正本は CLAUDE.md）

このリポジトリの AI 向けルールブックの**正本は `CLAUDE.md`** です。Codex（OpenAI）でこのフォルダを開いたときは、
まず次を読んでから作業してください。Claude Code と同じ1人のアシスタントとして振る舞います。

1. `CLAUDE.md` — 運用の要点・会社情報・「考える順番」4か条・禁止事項
2. `context/me.md` — 竹村翔の取扱説明書（応対ルール・判断基準）
3. `context/preferences.md` — 好み・NG メモ
4. `context/ai_operations_flow.md` — クリティカル7（人間の承認が要る7つ）

## Codex で作業するときの追加ルール

- **役割**：主に「画像生成」と「Claude の利用上限に当たったときの代打」。判断・設計・検証は Claude（Fable）側の仕事。代打で動いた内容は、次に Claude が開いたときに検品できるよう `context/ops_log.md` に1行残す
- **顧客情報・価格・仕入・社内メールの本文は、Codex のプロンプトに貼らない**（外部サービスへ送られるため）。画像の指示文・一般的な文章・公開情報だけを扱う
- 送信（メール・SNS 投稿）・Asana の更新・カレンダー変更はしない。下書きまで
- 金額・数量・納期を含む文書は必ず「⚠人間確認必須」を付ける
- 日付は `TZ=Asia/Tokyo date '+%Y-%m-%d (%a)'` で確認する
- 生成した画像は `缶バッジ事業部/SNS/画像/`（缶バッジ）または依頼元の部門フォルダに、`YYYYMMDD_<用途>_<連番>.png` で保存する
- 作業後は `git add` → commit → push（force push・reset --hard は禁止）
