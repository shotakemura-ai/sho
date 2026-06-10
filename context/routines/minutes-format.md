# Routine: 議事録の自動整形（平日 18:30 JST）

claude.ai/code/routines で作る Routine 用の設定一式。
**当日の Zoom 会議の文字起こしを、夜のうちに議事録フォーマットへ自動整形。**
（Plaud 録音は従来通り T-203 で手動発注。ここは Zoom 分の無人化）

## 基本設定

| 項目 | 値 |
|------|----|
| **Name** | Minutes - 当日会議の議事録化 |
| **Repository** | `shotakemura-ai/sho` |
| **Environment** | Default |
| **Model** | 最上位モデル |
| **Trigger** | Schedule → **Weekdays（平日）** → **18:30**（JST） |
| **Permissions** | Allow unrestricted branch pushes **ON** |
| **Connectors** | **Zoom のみ残す**（他は外す） |

## Prompt（コピー用）

```
あなたは三幸商事の AI アシスタント。当日の会議録音を議事録化します。
リポジトリの CLAUDE.md と context/plaud.md（議事録の流儀）を読んでから始めてください。

## 手順
1. Zoom コネクタで今日（JST）の会議・録音を検索
2. 文字起こしが取得できる会議ごとに、議事録フォーマットに整形：
   - 日時・参加者・議題・決定事項・宿題（担当・期日）
   - 決定事項と宿題はファイルの最上部に置く
   - 発言者の特定が曖昧な箇所は「※要確認」と明記
3. 録音・文字起こしが1件もなければ、何もせず終了（ファイルを作らない、commit もしない）

## セキュリティ（厳守）
- Zoom 側への書き込み・削除・共有設定の変更はしない（読み取りのみ）
- 議事録は社内文書として repo に保存するのみ。repo 外への送信はしない

## 出力
- 保存先: 総務・人事部/議事録/YYYYMMDD_[会議名].md
- 配布前に本人確認が必要である旨を末尾に1行明記

## ops_log への記録
（議事録を作成した場合のみ）context/ops_log.md の末尾に1行追記：
| YYYY-MM-DD 18:30 | 総務 | 当日会議の議事録自動整形（N件） | 1 | Routine 経由 |

## 仕上げ
git add → commit（メッセージ: "Add minutes for YYYY/MM/DD (Routine)"）→ push。
不可逆な git 操作は禁止。
```

## 検収

翌朝 or 当日夜に `総務・人事部/議事録/` を確認 → 内容チェック後に関係者へ配布（配布は本人）。
