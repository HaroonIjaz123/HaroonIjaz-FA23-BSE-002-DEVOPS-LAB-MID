import { readFile } from 'node:fs/promises';
import nodemailer from 'nodemailer';

const user = process.env.SMTP_USERNAME || '';
const password = process.env.SMTP_PASSWORD || '';
const recipient = process.env.EMAIL_TO || 'harooonijaz123@gmail.com';
if (!(user && password && recipient)) {
  console.log('SMTP_USERNAME / SMTP_PASSWORD / EMAIL_TO not set; email skipped.');
  process.exit(0);
}

const report = JSON.parse(await readFile(process.env.REPORT_FILE || 'test-report.json', 'utf8'));
const summary = report.summary;
const lines = [
  `Repository : ${report.repository}`,
  `Branch     : ${report.branch}`,
  `Commit     : ${report.commit_sha}`,
  `Run ID     : ${report.run_id}`,
  `Result     : ${summary.overall_status}`,
  `Total/Passed/Failed : ${summary.total}/${summary.passed}/${summary.failed}`,
  '',
  ...report.tests.map((item) => `- ${item.name}: ${item.result}${item.failure_message ? ` (${item.failure_message.slice(0, 200)})` : ''}`),
];
const port = Number(process.env.SMTP_PORT || 465);
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST || 'smtp.gmail.com',
  port,
  secure: port === 465,
  auth: { user, pass: password },
  connectionTimeout: 30_000,
  greetingTimeout: 30_000,
  socketTimeout: 30_000,
});
await transporter.sendMail({
  from: user,
  to: recipient,
  subject: `[CI ${summary.overall_status}] ${report.repository} @ ${report.commit_sha.slice(0, 7)} (${summary.passed}/${summary.total} passed)`,
  text: lines.join('\n'),
  attachments: [{ filename: 'test-report.json', content: JSON.stringify(report, null, 2), contentType: 'application/json' }],
});
console.log(`Report emailed to ${recipient}`);
