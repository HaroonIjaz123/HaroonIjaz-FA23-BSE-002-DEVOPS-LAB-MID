import test from 'node:test';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import { mkdtemp, rm } from 'node:fs/promises';
import { loadSubmissions, saveSubmission } from '../server.js';
import { isValidUrl, validateSubmission } from '../src/validation.js';
import { buildReport } from '../scripts/build-report.js';

const valid = {
  name: 'Haroon Ijaz', reg_no: 'FA23-BSE-002', title: 'Lab Assignment 2',
  url: 'https://github.com/haroon/lab2',
};

async function withDataFile(run) {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'submission-portal-'));
  const file = path.join(directory, 'submissions.json');
  try { await run(file); }
  finally { await rm(directory, { recursive: true, force: true }); }
}

test('valid submission is saved', async () => withDataFile(async (file) => {
  assert.deepEqual(validateSubmission(valid), []);
  await saveSubmission(file, valid);
  assert.deepEqual(await loadSubmissions(file), [valid]);
}));

test('missing registration number is rejected and not saved', async () => withDataFile(async (file) => {
  const errors = validateSubmission({ ...valid, reg_no: '' });
  assert.ok(errors.includes('Registration number is required.'));
  assert.deepEqual(await loadSubmissions(file), []);
}));

test('invalid URL is rejected and not saved', async () => withDataFile(async (file) => {
  const errors = validateSubmission({ ...valid, url: 'not-a-valid-url' });
  assert.ok(errors.includes('Submission URL is not a valid http(s) URL.'));
  assert.deepEqual(await loadSubmissions(file), []);
}));

test('valid URLs are accepted and bad URLs are rejected', () => {
  assert.equal(isValidUrl('https://example.com/path'), true);
  for (const url of ['ftp://example.com/file', 'https:///missing-host', 'https://example.com/a b', '']) {
    assert.equal(isValidUrl(url), false, url);
  }
});

test('CI report builder keeps individual pass, fail, and skipped test results', () => {
  const output = [
    '✔ accepts a valid submission (2.1ms)',
    '✖ rejects malformed URLs (1.2ms)',
    '﹣ skips optional integration check (0.2ms)',
    'ℹ tests 3', 'ℹ pass 1', 'ℹ fail 1', 'ℹ skipped 1',
  ].join('\n');
  const report = buildReport(output, { GITHUB_REPOSITORY: 'owner/repo', GITHUB_SHA: 'abc123' });
  assert.deepEqual(report.tests.map(({ name, result }) => [name, result]), [
    ['accepts a valid submission', 'passed'],
    ['rejects malformed URLs', 'failed'],
    ['skips optional integration check', 'skipped'],
  ]);
  assert.deepEqual(report.summary, { total: 3, passed: 1, failed: 1, skipped: 1, overall_status: 'FAILED' });
  assert.equal(report.repository, 'owner/repo');
});