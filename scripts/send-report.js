import { readFile, writeFile } from 'node:fs/promises';

const reportPath = process.env.REPORT_FILE || 'test-report.json';
const report = JSON.parse(await readFile(reportPath, 'utf8'));
console.log(JSON.stringify(report.summary));

const url = process.env.RECEIVER_URL;
if (!url) {
  console.log('RECEIVER_URL is not set; report is available as an Actions artifact only.');
  process.exit(0);
}

const headers = {
  'content-type': 'application/json',
  'ngrok-skip-browser-warning': 'true',
};
if (process.env.REPORT_TOKEN) headers['x-report-token'] = process.env.REPORT_TOKEN;

let lastError;
for (let attempt = 1; attempt <= 3; attempt += 1) {
  try {
    const response = await fetch(url, { method: 'POST', headers, body: JSON.stringify(report), signal: AbortSignal.timeout(20_000) });
    const body = await response.text();
    if (!response.ok) throw new Error(`Receiver returned ${response.status}: ${body}`);
    console.log(`Receiver replied: ${response.status} ${body}`);
    process.exit(0);
  } catch (error) {
    lastError = error;
    console.error(`Attempt ${attempt} failed: ${error.message}`);
    if (attempt < 3) await new Promise((resolve) => setTimeout(resolve, 3000));
  }
}
await writeFile('report-delivery-error.txt', `${lastError?.stack || lastError}\n`);
process.exitCode = 1;
