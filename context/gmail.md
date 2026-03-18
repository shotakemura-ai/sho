# Gmail 連携設定（メール受信）

## 接続情報

| 項目 | 値 |
|------|-----|
| アカウント | takemurasteelsanco@gmail.com |
| 用途 | 仕事メール受信（サイボウズからの転送含む） |
| プロトコル | IMAP over SSL |
| サーバー | imap.gmail.com:993 |
| アプリパスワード | `~/.claude/settings.json` の `gmail.app_password` を参照 |
| アクセス | 読み取り専用（送信不可） |

> **注意**: アプリパスワードは機密情報です。第三者に共有しないこと。

---

## curl コマンド例

```bash
# 未読メール件数確認
curl -s --url "imaps://imap.gmail.com:993/INBOX" \
  --user "takemurasteelsanco@gmail.com:<APP_PASSWORD>" \
  --request "SEARCH UNSEEN"

# 最新N件のヘッダー取得（件名・送信者・日時）
curl -s --url "imaps://imap.gmail.com:993/INBOX" \
  --user "takemurasteelsanco@gmail.com:<APP_PASSWORD>" \
  --request "FETCH <UID>:<UID-N> (BODY[HEADER.FIELDS (FROM SUBJECT DATE)])"

# 特定メールの本文取得
curl -s --url "imaps://imap.gmail.com:993/INBOX" \
  --user "takemurasteelsanco@gmail.com:<APP_PASSWORD>" \
  --request "FETCH <UID> (BODY[TEXT])"
```

> `<APP_PASSWORD>` は `syuixwzfodnvjboh`（スペースなし）

---

## Claude への指示

- メール確認の依頼があれば IMAP で取得して表示すること
- 件名・送信者はISO-2022-JPまたはUTF-8エンコードされている場合があるため適切にデコードすること
- 表示形式：日時・送信者・件名を一覧表示し、本文は要求があれば取得する
- 「未読メール」「最新メール」「〇〇からのメール」など条件に応じて絞り込む
- メールの送信・削除・既読化は行わないこと（読み取り専用運用）
- サイボウズからの転送メールも含まれるため、転送元の内容も考慮して表示すること
