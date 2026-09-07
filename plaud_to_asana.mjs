/**
 * plaud_to_asana.mjs
 *
 * Plaud録音データベースからアクションアイテムを抽出し、
 * Asanaタスクを対話的に作成するスクリプト。
 *
 * 使い方:
 *   node plaud_to_asana.mjs
 *   または「Plaudタスク登録.bat」をダブルクリック
 *
 * 動作フロー:
 *   1. _index.json から未処理の録音を取得
 *   2. 各録音の Markdown ファイルからアクションアイテムを抽出
 *   3. 対話的にプロジェクト選択 → Asana タスク作成
 *   4. 処理済みIDを .plaud_asana_state.json に保存（再実行時はスキップ）
 */

import fs from 'fs';
import path from 'path';
import readline from 'readline/promises';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ─────────────────────────────────────────────
// 設定定数
// ─────────────────────────────────────────────
const PLAUD_DB   = path.join(__dirname, '鉄鋼事業部/営業/会議資料/Plaud録音データベース');
const INDEX_FILE = path.join(PLAUD_DB, '_index.json');
const STATE_FILE = path.join(__dirname, '.plaud_asana_state.json');

const ASANA_BASE          = 'https://app.asana.com/api/1.0';
const ASANA_USER_GID      = '1204898614412973';
const ASANA_WORKSPACE_GID = '1203471303375035';

// ─────────────────────────────────────────────
// Asana プロジェクト一覧
// ─────────────────────────────────────────────
const PROJECTS = [
  { name: '通常タスク＠本社営業2部',         gid: '1203477948026491' },
  { name: '株式会社ぺノンプロジェクト',       gid: '1204811624267010' },
  { name: 'アクリル事業プロジェクト',         gid: '1204811624267013' },
  { name: '株式会社KANDOプロジェクト',        gid: '1204811624267016' },
  { name: '缶バッジマシン開発プロジェクト',   gid: '1204811624267034' },
  { name: 'ヒンジクリップ、ヒンジスタンド開発', gid: '1204965209456897' },
  { name: '缶バッジ自動機開発',               gid: '1204965209456903' },
  { name: 'キャラバン受注管理',               gid: '1206333702976778' },
  { name: '通常タスク＠三幸プロダクツ',       gid: '1206916985005725' },
  { name: 'ツインクル受注ガントチャート',     gid: '1208188795532620' },
];

// ─────────────────────────────────────────────
// Asana トークン取得
// ─────────────────────────────────────────────
function getAsanaToken() {
  try {
    const settings = JSON.parse(fs.readFileSync('C:/Users/FONE/.claude/settings.json', 'utf8'));
    return settings.mcpServers.asana.env.ASANA_ACCESS_TOKEN;
  } catch (err) {
    throw new Error(`Asanaトークンの取得に失敗しました: ${err.message}`);
  }
}

// ─────────────────────────────────────────────
// アクションアイテム抽出
// ─────────────────────────────────────────────
/**
 * Markdown コンテンツから「## アクションアイテム」セクションを解析し、
 * { text, deadline, owner } の配列を返す。
 */
