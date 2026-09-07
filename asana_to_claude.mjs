#!/usr/bin/env node
/**
 * asana_to_claude.mjs
 * Asana の最新タスクを取得して context/asana-live.md に書き出す
 * 使い方: node asana_to_claude.mjs
 * 定期実行: タスクスケジューラ or cron で毎朝実行推奨
 */

import { execSync } from 'child_process';
import { writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// トークンを環境変数 or Windows 環境変数から取得
const TOKEN = process.env.ASANA_ACCESS_TOKEN
  ?? execSync('powershell -Command "[System.Environment]::GetEnvironmentVariable(\'ASANA_ACCESS_TOKEN\', \'User\')"', { encoding: 'utf8' }).trim();

const WORKSPACE_GID = '1203471303375035';
const USER_GID = '1204898614412973';
const BASE_URL = 'https://app.asana.com/api/1.0';

async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${TOKEN}` }
  });
  if (!res.ok) throw new Error(`Asana API error: ${res.status} ${await res.text()}`);
  return (await res.json()).data;
}

async function main() {
  console.log('Asana からデータ取得中...');
  const now = new Date().toISOString();

  // 自分にアサインされた未完了タスク
  const myTasks = await get(
    `/tasks?assignee=${USER_GID}&workspace=${WORKSPACE_GID}&completed_since=now&opt_fields=name,due_on,assignee_status,projects.name,notes&limit=100`
  );

  // プロジェクト別に分類
  const byProject = {};
  const noProject = [];
  for (const task of myTasks) {
    const projects = task.projects ?? [];
    if (projects.length === 0) {
      noProject.push(task);
    } else {
      for (const p of projects) {
        if (!byProject[p.name]) byProject[p.name] = [];
        byProject[p.name].push(task);
      }
    }
  }

  // Markdown 生成
  let md = `# Asana ライブデータ\n\n`;
  md += `> 最終更新: ${now.replace('T', ' ').slice(0, 19)} JST\n`;
  md += `> 未完了タスク合計: ${myTasks.length} 件\n\n`;

  // 期限切れ・今日のタスクを先頭に
  const today = new Date().toISOString().slice(0, 10);
  const overdue = myTasks.filter(t => t.due_on && t.due_on < today);
  const dueToday = myTasks.filter(t => t.due_on === today);

  if (overdue.length > 0) {
    md += `## 🔴 期限超過 (${overdue.length}件)\n\n`;
    for (const t of overdue) md += `- [ ] **${t.name}** — 期限: ${t.due_on}\n`;
    md += '\n';
  }

  if (dueToday.length > 0) {
    md += `## 🟡 今日期限 (${dueToday.length}件)\n\n`;
    for (const t of dueToday) md += `- [ ] **${t.name}**\n`;
    md += '\n';
  }

  // プロジェクト別
  md += `## プロジェクト別タスク\n\n`;
  for (const [proj, tasks] of Object.entries(byProject).sort()) {
    md += `### ${proj} (${tasks.length}件)\n\n`;
    for (const t of tasks) {
      const due = t.due_on ? ` — 期限: ${t.due_on}` : '';
      md += `- [ ] ${t.name}${due}\n`;
    }
    md += '\n';
  }

  if (noProject.length > 0) {
    md += `### プロジェクト未割当 (${noProject.length}件)\n\n`;
    for (const t of noProject) md += `- [ ] ${t.name}\n`;
    md += '\n';
  }

  // ファイルに書き出し
  const outputPath = join(__dirname, 'context', 'asana-live.md');
  writeFileSync(outputPath, md, 'utf8');
  console.log(`✅ context/asana-live.md を更新しました (${myTasks.length}件)`);

  // Git コミット＆プッシュ
  try {
    execSync('git add context/asana-live.md && git commit -m "chore: Asana タスク自動同期" && git push', {
      cwd: __dirname,
      stdio: 'inherit'
    });
    console.log('✅ Git にプッシュしました');
  } catch (e) {
    console.log('⚠️  Git プッシュ失敗（変更なしの可能性あり）');
  }
}

main().catch(err => { console.error('❌ エラー:', err.message); process.exit(1); });
