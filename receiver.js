import express from 'express';
import { rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const projectDir = path.dirname(fileURLToPath(import.meta.url));
export const reportFile = process.env.REPORT_FILE || path.join(projectDir, 'test-report.json');

export function createReceiver() {
  const app = express();
  app.use(express.json({ limit: '2mb' }));
  app.get('/', (_req, res) => res.json({ message: 'Receiver is running. POST reports to /report' }));
  app.get('/health', (_req, res) => res.json({ status: 'ok' }));
  app.post('/report', async (req, res, next) => {
    const token = process.env.REPORT_TOKEN || '';
    if (token && req.get('x-report-token') !== token) return res.status(401).json({ message: 'Invalid token' });
    const report = req.body;
    if (!report || typeof report !== 'object' || !report.summary || !Array.isArray(report.tests)) {
      return res.status(400).json({ message: 'Body must be a test report with summary and tests.' });
    }
    try {
      const temporary = `${reportFile}.tmp`;
      await writeFile(temporary, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
      await rename(temporary, reportFile);
      const { summary = {} } = report;
      console.log(`[receiver] saved ${reportFile}: commit=${String(report.commit_sha || '').slice(0, 7)} status=${summary.overall_status} passed=${summary.passed}/${summary.total}`);
      return res.json({ message: 'Report saved' });
    } catch (error) { return next(error); }
  });
  app.use((error, _req, res, _next) => {
    if (error instanceof SyntaxError && 'body' in error) return res.status(400).json({ message: 'Body is not valid JSON' });
    console.error(error);
    return res.status(500).json({ message: 'Unable to save report.' });
  });
  return app;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.RECEIVER_PORT || process.env.PORT || 5050);
  const server = createReceiver().listen(port, '0.0.0.0', () => console.log(`[receiver] listening on http://localhost:${port}/report`));
  server.on('error', (error) => { console.error('[receiver] failed to start:', error.message); process.exitCode = 1; });
}
