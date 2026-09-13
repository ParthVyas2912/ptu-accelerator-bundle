import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { assertSafeOutputDirectory, buildSite, escapeHTML, hash } from '../scripts/build.mjs';
import { candidates, roadmap, statuses } from '../src/content.mjs';
import { assertPublicContent, assertServedPolicy, deployedURL } from './public-contract.mjs';
import { resolveSmokeTarget } from './smoke-options.mjs';

const { html, config, bytes } = await buildSite();
const policy = config.globalHeaders['Content-Security-Policy'];

test('CI manifest and lockfile agree, use public package URLs and require no production dependencies', async () => {
  const [manifest, lock] = await Promise.all(['package.json', 'package-lock.json'].map(async (name) =>
    JSON.parse(await readFile(new URL(`../${name}`, import.meta.url), 'utf8'))));
  assert.equal(manifest.engines.node, '>=22');
  assert.equal(lock.lockfileVersion, 3);
  assert.equal(lock.name, manifest.name);
  assert.equal(lock.version, manifest.version);
  assert.deepEqual(lock.packages[''].devDependencies, manifest.devDependencies);
  assert.deepEqual(lock.packages[''].engines, manifest.engines);
  assert.equal(Object.keys(manifest.dependencies || {}).length, 0);
  for (const [path, entry] of Object.entries(lock.packages)) {
    if (!path) continue;
    assert.equal(entry.dev, true, `${path} must remain development-only`);
    assert.equal(new URL(entry.resolved).origin, 'https://registry.npmjs.org');
    assert.ok(entry.integrity, `Missing package integrity for ${path}`);
  }
  for (const [name, version] of Object.entries(manifest.devDependencies)) {
    assert.match(version, /^\d+\.\d+\.\d+$/);
    assert.equal(lock.packages[`node_modules/${name}`].version, version);
  }
  assert.equal(manifest.scripts.test, 'node --test tests/build.test.mjs');
  assert.equal(manifest.scripts.build, 'node scripts/build.mjs');
  for (const hook of ['preinstall', 'install', 'postinstall', 'prepare']) assert.equal(manifest.scripts[hook], undefined);
});

