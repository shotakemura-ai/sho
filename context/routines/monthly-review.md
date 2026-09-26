# Routine: R-monthly — 月次振り返りの「事実」自動生成（毎月1日 09:00 JST）

らすく式「毎月1日の朝、先月の振り返りレポートが勝手にできあがっている」の実装（2026-09-26 新設）。
R-weekly（週次・自動）の上に乗る月1本。**このジョブは事実を集めるだけ**。問い・重点3つの決定は `/getsuji`（対話）がやる。
翔さんは朝刊の「月次やろうで10分」を見て「月次やろう」と言うだけ。

> **正本はこのファイル。** 変更は ①ここを直す → ②`RemoteTrigger update`（Claude が実行できる）か Routine 画面に貼り直す。

## 基本設定

| 項目 | 値 |
|------|----|
| **Name** | R-monthly 月次事実 - 24h AI ops |
| **Repository** | `shotakemura-ai/sho` |
| **Trigger** | 毎月1日 09:00 JST（cron `0 0 1 * *` UTC。JST 9時前は UTC で前日になるため 09:00 にしている） |
| **Permissions** | main への直 push を許可 |
| **Connectors** | 不要（repo だけ読む。Asana は /getsuji 本番で読む） |
| **出力** | `経営企画室/レポート/月次壁打ち/YYYYMM_事実.md`（YYYYMM＝対象月＝前月） |

## Prompt（コピー用・この ```` の中を丸ごと）

````
あなたは三幸商事の AI アシスタント。竹村翔の月次振り返り（スキル /getsuji）の「事実」パートを先に集計するジョブです。毎月1日 09:00 JST に動きます。翔さんは何も入力していません。推測で数字を作らず、実データだけを並べてください。

## 0. 準備
1. Bash で `TZ=Asia/Tokyo date '+%Y-%m-%d (%a)'` を実行し、その結果だけを「今日」とする。**対象月＝前月**（YYYY-MM。例：今日が 2026-10-01 なら 2026-09）
2. `git fetch origin main && git checkout -B main origin/main`
3. AGENTS.md、context/me.md、context/preferences.md、context/business_os.md の §0・§2、.claude/skills/getsuji/SKILL.md を読む（出力の形は getsuji の「1. 事実」の表に合わせる）

## 1. 集計（実データのみ。無いものは「記録なし」と書く。責めない）
1. context/learnings.md：対象月に書かれた「週次振り返り」見出しを全部拾い、各週の「事実」行と「今週の問い」の答え（翔さんが Yes/No を書いていればそれ）を1行ずつ
2. context/decision_log.md：対象月の行数。方針レベル（やる/やらない・数値目標・戦略の軸）のものを箇条書き
3. context/ops_log.md：対象月の行数と領域内訳（鉄鋼／缶バッジ／個人／仕組み／その他）
4. context/ai_backlog.md：状態別の件数（未着手・進行中・待ち・完了）。期限が今日より前で未完了の行を列挙
5. daily/：対象月の朝刊ファイル数（YYYYMM*.md の個数）
6. 前月の重点3つ：`経営企画室/レポート/月次壁打ち/<対象月の前月 YYYYMM>.md` があれば「来月の重点3つ」を転記し、各項目について decision_log・ops_log・`git log --since` から達成の形跡を探して「できた／途中／手つかず／形跡なし」を仮判定（翔さんが Q1 で訂正する前提）。ファイルが無ければ「初回（前月の重点なし）」
7. 計画原紙に対する現在地：`経営企画室/レポート/` に対象月の「部門別損益」「月次経営ダッシュボード」「全社会議資料」があれば、営業2部の売上・粗利・粗利率・重量を引用（ファイル名を添える）。無ければ「repo に無し → Q3 で翔さんに聞く」と書く。換算・推定はしない
8. `git log --since="<対象月1日>" --until="<今日>" --oneline | wc -l` でコミット数

## 2. 出力：`経営企画室/レポート/月次壁打ち/YYYYMM_事実.md`（フォルダが無ければ作る）
- 冒頭に「自動生成（Routine: R-monthly）YYYY-MM-DD」と「次の一手：翔さんが『月次やろう』と言えば /getsuji がこのファイルを読んで Q1 から始めます（所要10分）」
- 分量は A4 半分。**プラス材料から始める**（sbt.md の原則）。未達は事実として1行、責めない
- 見出し：## 事実（AI 集計）の下に、上の1〜8を getsuji の表の順で。各行に出典ファイル名
- 末尾に「## Q4 の候補（AI 案・翔さんが選ぶ）」として、来月の重点候補を3〜5つ、事実から根拠つきで（改善系・選択肢系・関係深耕系のバランス。1つは「頭を使う版」）
- 金額・顧客名は repo にあるものだけ。仕入価格・原価・個人の家計の数字は書かない

## 3. 記録と仕上げ
context/ops_log.md の末尾に1行 append（既存行は触らない）：
`- YYYY-MM-DD 仕組み：R-monthly 対象月 YYYY-MM の事実を自動生成 → 経営企画室/レポート/月次壁打ち/YYYYMM_事実.md`
```bash
git add "経営企画室/レポート/月次壁打ち/YYYYMM_事実.md" context/ops_log.md
git commit -m "Add monthly facts YYYYMM (R-monthly)"
for i in 1 2 3; do git pull --rebase origin main && git push origin main && break; sleep 10; done
```
rebase で ops_log.md が衝突したら両方の行を残す。force push・reset --hard は禁止。3回失敗したらファイル冒頭に「（push 失敗：手動反映が必要）」と書いてもう一度だけ push。
````

## 検収

月初の朝刊（R-daily）が「月次の事実が揃っています。『月次やろう』で10分」と1行出す。翔さんはそれに「月次やろう」と返すだけ。
`/getsuji` は `YYYYMM_事実.md` があれば集計をスキップして Q1 から始める。
