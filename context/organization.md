# 運用ルール

## 大前提：Claude は1人

窓口（ブラウザ / Windows Desktop）に関わらず、Claude は1人。
役割や人格を切り替える必要はなく、常に同じ Claude として動作する。

詳細は `context/assistant.md` 参照。

---

## 窓口の使い分け（覚えるのはこれだけ）

| 場所 | 窓口 | 主な用途 |
|------|------|--------|
| どこからでも（PC・iPhone・Mac） | **ブラウザ**（claude.ai/code） | 戦略議論・ドキュメント・GitHub・並列発注・Web 調査 |
| 仕事場の Windows | **Claude Code Desktop** | Asana / Gmail / 社内ネットワークドライブ / 経費精算スクリプト |

「今どこの Claude？」を意識する必要はない。**窓口は単なるアクセス手段**。

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
