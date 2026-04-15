# prompt: 議事録から請求書を作る

## 一文版
> `context/projects/<案件>.md` と直近の議事録から、<対象月> 分の請求書を `templates/invoice.md` に沿って作って。

## 前提
- `context/clients/<name>.md` の請求情報を優先
- 単価・支払条件が未定義なら生成前に質問
- 明細は議事録の ToDo 完了分と案件の時間実績から組む

## 出力
- Markdown の請求書
- 末尾に参照ファイル一覧
- 不足情報があれば先頭に箇条書きで列挙