function extractActionItems(mdContent) {
  const items = [];

  //「## アクションアイテム」セクションを切り出す
  const sectionMatch = mdContent.match(/## アクションアイテム([\s\S]*?)(?=\n## |\n# |$)/);
  if (!sectionMatch) return items;

  const section = sectionMatch[1];
  const lines = section.split('\n');

  let currentOwner = null;

  for (const line of lines) {
    // 担当者行: ### **@...** または ### **名前** など
    const ownerMatch = line.match(/^###\s+\*{0,2}@?(.+?)\*{0,2}\s*$/);
    if (ownerMatch) {
      currentOwner = ownerMatch[1].trim();
      continue;
    }

    // アクションアイテム行: - [ ] テキスト
    const itemMatch = line.match(/^-\s+\[\s*\]\s+(.+)$/);
    if (itemMatch) {
      let text = itemMatch[1].trim();
      let deadline = null;

      // 末尾の " - [XXX]" を期限として分離
      const deadlineMatch = text.match(/^(.*?)\s+-\s+\[([^\]]+)\]$/);
      if (deadlineMatch) {
        text     = deadlineMatch[1].trim();
        deadline = deadlineMatch[2].trim();
      }

      items.push({ text, deadline, owner: currentOwner });
    }
  }

  return items;
}

// ─────────────────────────────────────────────
// 期限日の変換
// ─────────────────────────────────────────────
/**
 * deadline 文字列と録音日付（YYYY-MM-DD）から due_on 文字列（YYYY-MM-DD or null）を返す。
 */
function parseDueDate(deadline, recordingDate) {
  if (!deadline || deadline === 'TBD') return null;

  if (deadline === '翌日') {
    const d = new Date(recordingDate);
    d.setDate(d.getDate() + 1);
    return d.toISOString().slice(0, 10);
  }

  if (deadline === '本日中') {
    return recordingDate;
  }

  // YYYY-MM-DD 形式ならそのまま返す
  if (/^\d{4}-\d{2}-\d{2}$/.test(deadline)) {
    return deadline;
  }

  return null;
}

// ─────────────────────────────────────────────
// Asana タスク作成
// ─────────────────────────────────────────────
/**
 * Asana API でタスクを作成する。成功したらタスクオブジェクトを返す。
 */
async function createAsanaTask(token, taskName, notes, projectGid, dueOn) {
  const body = {
    data: {
      name:      taskName,
      notes:     notes || '',
      assignee:  ASANA_USER_GID,
      workspace: ASANA_WORKSPACE_GID,
      projects:  [projectGid],
    },
  };
  if (dueOn) body.data.due_on = dueOn;

  const res = await fetch(`${ASANA_BASE}/tasks`, {
    method:  'POST',
    headers: {
      Authorization:  `Bearer ${token}`,
      'Content-Type': 'application/json',
      Accept:         'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errText}`);
  }

  const json = await res.json();
  return json.data;
}

// ─────────────────────────────────────────────
// 状態管理
// ─────────────────────────────────────────────
function loadState() {
  if (fs.existsSync(STATE_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    } catch {
      return { processedIds: [] };
    }
  }
  return { processedIds: [] };
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
}

// ─────────────────────────────────────────────
// ユーティリティ
// ─────────────────────────────────────────────

/** 録音エントリの日付を YYYY-MM-DD 形式で返す（取得できなければ null）*/
function getRecordingDate(entry) {
  // entry.date または entry.recording_date など形式が異なる場合に対応
  const raw = entry.date || entry.recording_date || entry.createdAt || null;
  if (!raw) return null;
  // ISO 文字列や YYYY-MM-DD はそのまま最初の10文字を使う
  return String(raw).slice(0, 10);
}

/** MM-DD 形式の短縮日付を返す */
function shortDate(dateStr) {
  if (!dateStr) return '??-??';
  return dateStr.slice(5); // YYYY-MM-DD → MM-DD
}

// ─────────────────────────────────────────────
// メイン処理
// ─────────────────────────────────────────────
async function main() {
  console.log('\n=== Plaud → Asana タスク登録 ===\n');

  // トークン取得
  let token;
  try {
    token = getAsanaToken();
  } catch (err) {
    console.error(`エラー: ${err.message}`);
    process.exit(1);
  }

  // インデックスファイル確認
  if (!fs.existsSync(INDEX_FILE)) {
    console.error(`エラー: インデックスファイルが見つかりません。\n  ${INDEX_FILE}`);
    console.error('先に plaud_sync.mjs を実行してデータベースを同期してください。');
    process.exit(1);
  }

  // インデックス読み込み
  let index;
  try {
    index = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
  } catch (err) {
    console.error(`エラー: インデックスファイルの読み込みに失敗しました: ${err.message}`);
    process.exit(1);
  }

  // 配列形式・オブジェクト形式どちらでも対応
  const allEntries = Array.isArray(index) ? index : (index.recordings || index.items || Object.values(index));

  // 状態読み込み
  const isFirstRun = !fs.existsSync(STATE_FILE);
  const state = loadState();
  const processedSet = new Set(state.processedIds);

  // readline インターフェース
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

  // 未処理エントリを絞り込む
  let unprocessed = allEntries.filter(e => !processedSet.has(e.id));

  // 初回実行時: 対象日付の絞り込み
  if (isFirstRun && unprocessed.length > 0) {
    const answer = await rl.question(
      'いつ以降の録音を対象にしますか？（例: 2026-03-20、全件=Enter）> '
    );
    const cutoff = answer.trim();
    if (cutoff) {
      const before = unprocessed.filter(e => {
        const d = getRecordingDate(e);
        return d && d < cutoff;
      });
      // 対象外は処理済みとしてスキップ
      for (const e of before) processedSet.add(e.id);
      unprocessed = unprocessed.filter(e => {
        const d = getRecordingDate(e);
        return d && d >= cutoff;
      });
      console.log(`  → ${cutoff} 以降の録音 ${unprocessed.length} 件を対象にします。\n`);
    } else {
      console.log(`  → 全件（${unprocessed.length} 件）を対象にします。\n`);
    }
  }

  // アクションアイテムの有無で分類
  const withItems    = [];
  const withoutItems = [];

  for (const entry of unprocessed) {
    const mdPath = path.join(PLAUD_DB, entry.filepath || `${entry.id}.md`);
    let items = [];

    if (fs.existsSync(mdPath)) {
      try {
        const content = fs.readFileSync(mdPath, 'utf8');
        items = extractActionItems(content);
      } catch {
        // 読み取り失敗はアイテムなし扱い
      }
    }

    if (items.length > 0) {
      withItems.push({ entry, items, mdPath });
    } else {
      withoutItems.push(entry);
    }
  }

  // アクションアイテムなしの録音は自動スキップ
  for (const e of withoutItems) processedSet.add(e.id);
  let skippedCount = withoutItems.length;

  // 既に対象外にしたものも保存（初回絞り込み分）
  state.processedIds = [...processedSet];
  saveState(state);

  console.log(`新規録音: ${unprocessed.length} 件（うちアクションアイテムあり: ${withItems.length} 件）`);
  if (skippedCount > 0) {
    console.log(`アクションアイテムなしの録音 ${skippedCount} 件を自動スキップしました。`);
  }

  if (withItems.length === 0) {
    console.log('\n登録対象のアクションアイテムはありません。\n');
    rl.close();
    return;
  }

  let totalCreated = 0;

  // 録音ごとに対話処理
  for (const { entry, items } of withItems) {
    const recDate = getRecordingDate(entry);
    const title   = entry.filename || entry.title || entry.name || entry.id;

    console.log('\n' + '━'.repeat(50));
    console.log(`📋 ${shortDate(recDate)} ${title}`);
    console.log(`   日時: ${recDate || '不明'}\n`);

    // アクションアイテム一覧表示
    items.forEach((item, idx) => {
      const deadlineStr = item.deadline ? ` [${item.deadline}]` : '';
      const ownerStr    = item.owner    ? ` (${item.owner})`    : '';
      console.log(`  ${idx + 1}. ${item.text}${deadlineStr}${ownerStr}`);
    });

    // プロジェクト選択
    console.log('\n登録先プロジェクト:');
    PROJECTS.forEach((p, idx) => {
      console.log(`  ${idx + 1}. ${p.name}`);
    });
    console.log('  0. この録音をスキップ');

    const projAnswer = await rl.question('\nプロジェクト番号を入力 > ');
    const projNum = parseInt(projAnswer.trim(), 10);

    if (!projNum || projNum < 1 || projNum > PROJECTS.length) {
      console.log('  → スキップしました。');
      processedSet.add(entry.id);
      state.processedIds = [...processedSet];
      saveState(state);
      continue;
    }

    const selectedProject = PROJECTS[projNum - 1];
    console.log(`  → プロジェクト: ${selectedProject.name}`);

    // 登録項目の選択
    const itemAnswer = await rl.question(
      '登録する項目（全て=Enter / 番号指定=1,2,3 / スキップ=s）> '
    );
    const itemInput = itemAnswer.trim().toLowerCase();

    if (itemInput === 's') {
      console.log('  → スキップしました。');
      processedSet.add(entry.id);
      state.processedIds = [...processedSet];
      saveState(state);
      continue;
    }

    // 登録対象のインデックスを決定
    let targetIndices;
    if (itemInput === '') {
      targetIndices = items.map((_, i) => i);
    } else {
      targetIndices = itemInput
        .split(',')
        .map(s => parseInt(s.trim(), 10) - 1)
        .filter(i => i >= 0 && i < items.length);
    }

    if (targetIndices.length === 0) {
      console.log('  → 有効な番号がありませんでした。スキップします。');
      processedSet.add(entry.id);
      state.processedIds = [...processedSet];
      saveState(state);
      continue;
    }

    // タスク作成実行
    let createdCount = 0;
    for (const idx of targetIndices) {
      const item    = items[idx];
      const dueOn   = parseDueDate(item.deadline, recDate);
      const notes   = [
        `録音: ${title}`,
        `日時: ${recDate || '不明'}`,
        item.owner ? `担当者: ${item.owner}` : null,
        item.deadline ? `期限メモ: ${item.deadline}` : null,
      ].filter(Boolean).join('\n');

      try {
        const task = await createAsanaTask(token, item.text, notes, selectedProject.gid, dueOn);
        console.log(`  ✓ [${idx + 1}] タスク作成: ${task.name}`);
        createdCount++;
        totalCreated++;
      } catch (err) {
        console.error(`  ✗ [${idx + 1}] タスク作成失敗: ${err.message}`);
      }
    }

    console.log(`  → ${createdCount} 件のタスクを作成しました。`);

    // 処理済みに追加して即座に保存
    processedSet.add(entry.id);
    state.processedIds = [...processedSet];
    state.lastRun = new Date().toISOString();
    saveState(state);
  }

  rl.close();

  console.log('\n' + '━'.repeat(50));
  console.log(`\n完了: 合計 ${totalCreated} 件のタスクを作成しました。\n`);
}

main().catch(err => {
  console.error(`\n予期せぬエラーが発生しました: ${err.message}`);
  process.exit(1);
});
