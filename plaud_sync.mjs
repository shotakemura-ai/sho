#!/usr/bin/env node
/**
 * Plaud 録音データ同期スクリプト
 * 文字起こし・サマリーを取得してMarkdownファイルとして保存
 */
import fs from 'fs';
import path from 'path';
import zlib from 'zlib';
import { promisify } from 'util';

const gunzip = promisify(zlib.gunzip);

const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxOWFiZTE4YjgwYTM3NjhkNWMxM2VhZGRhN2RiYjRjNyIsImF1ZCI6IiIsImV4cCI6MTc5MzY5Mzc2OSwiaWF0IjoxNzY3NzczNzY5LCJjbGllbnRfaWQiOiJ3ZWIiLCJyZWdpb24iOiJhd3M6dXMtd2VzdC0yIn0.dR27Z9RjEaAGiEV08TAxXVwdQgamuV3omn9UIz0Ghv0";
const BASE = "https://api-apne1.plaud.ai";
const HEADERS = {
  "Authorization": `Bearer ${TOKEN}`,
  "Origin": "https://web.plaud.ai",
  "Referer": "https://web.plaud.ai/",
  "app-platform": "web",
  "timezone": "Asia/Tokyo",
};

const OUT_DIR = path.join(import.meta.dirname, '鉄鋼事業部/営業/会議資料/Plaud録音データベース');
const INDEX_FILE = path.join(OUT_DIR, '_index.json');

async function fetchAPI(endpoint) {
  const res = await fetch(`${BASE}${endpoint}`, { headers: HEADERS });
  if (!res.ok) throw new Error(`API error ${res.status}: ${endpoint}`);
  return res.json();
}

async function fetchS3Gz(url) {
  const res = await fetch(url);
  if (!res.ok) return null;
  const buf = Buffer.from(await res.arrayBuffer());
  try {
    const decompressed = await gunzip(buf);
    return JSON.parse(decompressed.toString('utf8'));
  } catch {
    return JSON.parse(buf.toString('utf8'));
  }
}

function formatDate(ts) {
  return new Date(ts).toLocaleDateString('ja-JP', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    timeZone: 'Asia/Tokyo'
  }).replace(/\//g, '-');
}

function formatDuration(ms) {
  const m = Math.floor(ms / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  return `${m}分${s}秒`;
}

function sceneLabel(scene) {
  return { 1: '対面録音', 7: '通話録音', 102: 'デスクトップ' }[scene] || `scene${scene}`;
}

async function syncRecording(rec, existingIds) {
  if (existingIds.has(rec.id)) return null; // スキップ（既存）
  if (!rec.is_trans && !rec.is_summary) return null; // 文字起こしなし

  try {
    const detail = await fetchAPI(`/file/detail/${rec.id}`);
    const d = detail.data || detail;
    const cl = d.content_list || [];

    // サマリー取得（pre_download_content_listから）
    const predownload = d.pre_download_content_list || [];
    let summary = '';
    for (const p of predownload) {
      try {
        const c = typeof p.data_content === 'string' ? JSON.parse(p.data_content) : p.data_content;
        if (c?.ai_content) { summary = c.ai_content; break; }
      } catch {}
    }

    // 文字起こし取得（S3から）
    let transcript = '';
    const txItem = cl.find(c => c.data_type === 'transaction');
    if (txItem?.data_link) {
      const txData = await fetchS3Gz(txItem.data_link);
      if (txData) {
        // trans_result.json の形式: { data: [ { speaker, text, start_time, end_time } ] }
        const segments = txData.data || txData.trans_list || txData.result || [];
        if (Array.isArray(segments)) {
          transcript = segments.map(seg => {
            const speaker = seg.speaker_id !== undefined ? `話者${seg.speaker_id}` : '';
            const text = seg.text || seg.trans_text || '';
            return speaker ? `**${speaker}**: ${text}` : text;
          }).join('\n');
        } else if (typeof txData === 'string') {
          transcript = txData;
        }
      }
    }

    // Markdownファイル作成
    const date = formatDate(rec.start_time);
    const safeName = rec.filename.replace(/[\\/:*?"<>|]/g, '_');
    const filename = `${safeName}.md`;
    const filepath = path.join(OUT_DIR, filename);

    const md = [
      `# ${rec.filename}`,
      '',
      `| 項目 | 内容 |`,
      `|------|------|`,
      `| 日時 | ${date} |`,
      `| 録音時間 | ${formatDuration(rec.duration)} |`,
      `| 種別 | ${sceneLabel(rec.scene)} |`,
      `| ID | ${rec.id} |`,
      '',
      summary ? `## サマリー\n\n${summary}\n` : '',
      transcript ? `## 文字起こし\n\n${transcript}\n` : '',
    ].filter(l => l !== undefined).join('\n');

    fs.writeFileSync(filepath, md, 'utf8');
    return { id: rec.id, filename: rec.filename, date, filepath: filename };
  } catch (err) {
    console.error(`  [ERROR] ${rec.filename}: ${err.message}`);
    return null;
  }
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  // 既存インデックス読み込み
  let index = [];
  const existingIds = new Set();
  if (fs.existsSync(INDEX_FILE)) {
    try {
      index = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
      index.forEach(r => existingIds.add(r.id));
      console.log(`既存: ${existingIds.size}件`);
    } catch {}
  }

  // 全録音一覧取得
  console.log('録音一覧を取得中...');
  const listData = await fetchAPI('/file/simple/web?skip=0&limit=600');
  const allRecs = (listData.data_file_list || []).filter(r => !r.is_trash);
  console.log(`総録音数: ${allRecs.length}件（文字起こしあり: ${allRecs.filter(r=>r.is_trans).length}件）`);

  // 新規のみ同期（最新から）
  const newRecs = allRecs.filter(r => !existingIds.has(r.id) && (r.is_trans || r.is_summary));
  console.log(`新規同期対象: ${newRecs.length}件`);

  let done = 0;
  for (const rec of newRecs) {
    process.stdout.write(`\r同期中... ${done}/${newRecs.length}: ${rec.filename.slice(0,40)}`);
    const result = await syncRecording(rec, existingIds);
    if (result) {
      index.push(result);
      existingIds.add(rec.id);
    }
    done++;
    // レート制限対策
    await new Promise(r => setTimeout(r, 200));
  }

  console.log(`\n完了: ${done}件処理`);

  // インデックス保存（日付降順）
  index.sort((a, b) => b.date.localeCompare(a.date));
  fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2), 'utf8');

  // 検索用マスターインデックスMarkdown作成
  const masterMd = [
    '# Plaud録音データベース インデックス',
    '',
    `最終更新: ${new Date().toLocaleDateString('ja-JP')}　総件数: ${index.length}件`,
    '',
    '| 日付 | タイトル |',
    '|------|---------|',
    ...index.map(r => `| ${r.date} | [${r.filename}](${r.filepath}) |`),
  ].join('\n');

  fs.writeFileSync(path.join(OUT_DIR, '_index.md'), masterMd, 'utf8');
  console.log(`インデックス保存: ${INDEX_FILE}`);
}

main().catch(console.error);
