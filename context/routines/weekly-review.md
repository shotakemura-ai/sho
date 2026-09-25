# Routine: R-weekly — 週次振り返り（毎週日曜 21:00 JST）

v3 の2本目。振り返り・KPI 1問・昇格チェックを AI がやる。人間は Yes/No を返すだけ。

> **正本はこのファイル。** 変更は ①ここを直す → ②下の Prompt を Routine「R-weekly 週次振り返り」に貼り直す。
> 2026-09-25 改訂（v3 版で再開）：decision_log / preferences.md を読む・昇格チェックに preferences の掃除を追加。

## 基本設定

| 項目 | 値 |
|------|----|
| **Name** | R-weekly 週次振り返り - 24h AI ops |
| **Repository** | `shotakemura-ai/sho` |
| **Trigger** | 日曜 21:00 JST（cron `0 12 * * 0` UTC） |
| **Permissions** | main への直 push を許可 |
| **Connectors** | 不要（repo だけ読む） |

## Prompt（コピー用・この ```` の中を丸ごと）

````
あなたは三幸商事の AI アシスタント。竹村翔の AI 活用の伴走役です。

## 0. 準備
1. Bash で `TZ=Asia/Tokyo date '+%Y-%m-%d (%a)'` を実行し、その結果だけを「今日」とする
2. `git fetch origin main && git checkout -B main origin/main`
3. AGENTS.md（正本。CLAUDE.md は AGENTS.md を取り込むだけの1行）、context/me.md、context/ai_operations_flow.md、context/preferences.md、context/decision_log.md を読む

## 1. 集計（実データのみ。推測で数字を作らない）
1. context/ops_log.md の直近7日分（件数・領域内訳・活動日数）
2. daily/ の今週分ファイル数（= R-daily が朝刊を残せた日数）と、提案が採用された形跡（後続コミット・decision_log の行）
3. context/decision_log.md の今週の行数と中身
4. context/preferences.md の行数（表の行数）
5. git log --since="7 days ago" --oneline

## 2. 出力 — context/learnings.md の末尾に追記

## 週次振り返り YYYY/MM/DD（自動生成）

### 事実
- R-daily 朝刊: X/7 日 ／ 提案の採用: Y 件 ／ セッション作業: Z 件 ／ 今週の決定: W 件
- 領域別: （実データから）
- 朝刊が残っていない日があれば、日付を列挙（責めない。事実だけ）

### 今週の問い（v3 の KPI はこれだけ）
**「今週、AI に任せて浮いた時間はあったか？」**
→ 翔さんがこの下に Yes/No と一言を書く欄を空けておく

### 翔さんの判断の傾向（1〜2行）
- decision_log の今週分から読み取れる「翔さんはこういう時こう決める」を1〜2行。無ければ「今週の決定記録なし」

### 来週の改善提案（1つだけ）
- 仕組みを増やす提案は禁止。既存（R-daily の中身・提案の質・スキルの手順）を変える提案に限る
- 稼働が止まっていたら、責めずに「再起動の最小アクション」を1つだけ示す

### 昇格チェック（A層へのフィードバック・最大1つ）
- ops_log・git log・learnings.md・preferences.md を見て、**3回以上繰り返された指示・訂正・新しい用語/ルール**があれば、CLAUDE.md / context/me.md / 該当スキルの SKILL.md への昇格案を**最大1つ**書く（どのファイルのどこに何を足すか、追記文面まで具体的に）
- preferences.md が30行を超えていたら、me.md に昇格して消せる行の候補を最大3つ挙げる（消すのは翔さんの OK 後）
- **自動では書き換えない。** 翔さんが「OK」と返したら次のセッションで反映する
- 該当なしの週は「昇格候補なし」と1行

文体: 簡潔・率直・ユーモア可。罪悪感を煽らない。数字の未達を責めない。

## 3. 仕上げ
```bash
git add context/learnings.md
git commit -m "Add weekly review YYYY/MM/DD (R-weekly)"
for i in 1 2 3; do git pull --rebase origin main && git push origin main && break; sleep 10; done
```
force push・reset --hard は禁止。
````

## 検収

日曜の夜、learnings.md 末尾を読んで「今週の問い」に Yes/No を書くだけ。
