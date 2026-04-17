# カレンダー連携設定

## カレンダー一覧

| カレンダー | 用途 | iCal URL |
|-----------|------|----------|
| Google カレンダー | **プライベート予定** | `https://calendar.google.com/calendar/ical/sho.takemura%40gmail.com/private-d638f3fe9e72eb88986b091284e644f3/basic.ics` |
| サイボウズ Office | **仕事予定** | `https://steelsanco.p.cybozu.com/o/f8cdefbb8bbb1b58be2147da814ec900f7e30eff` |

> **注意**: いずれのURLも秘密のアドレスです。第三者に共有しないこと。

---

## 取得方法

```bash
# プライベート予定（Google カレンダー）
curl -s "https://calendar.google.com/calendar/ical/sho.takemura%40gmail.com/private-d638f3fe9e72eb88986b091284e644f3/basic.ics"

# 仕事予定（サイボウズ）
curl -s "https://steelsanco.p.cybozu.com/o/f8cdefbb8bbb1b58be2147da814ec900f7e30eff"
```

---

## Claude への指示

- スケジュール・予定確認の依頼があれば**両方のカレンダー**から ICS データを取得して統合して表示すること
- ICS データは `VEVENT` ブロックを解析し、`SUMMARY`（件名）・`DTSTART`（開始）・`DTEND`（終了）・`DESCRIPTION`（詳細）・`LOCATION`（場所）を抽出すること
- 日時は Asia/Tokyo（JST, UTC+9）で表示すること（UTC の場合は +9 時間に変換）
- 表示時はカレンダーの種別を区別すること：
  - サイボウズ → 🏢 仕事
  - Google カレンダー → 🏠 プライベート
- 依頼に応じて「今日の予定」「今週の予定」「〇月〇日の予定」などに絞って表示すること
- 書き込み（予定の追加・変更・削除）は非対応。必要な場合は各カレンダーを直接操作するよう案内すること
