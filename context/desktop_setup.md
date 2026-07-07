# Desktop アプリの共通化手順（Mac / Windows 共通）

新しい端末の Claude Code Desktop を「1つの仕組み」に接続するための手順。
iPhone 版は `iphone_setup.md`。**翔さんが覚えることはゼロ** — 下の指示文を貼るだけ。

---

## 翔さんがやること（2ステップ）

1. その端末で **Claude Code Desktop アプリ**を開く
2. 下の「共通化指示文」をそのままコピペして送る

以上。あとは Claude が自分でやり、最後に「共通化完了」と報告してくる。

---

## 共通化指示文（コピー用）

```
この端末を三幸商事ワークスペースに共通化して。手順：

1. 現在のフォルダで git remote -v を確認。shotakemura-ai/sho でなければ、
   ホームディレクトリに git clone https://github.com/shotakemura-ai/sho.git sho を実行し、
   以後そのフォルダ（~/sho）で作業する。認証を求められたら私に画面の指示を伝えて
2. git pull origin main で最新化
3. 古いローカルルールを掃除：「このPCは本業専用」「Mac=個人用」のような端末役割ルールを、
   ユーザーメモリ（~/.claude/CLAUDE.md）・CLAUDE.local.md・旧ワークスペースの CLAUDE.md から探して削除。
   ワークスペースのルールは repo（shotakemura-ai/sho）以外に一切書かないこと
4. sho リポジトリの CLAUDE.md → context/me.md → context/ai_operations_flow.md を読む
5. この端末で使えるツールを1行で申告し、掃除した内容を報告
6. context/ops_log.md に「端末共通化（機種名）」を1行 append して commit & push
7. 「共通化完了」と報告して終わり

以後この端末でも起動ワードは「いつものお願い」。端末に役割はない。
仕事/個人の判別は話題から Claude が行う（CLAUDE.md 準拠）。
```

---

## 補足（Claude 用）

- Desktop アプリは**開いているフォルダの CLAUDE.md を読む**。旧フォルダ（例：カーソル/三幸商事株式会社）を
  開いたままだと古いルールを読み続けるので、**sho クローンのフォルダを開き直してもらう**のが完了条件
- 共通化後の同期は共通ルール通り：セッション開始時 `git pull`、変更したら `commit & push`
- 物理制約は相変わらず2件のみ（社内ネットワークドライブ・経費精算 → 会社の Windows）
