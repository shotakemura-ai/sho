# Plaud 録音データベース連携設定

## 概要

竹村翔のPlaud AIレコーダーで録音した会議・商談・移動中の音声が、
文字起こし・サマリー付きでローカルデータベースに同期されている。

---

## データベース場所

```
鉄鋼事業部/営業/会議資料/Plaud録音データベース/
├── _index.json      ← 全録音の索引（ID・日付・タイトル）
├── _index.md        ← 人間が読むインデックス
└── *.md             ← 各録音のサマリー＋文字起こし
```

**絶対パス**: `\\192.168.1.126\本社\営業\営業2部\個人フォルダ\竹村\カーソル\三幸商事株式会社\鉄鋼事業部\営業\会議資料\Plaud録音データベース\`

---

## 統計（2026-03-25時点）

| 項目 | 件数 |
|------|------|
| 総録音数 | 521件 |
| 対面録音 | 465件 |
| 通話録音 | 85件 |
| デスクトップ録音 | 11件 |
| 期間 | 2025年6月〜現在 |

---

## Plaud API 接続情報

| 項目 | 値 |
|------|-----|
| APIエンドポイント | `https://api-apne1.plaud.ai` |
| トークン | `~/.plaud/config.json` の `token.accessToken` |
| 有効期限 | 2026年9月3日 |
| 必須ヘッダー | `Origin: https://web.plaud.ai`, `Referer: https://web.plaud.ai/`, `app-platform: web`, `timezone: Asia/Tokyo` |

### API呼び出し例

```bash
TOKEN=$(node -e "console.log(require('C:/Users/FONE/.plaud/config.json').token.accessToken)")

# 全録音一覧
curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "Origin: https://web.plaud.ai" \
  -H "Referer: https://web.plaud.ai/" \
  -H "app-platform: web" \
  -H "timezone: Asia/Tokyo" \
  "https://api-apne1.plaud.ai/file/simple/web?skip=0&limit=600"

# 特定録音の詳細（サマリー・文字起こしURL含む）
curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "Origin: https://web.plaud.ai" \
  -H "Referer: https://web.plaud.ai/" \
  -H "app-platform: web" \
  -H "timezone: Asia/Tokyo" \
  "https://api-apne1.plaud.ai/file/detail/<FILE_ID>"
```

---

## 同期スクリプト

```bash
# 新規録音を同期（差分のみ）
node "\\192.168.1.126\本社\営業\営業2部\個人フォルダ\竹村\カーソル\三幸商事株式会社\plaud_sync.mjs"
```

---

## Claudeへの指示

### 録音内容の検索・参照
- 特定のキーワード・顧客・日付での検索は `_index.json` を読んでから該当ファイルを参照する
- `_index.json` の形式: `[{ id, filename, date, filepath }]`
- 各録音MDファイルにはサマリーと文字起こしが含まれる

### 経営への活用
- 「〇〇社との商談」「価格交渉」「缶バッジ」などのキーワードでGrepしてファイルを特定
- 複数の会議にまたがるテーマを横断検索して分析
- 議事録の作成・アクション項目の抽出・顧客動向の把握に活用

### 新規録音の取得
- 最新録音は `plaud_sync.mjs` を実行して同期
- MCPサーバー経由でもアクセス可能（`plaud_list_recordings` / `plaud_get_transcript` ツール）
