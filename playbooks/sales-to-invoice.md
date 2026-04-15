# playbook: 問い合わせ → 請求までの標準フロー

各ステップで「自分が書く命令」は一〜二文を目標にする。
命令が長くなるのはコンテキスト不足のサイン。

## 1. 問い合わせ受領

- [ ] `context/clients/<name>.md` を `_template.md` から作成
- [ ] 問い合わせ本文をそのまま履歴に貼る
- 一文：「この問い合わせから clients/<name>.md の雛形を埋めて」

## 2. 初回ヒアリング

- [ ] `templates/minutes.md` で議事録
- [ ] `context/projects/<案件>.md` を作成
- 一文：「議事録とヒアリングメモから projects/<案件>.md の初期版作って」

## 3. 見積

- [ ] `templates/quote.md` で生成
- 一文：「clients/<name>.md と projects/<案件>.md から見積書作って」
- [ ] 自分でレビュー → 送付

## 4. 受注

- [ ] `projects/<案件>.md` の状態を「進行中」に
- [ ] マイルストーンを記入

## 5. 進行中

- [ ] ミーティングごとに `templates/minutes.md` で議事録
- [ ] 毎日または週次で `prompts/daily-summary.md` を実行してコンテキスト更新

## 6. 納品

- [ ] 成果物の参照を `projects/<案件>.md` に追記
- [ ] 状態を「納品済」に

## 7. 請求

- [ ] `prompts/invoice-from-minutes.md` で請求書生成
- [ ] 送付後、状態を「請求済」に
- [ ] 入金確認後「クローズ」

## 8. 振り返り

- [ ] 学んだことを `me.md` の判断基準 / NG 事項に反映
- [ ] 繰り返し出たパターンは新しい `prompts/*.md` に昇格
