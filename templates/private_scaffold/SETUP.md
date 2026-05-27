# private リポジトリのセットアップ手順

このディレクトリは `shotakemura-ai/private` リポジトリの**ひな形**です。
以下の手順で新しい repo を作成・初期化してください。

## 手順（竹村翔の作業）

### 1. GitHub で空 repo を作る
1. https://github.com/new を開く
2. Repository name: **`private`**
3. Visibility: **Private**（必須！）
4. 「Add a README」や「Add .gitignore」は**チェックしない**（空のままにする）
5. 「Create repository」をクリック

### 2. Mac / Windows の Claude Code Desktop に貼り付け
```
github で shotakemura-ai/private repo 作った。sho の templates/private_scaffold/ をベースに、~/private にセットアップして main に push して。

手順：
1. ~/private に git clone https://github.com/shotakemura-ai/private.git
2. sho リポジトリの templates/private_scaffold/ の中身を ~/private/ にコピー（隠しファイルとフォルダ含む）
3. ~/private で git add -A && git commit -m "Initial scaffold from sho templates" && git push -u origin main
4. 完了したら ls で構造確認
```

ローカル Claude が自動でやってくれます。

### 3. 確認
ローカル Claude が完了したら、ブラウザで https://github.com/shotakemura-ai/private を開いて、
ファイル一覧に CLAUDE.md / context/ / 副業_AIxBGM/ / 家計管理/ が並んでいれば成功。

### 4. 使い始める
以降、副業や家計の作業は `~/private` ディレクトリで Claude を起動して、
```
いつものお願い。
```
と投げるだけ。
