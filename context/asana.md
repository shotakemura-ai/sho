# Asana 連携設定

三幸商事株式会社のグループウェア運用：
- **スケジュール管理** → サイボウズ
- **進捗管理・タスク管理** → Asana
- **情報共有（ファイル・フォルダ）** → Asana（プロジェクトのメモ・添付ファイル）

---

## 接続情報

| 項目 | 値 |
|------|-----|
| ユーザー名 | 竹村 翔 |
| ユーザー GID | 1204898614412973 |
| ワークスペース | steelsanco.co.jp |
| ワークスペース GID | 1203471303375035 |
| API ベース URL | https://app.asana.com/api/1.0 |
| アクセストークン | `~/.claude/settings.json` の `mcpServers.asana.env.ASANA_ACCESS_TOKEN` |

---

## プロジェクト一覧（アクティブ）

| プロジェクト名 | GID |
|--------------|-----|
| 通常タスク＠本社営業2部 | 1203477948026491 |
| 株式会社ぺノンプロジェクト | 1204811624267010 |
| アクリル事業プロジェクト | 1204811624267013 |
| 株式会社KANDOプロジェクト | 1204811624267016 |
| 缶バッジマシン開発プロジェクト | 1204811624267034 |
| ヒンジクリップ、ヒンジスタンド開発 | 1204965209456897 |
| 缶バッジ自動機開発 | 1204965209456903 |
| キャラバン受注管理 | 1206333702976778 |
| 通常タスク＠三幸プロダクツ | 1206916985005725 |
| 缶バッジアクリル受注管理 | 1206936869345321 |
| 金型情報_三幸プロダクツ＠松原 | 1206986042758485 |
| ツインクル受注ガントチャート | 1208188795532620 |
| 第100回東京インターナショナル・ギフトショー秋2025出展 | 1209919273909539 |
| 営業1部 | 1205790445145676 |
| 営業3部＆OST | 1206736172249475 |
| 松原工場（総務経理） | 1208164256569978 |
| 東大阪工場（総務経理） | 1208164256569994 |
| 南港 | 1208290061906693 |
| アシスト運用立ち上げプロジェクト | 1207615542393443 |

---

## API 呼び出し方法

```bash
TOKEN="$(node -e "const s=require('C:/Users/FONE/.claude/settings.json');console.log(s.mcpServers.asana.env.ASANA_ACCESS_TOKEN)")"

# 自分にアサインされた未完了タスク一覧
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://app.asana.com/api/1.0/tasks?assignee=me&workspace=1203471303375035&completed_since=now&opt_fields=name,due_on,assignee_status,projects.name,notes"

# 特定プロジェクトのタスク一覧
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://app.asana.com/api/1.0/projects/<PROJECT_GID>/tasks?opt_fields=name,due_on,completed,assignee.name,notes"

# 特定タスクの詳細（メモ・添付含む）
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://app.asana.com/api/1.0/tasks/<TASK_GID>?opt_fields=name,due_on,notes,projects.name,attachments,assignee.name"

# プロジェクトのメモ（情報共有内容）を取得
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://app.asana.com/api/1.0/projects/<PROJECT_GID>?opt_fields=name,notes"

# タスクを完了にする
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"completed": true}}' \
  "https://app.asana.com/api/1.0/tasks/<TASK_GID>"

# 新規タスクを作成する
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "タスク名", "assignee": "1204898614412973", "workspace": "1203471303375035", "due_on": "2026-03-31", "notes": "メモ内容"}}' \
  "https://app.asana.com/api/1.0/tasks"

# タスクのメモを更新する
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"notes": "更新後のメモ"}}' \
  "https://app.asana.com/api/1.0/tasks/<TASK_GID>"
```

> **トークンの実際の値**は `C:/Users/FONE/.claude/settings.json` から取得する。
> Bash で直接使う場合は設定ファイルを Read して値を参照すること。

---

## Claude への指示

### タスク管理
- タスク確認・追加・完了などの依頼があれば上記 API を Bash ツールで呼び出して対応する
- タスク一覧は「**期限あり／期限なし**」に分類し見やすく整理する
- 新規タスク作成時は名前・期限・メモを確認してから登録する
- タスクの期限変更・削除など破壊的操作は必ずユーザーに確認してから実行する

### 情報共有
- プロジェクトの詳細情報（リンク・ファイルパス・ルールなど）はプロジェクトの `notes` に格納されている
- 「〇〇プロジェクトの情報を調べて」と言われたら、該当プロジェクトの `notes` とタスク一覧を取得して提示する
- プロジェクト名から GID を上記一覧で特定してから API を呼び出す
- 一覧にないプロジェクトはワークスペース全体のプロジェクト一覧 API で検索する
