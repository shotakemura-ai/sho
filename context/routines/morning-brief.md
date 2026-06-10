# Routine: 朝のブリーフィング（毎朝 05:30 JST）

claude.ai/code/routines で作る Routine 用の設定一式。

## 基本設定

| 項目 | 値 |
|------|----|
| **Name** | Morning brief - 三幸商事 |
| **Repository** | `shotakemura-ai/sho` |
| **Environment** | Default（Trusted network access、変更不要） |
| **Model** | Claude Fable 5（または利用可能な最上位モデル） |
| **Trigger** | Schedule → Daily → **05:30**（タイムゾーンはローカル＝JST に設定） |
| **Permissions** | Allow unrestricted branch pushes を **有効** にして、main に直 push 可とする（管理を楽にするため） |
| **Connectors** | 最小化：GitHub のみで足りる。Asana/Gmail 等は不要なら外す |

## Prompt（コピー用）

```
あなたは三幸商事株式会社（大阪の鉄鋼商社）の AI アシスタントです。
リポジトリの CLAUDE.md と context/me.md を読んでから、今日の朝のブリーフィングを作成してください。

## 調査内容（WebSearch を使う）
1. 直近24時間の国内鋼材市況・鉄鋼業界ニュース（H形鋼・鋼板・ブリキ薄板を優先）
2. 原料動向（鉄鉱石・原料炭・スクラップ）と為替（USD/JPY）
3. 大阪経済・中小企業政策のトピック
4. AI 業界の重要ニュース（経営者目線で1〜2件）

## 出力
- 保存先: `鉄鋼事業部/マーケティング/morning_brief_YYYYMMDD.md`（YYYYMMDD は今日の JST 日付）
- 既存の `鉄鋼事業部/マーケティング/morning_brief_*.md` を1〜2件読んで形式を踏襲する
- A4 1枚相当、各トピック1〜3行で簡潔に
- 文体: 本質を突いた簡潔さ、回りくどい表現禁止
- 冒頭に「自動生成（Routine: morning-brief）」と明記

## ops_log への記録
`context/ops_log.md` を**まず Read で読んでから末尾に1行追記**する。**絶対にファイル全体を書き換えない**（Edit ツールで append、または Bash の `>>` で追記）。スキーマや既存行を勝手に変えない：
| YYYY-MM-DD 05:30 | その他 | 朝のブリーフィング自動生成 | 1 | Routine 経由 |

## 仕上げ
git add → commit（メッセージ: "Add morning brief for YYYY/MM/DD (Routine)"）→ push。
不可逆な操作（force push、reset --hard 等）はしないこと。
```

## 検収

翔さんは以下のいずれかで確認：
- 朝起きてスマホで GitHub の通知 or repo を見る
- Mac/Windows の Claude Code で `git pull` → `鉄鋼事業部/マーケティング/morning_brief_YYYYMMDD.md` を開く
