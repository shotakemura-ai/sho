# AI運用台帳 — 自動化・パイプライン・資産の全所在

最終棚卸し: 2026-09-04（ルーティン整理 第1段・止血）／前回 2026-06-11／棚卸しルール: **月1回**（月初の朝コクピット後にPMが更新）＋**週次ヘルスチェック自動**（scheduled-task `routine-health-check` 月曜7:00が本章の台帳を突合し異常時のみ通知）
整理計画（第2段の残作業）: `経営企画室\プロジェクト\AI基盤再設計\20260904_ルーティン整理計画.md`

---

## 1. ルーティン台帳（稼働中の自動化・3層）

**設計原則（2026-09-04 ルーティン整理で確定）**: 朝の受け取り口はクラウド「朝刊」1本（iPhone・6:00）／PC側の判断キューは朝コクピットが起動時に生成／夕方は17:15→17:45の直列1本／市況ウォッチはローカル2本（週次・月次）＋メディアレーダー／壊れたら月曜7:00の健診が件数だけ通知。
**列の意味**: 「鮮度」＝健診が『この期間内に出力先が更新されていなければ異常』と判定する閾値。「終了コード」はWindowsタスクのみ（0以外＝異常）。

### 1-A. ローカル scheduled-tasks（PC ON時のみ・`.claude\scheduled-tasks\`・PCが落ちていれば次回起動時に繰り越し実行）
| 名前 | 周期(JST) | 役割 | 出力先（健診の鮮度チェック対象） | 鮮度 | 状態・備考 |
|---|---|---|---|---|---|
| mail-tagger-daily | 平日 6:00 | POP3同期＋メールAIタグ付け（直近7日・5並列） | `projects\sankoh-mail-ai\data\mail.db` | 1営業日 | ⚠**タグ付けは2026-07-02から認証切れで停止中**（preflightで即終了・同期のみ正常）。復旧＝ターミナルで `claude auth login`（2026-09-07 `%APPDATA%\npm\claude.cmd` シム設置でPATH解決済・復旧後は mail-tagger-daily が `--retag` で mock タグを自動上書き） |
| morning-cockpit | 平日 6:32 | メール/カレンダー/Asana→判断キュー（朝版）→GitHub公開＋3層push（3行本文・📄詳細/✅OK/⏰後で） | `経営企画室\レポート\判断キュー\判断キュー_最新.md`（GitHub sho main にも公開） | 1営業日 | 2026-09-07 3層通知で先行稼働。「push廃止」案は撤回（朝刊は繰り越し取込を担当） |
| caravan-slack-morning-digest | 平日 7:30 | キャラバンSlack 5スレッドの差分メモ | `経営企画室\レポート\朝メモ\` | 1営業日 | **2026-09-07 再作成**。7/8〜9/7はcwd（共有ドライブの消えたパス）不在で毎朝スキップ＝出力ゼロ62日。定期タスクは必ずローカルcwdのセッションから作る |
| **routine-health-check** | 月曜 7:00 | 本台帳と3層の実行状況・出力鮮度を突合し異常時のみ件数push | `経営企画室\レポート\ルーティン健診\` | 8日 | 2026-09-04新設。外部API・Web検索を使わない最単純構成 |
| adhd-mechanisms-review-20260911 | 単発 2026-09-11 7:00 | ADHD×AI 5つの仕組み（返信待ち/期限危機/叩き台/移動ブロック/クールダウン）の1週間実績集計＋閾値変更案 | `経営企画室\レポート\ADHD5仕組み_1週間見直し_2026-09-11.md` | — | 2026-09-04設定・1回限定。実行後は無効化→`_archive\` 退避（2026-09-07 健診指摘で台帳追記） |
| mytasks-redesign-review-20261009 | 単発 2026-10-09 7:00 | Asanaマイタスク改修（5段・期限なし禁止・次の1手・夕コクピット棚卸し）の1か月実績集計＋閾値変更案 | 経営企画室 レポート（見直しMD）＋push | — | 2026-09-07設定・1回限定。実行後は無効化→_archive 退避（同日再点検で台帳追記） |
| caravan-attach-batch | 平日 8-17時 毎時 | キャラバン徳富メール添付→Asana upload（sweep保険付） | Asanaタスク添付（件数のみpush） | — | **運用オーナー=「キャラバン業務効率化チーム」セッション。他から改修禁止** |
| reply-drafter-hourly | 平日 8-17時 毎時20分 | Gmailラベル「会社」の返信すべき社外メール→竹村名義の返信下書きをGmail同スレッドへ自動作成（送信なし・ラベル「AI下書き」） | Gmail下書き＋data/reply_drafts/控え（件数のみpush） | 2026-09-25新設 | claude CLI認証切れはexit=3で即停止。除外=Cc/社内/ノイズ/既下書き。やり直し `--forget <tid>` |
| plaud-auto-rename | 平日 8:30 / 17:30 | 未命名Plaud録音の自動命名 | Plaud側（ファイル出力なし） | — | 2026-09-04 夕方枠を18:30→17:30へ |
| eigyo2-asana-dashboard | 平日 9:00 | Asana→営業2部進捗ダッシュボード＋期限危機判定・報告下書き | `営業2部\進捗ダッシュボード\進捗ダッシュボード.html` | 1営業日 | 件数push |
| daily-keiei-dashboard | 平日 9:20 / 15:20 | IDS日報PDF→経営ダッシュボード | `経営企画室\日報\経営ダッシュボード.html` | 2営業日 | PDF未着日は朝のみ催促push |
| noon-cockpit | 平日 12:33 | 判断キュー昼版追記（pushなし） | 判断キュー_最新.md | 1営業日 | — |
| plaud-meeting-actions | 平日 17:25 | Plaud録音→アクション抽出→Asanaマイタスク直接登録 | Asanaマイタスク | — | 2026-09-04 18:25→17:25（PlaudSync 17:15の後続） |
| evening-cockpit | 平日 17:45 | 退社前まとめ＋翌日予測＋叩き台の夜間仕込み＋件数push | 判断キュー_最新.md／`営業2部\下書き\叩き台\` | 1営業日 | 2026-09-04 18:37→17:45（PCが18時台に落ち翌朝生成になっていたため） |
| tinplate-ad-watch | 月曜 10:30 | ぶりきAD動向（韓KTC/米AD/日本追随）Web監視 | `営業2部\薄板\AD監視_log.md` | 動きあり時のみ | 第2段で「薄板週次ウォッチ」へ統合予定 |
| asana-knowledge-weekly | 月曜 8:30 | Asana週次差分→ナレッジMD追記＋差分報告 | `営業2部\ナレッジ\Asana\週次差分\` | 8日 | 差分0件は報告MDなし（pushのみ） |
| expense-report-reminder | 毎月25日 9:00 | 経費精算リマインド | push | — | — |
| kakei-monthly | 毎月1日 7:00 | **個人**：マネーフォワード ME を翔さんログイン済み Chrome で読み、前月の収支・純資産・目標 5,000万円への必要ペース vs 実績・未分類チェック → 月次レポート＋CSV。読めなければ催促 push | `PB\家計管理\月次\`（**.gitignore 済み・git に載せない**） | 35日 | 2026-09-26 新設（らすく式「毎月1日の経理自動化」の家計版）。push は金額なし。手動は「家計やって」→ run_scheduled_task。MF 側の追加認証で読めない月は催促モード |
| ~~maker-watch-89ki-20260601~~ | 単発（6/1済） | 重要4メーカー動向brief | — | — | 終了済み・無効。`_archive\` へ退避可 |
| ~~2026-05-07-morning-brief / tomorrow-boost-20260602~~ | 単発（終了済み） | — | — | — | 2026-06-11 `_archive\` 退避済み |

### 1-B. Windowsタスクスケジューラ（ネイティブ・PC ON時のみ・終了コードで健診）
| 名前 | 周期(JST) | 役割 | 出力先（鮮度チェック対象） | 鮮度 | 状態・備考 |
|---|---|---|---|---|---|
| sankoh-mail-hourly | 毎時30分 | POP3同期＋サーバー迷惑メール掃除 | `projects\sankoh-mail-ai\data\sync.log` | 3時間 | メール基盤の心臓。止まるとコクピット全部が古くなる |
| Sanko\ApprovalPoll | 5分毎 | 双方向承認（iPhone 1タップ）＋通知の ✅OK/⏰後で の応答ポーリング | `data\approvals.json`・`data\sho_publish\daily\carryover.json`（繰り越し・GitHub同期） | 1日 | `approve.py --poll`（pythonw）。削除は `schtasks /Delete /TN "Sanko\ApprovalPoll"`。クラウド朝刊06:00が夜間分を二重受信 |
| Sanko\SBT-Poll / SBT-Morning / SBT-Night | 5分毎 / 平日7:00 / 毎日22:30 | SBTメンタルトレーニング 朝夜1タップ＋ストリーク | `data\sbt_streak.json` | 1日 | 承認基盤と分離 |
| steel-radar-daily | 平日 8:40 | 鉄鋼メディア4誌の見出しレーダー→ダイジェスト＋件数push | `鉄鋼新聞\メディアレーダー\レーダー_YYYY-MM-DD.md` | 1営業日 | **2026-09-04修理**（7/16設置以来 PATH未解決で未稼働だった。cmd.exe /c 経由＋pythonフルパスに変更・同日実行で新着81件を確認） |
| tsukan-stats-daily | 毎日 9:05 | 通関統計の新月分を自動追記＋push。**後続で `thin_sheet_ports.py --auto`（薄板・ぶりき輸入統計 港別×国別×月別 11品目・2023〜）が `02_薄板輸入統計.html/.xlsx` を、さらに `--flow export` が `05_薄板輸出統計.html/.xlsx`（輸出11品目・FOB・発生品計付き）を再生成＋push（各々新月検知時のみ）** | `営業2部\薄板\通関統計\`（01=ぶりき/TFS 小家氏版・02=薄板輸入11品目 2026-09-14新設・05=薄板輸出11品目 2026-09-15新設） | 35日 | 月次データなので鮮度は緩め。8月分(9月末)が初本番。手動更新＝`python thin_sheet_ports.py [--flow export]`・全再取得＝`--refetch`。キャッシュ/状態は輸入=ports_cache・輸出=ports_cache_export で分離 |
| genryo-cost-daily | 平日 9:10 | FRED/TE/frankfurter→原料コストxlsx更新 | `営業2部\薄板\原料コスト_自動更新.xlsx` | 2営業日 | 行所有権=備考【自動】 |
| genba-manual-keepalive | 月・木 9:10 | 現場手順ナビ(Firestore)の死活監視 | `sanko-tools\scripts\genba_keepalive.log` | 8日 | 異常時のみpush |
| shintoa-report-monthly | 月曜 9:30 | 新東亜レポート添付→OCR→月次メモリ（raw） | メモリ shintoa_market_raw_* | 動きあり時のみ | 週次に走り新着月のみ処理。**レポート自体が不定期着**（最終受信=6月度・7/13。2026-09-07にGmail検索で7月以降の新着なしを確認）のため鮮度判定は外す。タスク自体の rc≠0 のみ異常扱い |
| Sanko\PlaudSync | 平日 17:15 | Plaud録音→ローカルDB差分同期（公式MCP版） | Plaud DB | 1営業日 | 2026-09-04 18:15→17:15。認証=~\.plaud\tokens-mcp.json（切れたら `npx -y @plaud-ai/mcp@latest install`） |
| sankoh-mark-read-nightly | 毎日 23:30 | 当日メールの既読化（社内含む） | mail.db | 1日 | — |
| ~~sankoh-morning-cockpit~~ | 停止 2026-09-04 | 旧・朝ダッシュボード（4/23以降出力なし・終了コード1で4か月空転） | — | — | 無効化。役割は morning-cockpit が継承済み |
| ~~Sankoh\MorningNews / EveningReport~~ | 停止 2026-09-04 | news_digest / evening_report（生成物を誰も読んでいなかった） | — | — | 無効化。市況は朝刊＋レーダー、夕まとめは evening-cockpit が担う |

### 1-C. クラウドRoutine（claude.ai/code/routines・PC OFFでも稼働・cronはUTC）
| 名前 | 周期(JST) | routine ID | 役割 | 出力先 | 状態・備考 |
|---|---|---|---|---|---|
| **朝刊** | 毎日 6:00 | trig_016vUW7bXRd3Gj6SNAkuuUnh | 市況/未返信メール/Asana/予定＋「今日任せられること3つ」→iPhoneプッシュ | sho repo `daily/YYYYMMDD.md`（**現状は使い捨てブランチ・第2段でmain直書きへ**） | 朝の唯一の受け取り口。ops_log追記は第2段で廃止 |
| キャラバン徳富 自動転記 | 平日 8-17時 毎時 | trig_0173S24SniKqcXWXBTpQ3XWG | Gmail→Asana本文逐語転記・起票・添付ハンドオフ | Asana | **運用オーナー=「キャラバン業務効率化チーム」セッション。他から改修禁止**。洪水ガード・既出確認あり |
| 薄板月次C 需要・在庫・生産 | 11日 9:00 | trig_01RUvTJdiHv9u4kvSCeRNCZS | Web定点調査 | Routine画面のみ | 第2段で「薄板月次ウォッチ」(ローカル)へ統合→無効化 |
| 薄板月次B 原料・スクラップ・為替 | 13日 9:00 | trig_01VYUz3fHw1v9gNR8mKF1tog | 同上 | 同上 | 同上 |
| 薄板月次A ミル価格・契約 | 18・21日 9:00 | trig_014GVaKD1uMFsKWeZckLqGme | 同上 | 同上 | 同上 |
| 薄板ウォッチ④ 週次 | 月曜 9:00 | trig_01LF2y9ZSMFJjcW47XKYuPFe | GI-AD／米イラン停戦／突発 | 同上 | 第2段で「薄板週次ウォッチ」(ローカル)へ統合→無効化 |
| R-weekly 週次振り返り | 日曜 21:00 | trig_01CU46f3Cxopc2NKXn9TRPMs | ops_log/decision_log/preferences の週次集計＋KPI 1問＋昇格チェック | `context/learnings.md` 末尾 | 2026-09-25 Claude が作成（v3 版）。正本 `context/routines/weekly-review.md` |
| R-monthly 月次事実 | 毎月1日 9:00 | trig_01MJ2qKtn299fUCWtT6rrzmi | 前月の週次振り返り・判断ログ・ops_log・宿題・前月の重点3つの達成形跡を集計（/getsuji の「事実」パート） | `経営企画室/レポート/月次壁打ち/YYYYMM_事実.md` | 2026-09-26 新設。朝刊が月初1〜7日に「月次やろうで10分」を出す。正本 `context/routines/monthly-review.md` |
| ~~Morning brief - 三幸商事~~ | 停止 2026-09-04 | trig_011e5vWs4JbZGXHJp72zp4oF | 市況ブリーフ（朝刊と重複・使い捨てブランチ） | — | 無効化済み |
| ~~Weekly review - 24h AI ops~~ | 停止 2026-09-04 | trig_01PnGhFkrXWmYN9gUNfXNtU5 | ops_log集計（誰も書かないログを毎週「停止47日」と誤診） | — | 無効化済み |
| ~~薄板ウォッチ③ 東鉄7月契約~~ | 停止 2026-09-04 | trig_01YT5g2WvviCA8ky4cTcZFYo | 2027年6月に再発火する設定だった | — | 無効化済み |
| ~~旧朝枠／C移行テスト3本／①②~~ | 無効（残骸6本） | 017Bv… / 01NjN… / 01BLe… / 013PG… / 01MnB… / 01Hse… | — | — | **完全削除はWeb画面（claude.ai/code/routines）からのみ＝竹村作業**。APIは無効化まで |

## 2. データパイプライン（projects\・移動禁止）
| 場所 | 役割 | 備考 |
|---|---|---|
| projects\sankoh-mail-ai | メール基盤（mail.db 約10万通・コクピット・タグ・要約・フォロー漏れ抽出follow_gaps） | タグ付け2026-06-11復旧（mail-tagger-daily常設）。フォロー漏れレポート=営業2部\フォロー\ |
| projects\sanko-tools | 業務スクリプト集約（2026-06-11新設）: 経費精算・edoc・Plaud同期・Google Drive/Sheets・正規雛形templates_official・スクショ即AI（scripts\snap 2026-07-02） | 起動口batは会社フォルダ直下。snapはCtrl+Alt+S（デスクトップlnk）→temp\screenshots保存＋パスコピー |
| projects\sanko-tools\scripts\eigyo2_progress_dashboard | 営業2部Asana進捗ダッシュボード描画（build_dashboard.py・data\にMCP生JSON） | 呼び出し元=scheduled-task eigyo2-asana-dashboard |
| projects\estat-trade | 貿易統計 薄板3品パイプライン（月次更新可） | aggregate.py |
| projects\helfecloud-archive | TDBアーカイブ（終了案件・参照のみ） | — |
| 経営企画室\日報\build_*.py | 日次ダッシュボード（dashboard/plan/master） | データ近接配置 |
| 経営企画室\IDS\ | IDS基幹システム知識ベース（マニュアル352頁を全頁知識化 2026-06-11） | 総覧+6分冊。原本=\\192.168.1.126\全社共有\idsマニュアル.pdf |
| 経営企画室\アシスト\ | アシスト(三幸プロダクツ生産管理)知識ベース（マニュアル159頁を全頁知識化 2026-06-12） | 総覧+6分冊。原本=\\192.168.1.126\本社\アシストマニュアル動画\（動画もあり） |

## 3. 秘密情報の所在（共有ドライブ・OneDrive圏外）
| 場所 | 中身 |
|---|---|
| `C:\Users\FONE\.secrets\` | Google OAuth（credentials.json/token.pickle/client_secret*）・edoc_config.json |
| `projects\sankoh-mail-ai\.env` | ASANA_PAT 等 |
| `projects\sankoh-mail-ai\data\` | gmail_credentials/token・notify.json（ntfyトピック） |
| `temp\_89keikaku_readonly.xlsx` | 計画原紙ローカルコピー（原本=共有ドライブ・書込禁止） |

## 4. AI運用の構造（2026-06-11 再設計後）
- **3層**: 成果物=`三幸商事株式会社\`／自動化=`projects\`／AI運用=`.claude\`
- **人格制度は廃止**。スキル: `mail-ops`（旧ノブ）・`design-studio`（旧マナ）・`thin-sheet-sales`（旧テツ・2026-06-11新設）・`virtual-board`（バーチャル役員会・2026-07-02新設）・`contract-review`（契約書チェック・2026-07-02新設）・`proposal-review`（添削パターン学習型資料レビュー・2026-07-02新設）・`cool-down`（衝動返信のクールダウン翻訳・2026-09-04新設）。PM動作原則はグローバルCLAUDE.md
- **ADHD×AI 5つの仕組み（ma-ji記事3本目・2026-09-04実装）**: ①遅刻=スクショ即登録＋移動/準備ブロック自動挿入（CLAUDE.md）②返信漏れ=`sankoh-mail-ai\scripts\reply_nag.py` 返信待ちキュー（N日目カウント・朝コクピット同梱）③後回し=白紙脱出ルール＋夕コクピットの叩き台夜間仕込み（`営業2部\下書き\叩き台\`）④衝動返信=`cool-down`スキル⑤遅延報告=Asanaダッシュボード9:00に期限危機判定＋報告下書き（`営業2部\進捗ダッシュボード\期限危機_最新.md`）
- **長期記憶は自動メモリ（MEMORY.md）一本**。旧経験ログ7本は `.claude\agents\_archive\` に凍結（caravan等の詳細参照先）
- 再設計計画書: `経営企画室\プロジェクト\AI基盤再設計\20260611_AI基盤再設計計画.md`

## 5. 安全制御（Hooks・2026-07-02新設）
- **ガードフック**: `.claude\hooks\guard.py` — 全Claude Codeセッションのツール実行前（PreToolUse）に自動検査。配線=`.claude\settings.json` の `hooks` キー
- ブロック対象（CLAUDE.md守秘原則の機械化）:
  1. 共有ドライブ `\\192.168.1.126` への書き込み・削除（読み取り・共有→ローカルのコピーは許可）
  2. 保護ルート（三幸商事株式会社\・projects\・.claude\・.secrets\）の再帰削除、.secretsとメモリの削除全般
  3. ntfy/プッシュ通知への固有名詞（社名・人名・得意先名。日本語表記で照合＝ASCIIトピック名は誤検知しない）
  4. ホーム直下への新規フォルダ作成（既存フォルダ配下はOK・実在チェック方式）
  5. shutdown・format等のシステム破壊操作
- 判定不能時はフェイルオープン（通過）。ブロック時はClaudeに理由が返り代替手段を取る
- テスト22ケースで検証済み（2026-07-02）。誤ブロックが出たら guard.py の該当正規表現を調整
- 併せて settings.json 内に平文残存していた旧トークン埋込permissionルールを削除済み

## 6. 月次棚卸しチェックリスト
- [ ] scheduled-tasks: 終了済み単発タスクの削除・lastRun確認
- [ ] クラウドRoutine: 稼働確認・停止条件到達の有無
- [ ] ⚠継続課題: 毎月会議資料の自動生成（タグ付け・仕入側明細分析は6/11完了）
- [ ] このファイルの日付更新
