import express from 'express';
import { readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateSubmission } from './src/validation.js';

const here = path.dirname(fileURLToPath(import.meta.url));
export const dataFile = process.env.SUBMISSIONS_FILE || path.join(here, 'submissions.json');

export async function loadSubmissions(file = dataFile) {
  try {
    return JSON.parse(await readFile(file, 'utf8'));
  } catch (error) {
    if (error.code === 'ENOENT') return [];
    throw error;
  }
}

export async function saveSubmission(file, record) {
  const submissions = await loadSubmissions(file);
  submissions.push(record);
  await writeFile(file, `${JSON.stringify(submissions, null, 2)}\n`, 'utf8');
  return submissions;
}

export function createApp(file = dataFile) {
  const app = express();
  app.use(express.json());
  const builtSite = path.join(here, 'dist');
  if (existsSync(builtSite)) app.use(express.static(builtSite));

  app.get('/api/submissions', async (_req, res, next) => {
    try { res.json(await loadSubmissions(file)); } catch (error) { next(error); }
  });

  app.post('/api/submissions', async (req, res, next) => {
    const errors = validateSubmission(req.body ?? {});
    if (errors.length) return res.status(400).json({ errors });

    try {
      const record = Object.fromEntries(['name', 'reg_no', 'title', 'url']
        .map((field) => [field, req.body[field].trim()]));
      const submissions = await saveSubmission(file, record);
      return res.status(201).json({ submission: record, submissions });
    } catch (error) { return next(error); }
  });

  app.use((error, _req, res, _next) => {
    console.error(error);
    res.status(500).json({ error: 'Unable to process the request.' });
  });
  return app;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 5000);
  const server = createApp().listen(port, () => console.log(`Portal listening on http://localhost:${port}`));
  server.on('error', (error) => { console.error('Portal failed to start:', error.message); process.exitCode = 1; });
}
