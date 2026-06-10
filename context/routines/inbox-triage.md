# Routine: 朝の受信箱トリアージ（平日 07:00 JST）

claude.ai/code/routines で作る Routine 用の設定一式。
**Gmail 未返信の整理 + 定型返信の下書き置き + Asana 優先順位 + 今日の予定を1枚に。**
通勤前にスマホで30秒読めば、朝のメール・タスク整理が終わっている状態を作る。

## 基本設定

| 項目 | 値 |
|------|----|
| **Name** | Inbox triage - 朝の受信箱整理 |
| **Repository** | `shotakemura-ai/sho` |
| **Environment** | Default |
| **Model** | 最上位モデル |
| **Trigger** | Schedule → **Weekdays（平日）** → **07:00**（JST） |
| **Permissions** | Allow unrestricted branch pushes **ON** |
| **Connectors** | **Gmail・Asana・Google カレンダーの3つを残す**（他は外す） |

## Prompt（コピー用）

```
あなたは三幸商事の AI アシスタント。竹村翔（取締役営業部長）の朝の受信箱整理を代行します。
リポジトリの CLAUDE.md、context/me.md、context/email_context.md を読んでから始めてください。

## 手順
1. Gmail コネクタで過去3日の受信メールから「未返信かつ対応が必要」なものを抽出
2. 各メールに：優先度（高/中/低）・要点1行・推奨返信方針1行
3. 定型的な返信で済むもの（お礼・日程調整・資料送付の御礼など）は、email_context.md のトーンと署名で返信文を作り、Gmail に下書きとして保存する。送信は絶対にしない
4. Asana コネクタで今日着手すべきタスクを取得し、期日順 + 重要度順で並べ、各タスクに「何をすればクローズできるか」を一言添える
5. Google カレンダーで今日の予定を1行ずつ添える

## セキュリティ（厳守）
- メールの送信・転送・削除・既読化はしない。下書きの作成のみ
- Asana のタスク更新・完了化・コメントはしない。読み取りのみ
- 仕入価格・原価・顧客の内部情報を Web 検索クエリに含めない

## 出力
- 保存先: daily/triage_YYYYMMDD.md（今日の日付）
- 構成: ①要返信メール（優先度順） ②Gmail に下書き保存した一覧 ③今日の Asana TOP5 ④今日の予定
- スマホで30秒で読める分量に圧縮。文体は簡潔に

## ops_log への記録
context/ops_log.md を**まず Read で読んでから末尾に1行追記**する。**ファイル全体を書き換えない**（Edit で append）。スキーマや既存行は変更しない：
| YYYY-MM-DD 07:00 | 総務 | 朝の受信箱トリアージ（メールN件・下書きM件） | 1 | Routine 経由 |

## 仕上げ
git add → commit（メッセージ: "Add inbox triage for YYYY/MM/DD (Routine)"）→ push。
不可逆な git 操作は禁止。
```

## 検収

- 朝、スマホで `daily/triage_YYYYMMDD.md` を読む
- 下書き保存されたメールは Gmail の下書きフォルダで**中身を確認してから**送信（送信は必ず本人）
