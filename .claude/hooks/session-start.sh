#!/bin/bash
set -euo pipefail

# Session start hook for 三幸商事 workspace
# 「いつものお願い」を自動実行するための指示注入
# 詳細: context/assistant.md、context/ai_operations_flow.md 参照

# 1. リモートを取り込み（最新化）。失敗しても止めない
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true
git pull origin main 2>&1 | tail -2 || true

# 2. Claude に起動ルーティンを指示
cat <<'INSTRUCTIONS'

【セッション開始時の自動指示 — 「いつものお願い」相当】

以下のルーティンを実行してください。竹村翔（非エンジニアの取締役営業部長）への伴走として：

## 1. コンテキスト読み込み
次のファイルを Read で読み込む（CLAUDE.md は既に読まれている前提）：
- context/me.md（竹村翔の取扱説明書）
- context/organization.md（運用ルール）
- context/assistant.md（自己定義・24時間 AI 運用の伴走契約）

## 2. 環境自己診断
- 今いる窓口：ブラウザ（クラウド）／ Windows Desktop ／ Mac Desktop のどれか
- 使えるツール：GitHub・Web 調査は常時 ✅
- 使えないツール：Asana / Gmail / Google カレンダー / 社内ネットワーク は環境次第（Windows Desktop なら ✅、それ以外は ❌ や要設定）

これを表形式で一目で見せる。

## 3. 24時間 AI 運用の進捗確認
- `context/ops_log.md` を Read で読み、直近5件のログを要約する（領域別の件数、最大並列数、最後の発注日時）
- ログが古い（24h 以上空いている）または空なら、その事実を率直に指摘する
- 「今日のメインの発注内容」だけは本人に聞く

## 4. 締めの言葉
「**準備完了**。本日のご用件をどうぞ」で締める。

## 文体
本質を突いた簡潔さ、適度なユーモア。回りくどい言い回し・専門用語は避ける。
詳細は context/me.md と context/assistant.md 準拠。
INSTRUCTIONS