test('build is deterministic, self-contained and comfortably within the size budget', async () => {
  const second = await buildSite();
  assert.equal(second.html, html);
  assert.deepEqual(second.config, config);
  assert.ok(bytes < 175 * 1024, `HTML is ${bytes} bytes`);
  assert.deepEqual((await readdir(new URL('../dist/', import.meta.url))).sort(), ['index.html', 'staticwebapp.config.json']);
  assert.doesNotMatch(html, /@@[A-Z_]+@@/);
  assert.doesNotMatch(html, /<(?:script|img|iframe|audio|video)\b[^>]*\bsrc\s*=/i);
  assert.doesNotMatch(html, /<link\b/i);
  assert.doesNotMatch(html, /@import\b|url\s*\(/i);
  assert.equal(Object.hasOwn(config, 'navigationFallback'), false);
  assert.equal(Object.hasOwn(config, 'responseOverrides'), false);
});

test('output guard rejects unexpected files and directories without reading or copying them', async () => {
  await mkdir(new URL('../test-results/', import.meta.url), { recursive: true });
  const fixture = await mkdtemp(new URL('../test-results/output-guard-', import.meta.url));
  try {
    await assertSafeOutputDirectory(fixture);
    await writeFile(join(fixture, 'index.html'), 'synthetic public fixture');
    await assertSafeOutputDirectory(fixture);
    await writeFile(join(fixture, 'not-for-publication.txt'), 'synthetic guard fixture');
    await assert.rejects(assertSafeOutputDirectory(fixture), /Unexpected output entry/);
    await rm(join(fixture, 'not-for-publication.txt'));
    await mkdir(join(fixture, 'reports'));
    await assert.rejects(assertSafeOutputDirectory(fixture), /Unexpected output entry/);
  } finally {
    await rm(fixture, { recursive: true, force: true });
  }
});

test('smoke URL/env selection supports deployment and rejects unsafe or ambiguous targets', () => {
  assert.deepEqual(resolveSmokeTarget([], ''), { help: false, url: null });
  assert.equal(resolveSmokeTarget([], deployedURL).url, new URL(deployedURL).origin);
  assert.equal(resolveSmokeTarget(['--url', deployedURL], 'https://unused.example/').url, new URL(deployedURL).origin);
  assert.equal(resolveSmokeTarget([`--url=${deployedURL}`]).url, new URL(deployedURL).origin);
  assert.equal(resolveSmokeTarget(['--local'], deployedURL).url, null);
  assert.equal(resolveSmokeTarget(['--url', 'http://127.0.0.1:4173/']).url, 'http://127.0.0.1:4173');
  assert.equal(resolveSmokeTarget(['--help']).help, true);
  for (const args of [
    ['--url'], ['--url='], ['--unknown'], ['--url', 'file:///index.html'],
    ['--url', 'http://example.test/'], ['--url', 'https://user:secret@example.test/'],
    ['--url', 'https://example.test/?token=not-a-real-token'], ['--url', 'https://example.test/source/'],
  ]) assert.throws(() => resolveSmokeTarget(args));
});

test('all 20 candidates and five planned workflows are rendered, complete and uniquely identified', () => {
  assert.equal((html.match(/class="candidate status-/g) || []).length, 20);
  assert.equal((html.match(/class="roadmap-item"/g) || []).length, 5);
  assert.deepEqual(candidates.map((item) => item.id), Array.from({ length: 20 }, (_, index) => index + 1));
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(ids.length, new Set(ids).size);
  for (const item of candidates) {
    assert.ok(html.includes(escapeHTML(item.name)));
    assert.ok(html.includes(escapeHTML(item.summary)));
    assert.ok(html.includes(escapeHTML(item.ptu)));
    assert.ok(html.includes(escapeHTML(item.next)));
    assert.ok(item.caveats.length >= 2);
  }
  for (const item of roadmap) assert.ok(html.includes(escapeHTML(item.boundary)));
  assert.equal(roadmap[0].priority, 'Highest priority');
  for (const label of Object.values(statuses)) assert.ok(html.includes(escapeHTML(label)));
});

test('HTTP and meta CSP hash every actual inline script and style with no unsafe execution', () => {
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
  const styles = [...html.matchAll(/<style>([\s\S]*?)<\/style>/g)].map((match) => match[1]);
  assert.equal(scripts.length, 2);
  assert.equal(styles.length, 1);
  for (const block of [...scripts, ...styles]) assert.ok(policy.includes(hash(block)));
  assert.equal((policy.match(/'sha256-/g) || []).length, 3);
  assert.doesNotMatch(policy, /unsafe-inline|unsafe-eval|\*/);
  for (const directive of ["connect-src 'none'", "frame-ancestors 'none'", "base-uri 'none'", "form-action 'none'"]) {
    assert.ok(policy.includes(directive));
  }
  const meta = html.match(/http-equiv="Content-Security-Policy" content="([^"]+)"/)?.[1];
  assert.equal(meta, escapeHTML(policy.replace("; frame-ancestors 'none'", '')));
  assert.doesNotMatch(html, /<[^>]+\s(?:on[a-z]+|style)\s*=/i);
  for (const script of scripts) {
    assert.doesNotMatch(script, /\b(?:eval|Function|fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts)\s*\(/);
    assert.doesNotMatch(script, /\.innerHTML\b|\.outerHTML\b|insertAdjacentHTML|document\.write\b/);
  }
  assert.equal(config.globalHeaders['X-Content-Type-Options'], 'nosniff');
  assert.equal(config.globalHeaders['X-Frame-Options'], 'DENY');
  assert.equal(config.globalHeaders['Referrer-Policy'], 'no-referrer');
});

test('generated public files contain no identifiable infrastructure, contacts, raw artifacts or local paths', () => {
  assertPublicContent(`${html}\n${JSON.stringify(config)}`);
  assertPublicContent(`${html}\n<a href="${deployedURL}">Public website</a>`);
  for (const marker of ['rg-synthetic-fixture', 'accountId: synthetic', 'resourceGroupName: synthetic']) {
    assert.throws(() => assertPublicContent(`${html}\n${marker}`), /Public privacy check failed/);
  }
});

test('delivered-content checks validate HTTP hashes without relying on local deployment files', () => {
  const headers = Object.fromEntries(Object.entries(config.globalHeaders).map(([key, value]) => [key.toLowerCase(), value]));
  assertServedPolicy(html, headers);
  assert.throws(() => assertServedPolicy(html.replace('const param =', 'const unexpectedChange ='), headers), /exact delivered content/);
  assert.throws(() => assertServedPolicy(html, {}), /exact delivered content/);
});

test('required evidence boundaries survive rendering', () => {
  const checks = [
    [1, /adapted local/], [2, /final combined response failed/], [3, /not retested/],
    [4, /limited corpus/], [5, /all GitHub Copilot features/], [6, /filter warning/],
    [7, /grounded-answer requirement/], [8, /semantic defects/], [9, /full behavioral equivalence/],
    [10, /existing inventory only/], [11, /not categorically excluded/], [12, /not implemented/],
    [13, /marketing content/], [14, /not a standalone/], [15, /Copilot Studio/],
    [16, /Custom model endpoints are possible/], [17, /telemetry does not imply/],
    [18, /do not ship/], [19, /one safety block/], [20, /Owner and package unknown/],
  ];
  for (const [id, pattern] of checks) assert.match(JSON.stringify(candidates[id - 1]), pattern);
  assert.match(candidates[10].ptu, /documented BYOM route can use compatible PTU/);
  assert.match(candidates[7].ptu, /Batch/);
  for (const phrase of [
    'Guided demonstrations only', 'not a sixth new app', 'Standard', 'Batch',
    'No automatic redaction or release', 'No autonomous high-impact changes',
    'not a business-drafting workflow', '2026-09-12', 'not an official product',
  ]) assert.ok(html.includes(phrase), `Missing business boundary: ${phrase}`);
});

test('theme uses the exact base variables, correct font, only token colors and explicit light handling', async () => {
  const css = await readFile(new URL('../src/styles.css', import.meta.url), 'utf8');
  const theme = await readFile(new URL('../src/theme.js', import.meta.url), 'utf8');
  const componentCSS = css.slice(css.indexOf('* { box-sizing'));
  assert.doesNotMatch(componentCSS, /#[0-9a-f]{3,8}\b|\brgba?\s*\(|\bhsla?\s*\(/i);
  assert.doesNotMatch(componentCSS, /(?:color|background|stroke|fill)\s*:\s*(?:white|black|red|blue|transparent|currentColor)\b/i);
  assert.match(css, /"Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif/);
  assert.match(css, /Consolas, "Courier New", Courier, monospace/);
  assert.match(css, /--cp-bg: #f7f4ef;/);
  assert.match(css, /--cp-bg: #3d3b3a;/);
  assert.match(css, /--cp-accent: #b11f4b;/);
  assert.match(css, /--cp-accent: #fd8ea1;/);
  assert.match(theme, /param \|\| \(window\.matchMedia/);
  assert.match(theme, /param === "light" \|\| param === "dark"/);
  assert.match(css, /prefers-reduced-motion: reduce/);
  assert.match(css, /@media print/);
});

test('escaping protects curated values and all internal anchor targets exist', () => {
  assert.equal(escapeHTML('<img src=x onerror="bad()"> & \''), '&lt;img src=x onerror=&quot;bad()&quot;&gt; &amp; &#39;');
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]));
  for (const [, target] of html.matchAll(/\bhref="#([^"]+)"/g)) assert.ok(ids.has(target), `Missing anchor: ${target}`);
  assert.match(html, /<html lang="en">/);
  assert.equal((html.match(/<h1\b/g) || []).length, 1);
});

test('four progressive views retain native anchors and do not hide content before JavaScript runs', () => {
  assert.deepEqual([...html.matchAll(/data-view-link="([^"]+)"/g)].map((match) => match[1]),
    ['overview', 'catalog', 'guide', 'roadmap']);
  const sections = [...html.matchAll(/<(?:section|div)\b[^>]*\bdata-page="([^"]+)"[^>]*>/g)];
  assert.equal(sections.length, 9);
  assert.deepEqual([...new Set(sections.map((match) => match[1]))].sort(), ['catalog', 'guide', 'overview', 'roadmap']);
  for (const [tag] of sections) assert.doesNotMatch(tag, /\bhidden\b/);
  assert.match(html, /id="bundle-chips"[^>]*role="group"[^>]*hidden/);
  assert.match(html, /id="view-switch"[^>]*role="group"[^>]*hidden/);
  assert.match(html, /data-layout="grid" aria-pressed="true"/);
  assert.match(html, /data-layout="list" aria-pressed="false"/);
});
