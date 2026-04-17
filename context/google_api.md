# Google API 連携設定

## 概要

OAuth 2.0 による Google サービス一括接続。
Drive / Gmail / Calendar / Sheets / Docs に単一の認証で接続可能。

## 認証ファイル

| ファイル | 説明 | 場所 |
|---------|------|------|
| `credentials.json` | Google Cloud Console から発行（要手動取得） | `三幸商事株式会社/` 直下 |
| `token.pickle` | 初回認証後に自動生成される認証トークン | `三幸商事株式会社/` 直下 |

> **注意**: credentials.json / token.pickle は秘密情報。git にコミットしないこと。

## スクリプト

| ファイル | 役割 |
|---------|------|
| `google_auth.py` | 認証モジュール（全サービス共通） |
| `google_drive.py` | Drive ファイル一覧取得・整理 |

## 使い方

### 初回認証
```bash
python google_auth.py
# → ブラウザが開く → Googleアカウントでログイン → 許可
# → token.pickle が生成されて以降は自動認証
```

### Drive の中身を取得
```bash
python google_drive.py
# → drive_contents.json に全ファイル一覧が出力される
```

## Claude への指示

- Google Drive の操作依頼があれば `google_auth.get_drive_service()` を使うこと
- Gmail の操作依頼があれば `google_auth.get_gmail_service()` を使うこと（ `context/gmail.md` の IMAP より優先）
- カレンダーの書き込みが必要な場合は `google_auth.get_calendar_service()` を使うこと（読み取りは `context/google_calendar.md` の iCal URL でも可）
- `credentials.json` が存在しない場合は取得手順をユーザーに案内すること

## credentials.json の取得手順

1. https://console.cloud.google.com/ にアクセス
2. プロジェクトを作成（例: `sanko-shoji`）
3. 「APIとサービス」→「ライブラリ」で以下を有効化：
   - Google Drive API
   - Gmail API
   - Google Calendar API
   - Google Sheets API
   - Google Docs API
4. 「APIとサービス」→「認証情報」→「認証情報を作成」→「OAuth 2.0 クライアント ID」
5. アプリケーションの種類：**デスクトップアプリ**
6. `credentials.json` をダウンロード → `三幸商事株式会社/` 直下に配置

## スコープ一覧

```python
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
]
```
