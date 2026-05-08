import express from 'express';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { execSync } from 'child_process';

const PORT = process.env.MCP_PORT || 3456;

function getToken() {
  if (process.env.MCP_TOKEN) return process.env.MCP_TOKEN;
  const tokenFile = path.join(import.meta.dirname, 'mcp-token.txt');
  return fs.readFileSync(tokenFile, 'utf8').trim();
}

function getAsanaToken() {
  try {
    const settingsPath = path.join(process.env.USERPROFILE || os.homedir(), '.claude', 'settings.json');
    const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    return settings?.mcpServers?.asana?.env?.ASANA_ACCESS_TOKEN || process.env.ASANA_ACCESS_TOKEN || '';
  } catch {
    return process.env.ASANA_ACCESS_TOKEN || '';
  }
}


function formatIcsDate(date) {
  return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
}

function escapeIcsText(text) {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/\r?\n/g, '\\n')
    .replace(/,/g, '\\,')
    .replace(/;/g, '\\;');
}

function createMcpServer() {
  const server = new McpServer({ name: 'sanko-local-mcp', version: '1.0.0' });

  server.tool('read_file', 'ローカルファイルを読み込む', {
    path: z.string().describe('ファイルパス（絶対パス）'),
  }, async ({ path: filePath }) => {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      return { content: [{ type: 'text', text: content }] };
    } catch (e) {
      return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
    }
  });

  server.tool('write_file', 'ローカルファイルに書き込む', {
    path: z.string().describe('ファイルパス（絶対パス）'),
    content: z.string().describe('書き込む内容'),
  }, async ({ path: filePath, content }) => {
    try {
      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      fs.writeFileSync(filePath, content, 'utf8');
      return { content: [{ type: 'text', text: `Written: ${filePath}` }] };
    } catch (e) {
      return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
    }
  });

  server.tool('list_dir', 'ディレクトリの内容一覧を取得する', {
    path: z.string().describe('ディレクトリパス'),
  }, async ({ path: dirPath }) => {
    try {
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });
      const list = entries.map(e => `${e.isDirectory() ? '[DIR] ' : '[FILE]'} ${e.name}`).join('\n');
      return { content: [{ type: 'text', text: list || '（空のディレクトリ）' }] };
    } catch (e) {
      return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
    }
  });

  server.tool('run_powershell', 'PowerShell コマンドを実行する', {
    command: z.string().describe('実行する PowerShell コマンド'),
  }, async ({ command }) => {
    const tmpFile = path.join(os.tmpdir(), `mcp-${Date.now()}.ps1`);
    try {
      fs.writeFileSync(tmpFile, command, 'utf8');
      const output = execSync(
        `powershell -NoProfile -ExecutionPolicy Bypass -File "${tmpFile}"`,
        { encoding: 'utf8', timeout: 60000 }
      );
      return { content: [{ type: 'text', text: output || '（出力なし）' }] };
    } catch (e) {
      return { content: [{ type: 'text', text: `Error: ${e.message}\n${e.stdout || ''}` }], isError: true };
    } finally {
      try { fs.unlinkSync(tmpFile); } catch {}
    }
  });

  server.tool('asana_api', 'Asana API を呼び出す（クラウド制限を迂回）', {
    method: z.enum(['GET', 'POST', 'PUT', 'DELETE']).describe('HTTP メソッド'),
    endpoint: z.string().describe('エンドポイント（例: /tasks?assignee=me&...）'),
    body: z.record(z.unknown()).optional().describe('POST/PUT 時のリクエストボディ'),
  }, async ({ method, endpoint, body }) => {
    try {
      const token = getAsanaToken();
      if (!token) throw new Error('Asana トークンが設定されていません（settings.json を確認してください）');
      const res = await fetch(`https://app.asana.com/api/1.0${endpoint}`, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify({ data: body }) : undefined,
      });
      const data = await res.json();
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    } catch (e) {
      return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
    }
  });


  server.tool('create_calendar_event_ics', 'カレンダー登録用のICSファイルを作成する', {
    title: z.string().describe('予定タイトル'),
    start: z.string().describe('開始日時（ISO形式。例: 2026-05-03T01:00:00Z）'),
    end: z.string().describe('終了日時（ISO形式。例: 2026-05-03T02:00:00Z）'),
    description: z.string().optional().describe('詳細メモ'),
    location: z.string().optional().describe('場所'),
    outputPath: z.string().optional().describe('出力先パス（省略時はtmp）'),
  }, async ({ title, start, end, description, location, outputPath }) => {
    try {
      const startDate = new Date(start);
      const endDate = new Date(end);
      if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
        throw new Error('start/end は ISO 8601 形式で指定してください');
      }
      if (endDate <= startDate) {
        throw new Error('end は start より後にしてください');
      }

      const uid = `${Date.now()}-${Math.random().toString(36).slice(2)}@sanko-local-mcp`;
      const dtStamp = formatIcsDate(new Date());
      const dtStart = formatIcsDate(startDate);
      const dtEnd = formatIcsDate(endDate);
      const lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Sanko Shoji//Local MCP//JA',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        `UID:${uid}`,
        `DTSTAMP:${dtStamp}`,
        `DTSTART:${dtStart}`,
        `DTEND:${dtEnd}`,
        `SUMMARY:${escapeIcsText(title)}`,
      ];
      if (description) lines.push(`DESCRIPTION:${escapeIcsText(description)}`);
      if (location) lines.push(`LOCATION:${escapeIcsText(location)}`);
      lines.push('END:VEVENT', 'END:VCALENDAR');
      const content = `${lines.join('\r\n')}\r\n`;

      const filePath = outputPath || path.join(os.tmpdir(), `calendar-event-${Date.now()}.ics`);
      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      fs.writeFileSync(filePath, content, 'utf8');

      return {
        content: [{
          type: 'text',
          text: `ICSファイルを作成しました: ${filePath}\nGoogleカレンダーで「インポート」から登録してください。`,
        }],
      };
    } catch (e) {
      return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
    }
  });

  server.tool('read_claude_settings', 'Claude の settings.json を読む', {}, async () => {
    try {
      const p = path.join(process.env.USERPROFILE || os.homedir(), '.claude', 'settings.json');
      return { content: [{ type: 'text', text: fs.readFileSync(p, 'utf8') }] };
    } catch (e) {
      return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
    }
  });

  server.tool('write_claude_settings', 'Claude の settings.json を更新する', {
    content: z.string().describe('新しい JSON 文字列'),
  }, async ({ content }) => {
    try {
      const p = path.join(process.env.USERPROFILE || os.homedir(), '.claude', 'settings.json');
      JSON.parse(content); // 構文チェック
      fs.writeFileSync(p, content, 'utf8');
      return { content: [{ type: 'text', text: 'settings.json を更新しました' }] };
    } catch (e) {
      return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
    }
  });

  return server;
}

const app = express();
app.use(express.json());

// 認証ミドルウェア
app.use('/mcp', (req, res, next) => {
  const auth = req.headers['authorization'] || '';
  try {
    if (auth !== `Bearer ${getToken()}`) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
  } catch {
    return res.status(500).json({ error: 'Token file not found. Run setup.bat first.' });
  }
  next();
});

app.all('/mcp', async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  const mcpServer = createMcpServer();
  await mcpServer.connect(transport);
  await transport.handleRequest(req, res, req.body);
  res.on('finish', () => mcpServer.close().catch(() => {}));
});

app.get('/health', (_req, res) => res.json({ status: 'ok', service: 'sanko-local-mcp' }));

app.listen(PORT, () => {
  console.log(`[Sanko Local MCP] ポート ${PORT} で起動しました`);
});
