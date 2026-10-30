import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export function buildReport(output, metadata = process.env) {
  const clean = output.replace(/\u001b\[[0-9;]*m/g, '');
  const tests = [];
  for (const line of clean.split(/\r?\n/)) {
    const match = line.match(/^[✔✖﹣]\s+(.+?)(?:\s+\(([\d.]+)ms\))?$/u);
    if (!match) continue;
    const result = line.startsWith('✔') ? 'passed' : line.startsWith('✖') ? 'failed' : 'skipped';
    tests.push({
      name: match[1], result,
      failure_message: result === 'failed' ? 'See the test job log for details.' : null,
    });
  }

  if (!tests.length) {
    const failCount = Number(clean.match(/^ℹ fail (\d+)$/m)?.[1] || 0);
    tests.push({
      name: 'test runner', result: 'failed',
      failure_message: failCount ? 'See the test job log for details.' : 'No individual test results were found in test-output.txt.',
    });
  }
  const passed = tests.filter((item) => item.result === 'passed').length;
  const failed = tests.filter((item) => item.result === 'failed').length;
  const skipped = tests.filter((item) => item.result === 'skipped').length;
  return {
    repository: metadata.GITHUB_REPOSITORY || 'local/repo',
    branch: metadata.GITHUB_REF_NAME || 'local',
    commit_sha: metadata.GITHUB_SHA || 'local',
    run_id: metadata.GITHUB_RUN_ID || 'local',
    timestamp: new Date().toISOString(),
    summary: { total: tests.length, passed, failed, skipped, overall_status: failed === 0 && passed > 0 ? 'PASSED' : 'FAILED' },
    tests,
  };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  let output = '';
  try { output = await readFile(process.env.TEST_OUTPUT || 'test-output.txt', 'utf8'); }
  catch { output = ''; }
  const report = buildReport(output);
  await writeFile(process.env.REPORT_FILE || 'test-report.json', `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify(report.summary));
}
