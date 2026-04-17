# 三幸商事株式会社 — Claude Code 設定

**会社**: 三幸商事株式会社（鉄鋼商社）| **担当**: 竹村 翔 (s-takemura@steelsanco.co.jp)
**署名**: `context/email_context.md` 参照

## スタイル
日本語・敬語・ビジネス文体。金額カンマ区切り。日付は西暦。金額・数量・納期を含む文書には確認コメントを添えること。

## コンテキストファイル（必要時のみ読む）

| ファイル | 用途 |
|---------|------|
| `context/company_profile.md` | 会社詳細・沿革・取扱品目 |
| `context/customers.md` | 主要顧客マスター |
| `context/email_context.md` | メール署名・テンプレート |
| `context/asana.md` | Asana API（タスク管理） |
| `context/google_calendar.md` | Google カレンダー（iCal） |
| `context/gmail.md` | Gmail IMAP |
| `context/plaud.md` | Plaud 録音DB（521件） |
| `context/google_api.md` | Google Drive/Sheets/Docs API |

## ルーティング指示

- タスク管理 → `context/asana.md` を読んで Asana API 呼び出し
- スケジュール → `context/google_calendar.md` を読んで iCal 取得
- メール → `context/gmail.md` を読んで IMAP 接続
- Drive操作 → `context/google_api.md` を読んで `google_drive.py` 実行
- 会議・商談記録 → `context/plaud.md` を読んで Plaud録音DB を Grep
- 部門固有ルール → 各サブディレクトリの CLAUDE.md 参照

## 営業2部 組織構成

```
営業2部/
├── 非缶材課/         ← 缶バッジ・ブリキ材・ECサイト・SNS・マーケティング
│   ├── カレンダー係/
│   └── 仕入先/       ← 缶バッジ仕入先管理
└── 一般薄板課/       ← 薄板鋼材・営業・マーケティング
    ├── シャーリング係/
    ├── 仲間係/
    ├── 自動車係/
    ├── 在庫/
    └── 仕入先/       ← 鉄鋼仕入先管理
```
