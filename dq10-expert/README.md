# DQ10 エキスパートチーム

ドラゴンクエストX オンライン v7.6 後期環境の **全24職 × 全エンドコンテンツ** に対応する
Claude Code マルチエージェント専門家チーム。

## 使い方

このディレクトリで Claude Code を起動：

```bash
cd dq10-expert
claude
```

質問例：
- 「魔剣士で聖守護者ジェルザーグやりたい。装備・宝珠・スキル・コマンド配置全部教えて」
- 「v7.6後期の万魔の塔、おすすめ職構成は？」
- 「賢者の160スキルどう振るのが今は正解？」
- 「天地雷鳴士で深淵やるならカカロン型？スパーク型？」

`dq10-coordinator` が内容を読んで適切な専門家へ振り分けます。

## 構成

```
dq10-expert/
├── CLAUDE.md                 # プロジェクト指示（出力フォーマット定義）
├── README.md                 # 本ファイル
├── .claude/
│   └── agents/
│       ├── dq10-coordinator.md
│       ├── dq10-warrior-class.md   # 戦/パラ/ガデ
│       ├── dq10-attacker-class.md  # バト/武/まも/魔剣/海賊
│       ├── dq10-mage-class.md      # 魔/まほう/天地/占い
│       ├── dq10-healer-class.md    # 僧/賢/デス/旅
│       ├── dq10-trickster-class.md # 盗/レン/スパ/踊/遊び人
│       ├── dq10-equipment.md
│       ├── dq10-jewel.md
│       ├── dq10-skill160-200.md
│       ├── dq10-command-layout.md
│       └── dq10-endcontent.md
└── knowledge/
    ├── jobs/                 # 職ごとのテンプレ・確定情報
    ├── content/              # コンテンツごとの要点
    └── sources.md            # 情報源URL集
```

## 設計思想

1. **専門化**: 1エージェント=1領域。職と横断トピックを直交させ、知識密度を上げる
2. **並列化**: 多領域横断の質問は専門家を並列起動して時間短縮
3. **検証可能**: WebFetch で公式・wikiを引きながら回答し、出典URLを必ず添える
4. **正直**: 知識カットオフ（2026年1月）後の変更や不確実な数値はハッキリ言う
5. **更新可能**: knowledge/ にメモを溜めて、次回以降の精度を上げる

## メンテナンス

- バージョン更新時は `CLAUDE.md` の対象バージョンと各エージェントを更新
- 新情報を得たら `knowledge/` に追記
- 信頼できる新ソース（wiki/ブログ）が出てきたら `knowledge/sources.md` に追加
