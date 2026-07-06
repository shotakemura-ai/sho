# 運用ルール

## 大前提：Claude は1人

窓口（ブラウザ / Windows Desktop）に関わらず、Claude は1人。
役割や人格を切り替える必要はなく、常に同じ Claude として動作する。

詳細は `context/assistant.md` 参照。

---

## 窓口の使い分け（覚えるのはこれだけ）

| 場所 | 窓口 | 備考 |
|------|------|------|
| どこからでも（iPhone・PC・Mac） | **ブラウザ**（claude.ai/code）/ Claude アプリ | ほぼ全部できる（Asana / Gmail / カレンダーもクラウド MCP で可） |
| 仕事場の Windows | **Claude Code Desktop** | **社内ネットワークドライブと経費精算スクリプトの2件だけ**ここ専用 |
| 自宅の Mac | **Claude Code Desktop** | クラウドと同等。副業作業に |

「今どこの Claude？」を意識する必要はない。**窓口は単なる窓。部屋（repo + クラウド）は1つ**。
Windows 専用の2件に当たったら Claude が「これは会社 PC で」と案内する。

---

## 起動ワード（全窓口共通）

```
いつものお願い。
```

これを送れば Claude が `git pull` → 必要な context を読み込み → 環境を自己診断 → 「準備完了」を返す。

---

## 共通ルール

1. セッション開始時に必ず `git pull origin main` で最新化する
2. `CLAUDE.md` や `context/*` を変更したら必ず `git commit & push` する
3. 重要な資料は git にコミットして全窓口で共有する
4. 環境に依存する情報（トークン等）は `context/.secrets` に置き、git 管理外にする
