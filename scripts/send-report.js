import { readFile, writeFile } from 'node:fs/promises';

const reportPath = process.env.REPORT_FILE || 'test-report.json';
const report = JSON.parse(await readFile(reportPath, 'utf8'));
console.log(JSON.stringify(report.summary));

if (!Array.isArray(report.tests) || report.tests.length === 0 || !report.summary || report.summary.total < 1) {
  console.error('The report has no test results. Run `npm test > test-output.txt` and `npm run build-report` first.');
  process.exit(1);
}

const url = process.env.RECEIVER_URL;
if (!url) {
  console.log('RECEIVER_URL is not set; report is available as an Actions artifact only.');
  process.exit(0);
}
try {
  if (!new URL(url).pathname.endsWith('/report')) throw new Error('RECEIVER_URL must end in /report.');
} catch (error) {
  console.error(`Invalid RECEIVER_URL: ${error.message}`);
  process.exit(1);
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
    if (/Receiver returned (400|401|403|404):/.test(error.message)) {
      if (error.message.includes('ERR_NGROK_3200') || error.message.includes('endpoint') && error.message.includes('offline')) {
        console.error('ngrok is offline. Start the receiver with `npm run receiver`, start `ngrok http 5050`, then update RECEIVER_URL to the current HTTPS URL ending in /report.');
      } else if (error.message.includes('404')) {
        console.error('Check that RECEIVER_URL uses the current ngrok HTTPS address and ends in /report.');
      }
      break;
    }
    if (attempt < 3) await new Promise((resolve) => setTimeout(resolve, 3000));
  }
}
await writeFile('report-delivery-error.txt', `${lastError?.stack || lastError}\n`);
process.exitCode = 1;
