import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { assertSafeOutputDirectory, brandAssets, buildSite, escapeHTML, hash, sourceLabel, validateDossier, validateProgram, validateRoadmap } from '../scripts/build.mjs';
import { candidates, catalogCandidates, glossary, plainKinds, roadmap } from '../src/content.mjs';
import { onboarding, problems, sources, tenantSteps } from '../src/onboarding.mjs';
import { dossiers } from '../src/dossiers.mjs';
import { solutionVisuals, visualIcons } from '../src/visuals.mjs';
import { catalogReview, legacyGuidance, pathways, pilotGates, programReviewDate, programSources } from '../src/program.mjs';
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
  assert.ok(bytes < 800 * 1024, `HTML with 20 illustrated dossiers and embedded approved logos is ${bytes} bytes`);
  assert.deepEqual((await readdir(new URL('../dist/', import.meta.url))).sort(), ['index.html', 'staticwebapp.config.json', 'web.config']);
  assert.doesNotMatch(html, /@@[A-Z_]+@@/);
  assert.doesNotMatch(html, /<(?:script|iframe|audio|video)\b[^>]*\bsrc\s*=/i);
  assert.equal((html.match(/<img\b/g) || []).length, 5);
  assert.equal((html.match(/src="data:image\/png;base64,[A-Za-z0-9+/=]+"/g) || []).length, 5);
  assert.doesNotMatch(html, /<link\b/i);
  assert.doesNotMatch(html, /@import\b|url\s*\(/i);
  assert.equal(Object.hasOwn(config, 'navigationFallback'), false);
  assert.equal(Object.hasOwn(config, 'responseOverrides'), false);
});

test('only reviewed Microsoft logo derivatives are embedded with meaningful alternatives', async () => {
  for (const asset of Object.values(brandAssets)) {
    const png = await readFile(new URL(`../src/assets/${asset.file}`, import.meta.url));
    assert.equal(png.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
    assert.ok(png.length < 32 * 1024);
    assert.ok(html.includes(`data:image/png;base64,${png.toString('base64')}`));
  }
  assert.ok(policy.includes('img-src data:'));
  assert.equal((html.match(/alt="Microsoft"/g) || []).length, 4);
  assert.equal((html.match(/alt="Microsoft Azure"/g) || []).length, 1);
  assert.throws(() => assertPublicContent(`${html}<img src="data:image/png;base64,bm90LWFuLWFzc2V0" alt="Unreviewed">`), /unreviewed image/);
  assert.throws(() => assertPublicContent(`${html}<img src="https://example.com/logo.png" alt="External">`), /embedded PNG/);
});

test('the IIS configuration mirrors the static-host headers so both published links serve one policy', async () => {
  const webConfig = await readFile(new URL('../dist/web.config', import.meta.url), 'utf8');
  for (const [name, value] of Object.entries(config.globalHeaders)) {
    const escaped = value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    assert.ok(webConfig.includes(`<add name="${name}" value="${escaped}" />`), `web.config is missing ${name}`);
  }
  assert.match(webConfig, /<add value="index\.html" \/>/);
});

test('guided discovery and the planning workspace preserve catalog identities and accessible controls', () => {
  const header = html.match(/<header\b[\s\S]*?<\/header>/)[0];
  assert.match(header, /class="header-microsoft brand-attribution"/);
  assert.equal((header.match(/alt="Microsoft"/g) || []).length, 2);
  assert.match(header, /id="header-plan-count"/);
  assert.match(html, /class="adoption-map"/);
  assert.match(html, /Your organization<\/h3>/);
  assert.match(html, /Your AI toolkit<\/h3>/);
  assert.match(html, /Success you can measure<\/h3>/);
  assert.match(html, /id="finder-results"[^>]*hidden[^>]*aria-labelledby="finder-title"/);
  assert.match(html, /Matched by documented use case, not ranked by readiness/);
  for (const item of catalogCandidates) {
    assert.equal((html.match(new RegExp(`data-quick-select="${item.id}"`, 'g')) || []).length, 1);
  }
  assert.doesNotMatch(html, /data-compare|id="comparison|dock-compare|renderComparison|data-spotlight/);
  assert.match(html, /id="selection-status"[^>]*role="status"/);
  assert.equal((html.match(/class="solution-reader"/g) || []).length, catalogCandidates.length);
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

test('all 20 candidates and five planned workflows are rendered with stable historical IDs', () => {
  assert.equal((html.match(/class="candidate"/g) || []).length, 20);
  assert.equal((html.match(/class="roadmap-item"/g) || []).length, 5);
  assert.deepEqual(candidates.map((item) => item.id),
    Array.from({ length: 22 }, (_, index) => index + 1).filter((id) => ![18, 20].includes(id)));
  const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(ids.length, new Set(ids).size);
  for (const item of candidates) {
    assert.ok(html.includes(escapeHTML(item.name)));
    assert.ok(html.includes(escapeHTML(item.evidence)));
    assert.ok(html.includes(escapeHTML(item.ptu)));
    assert.ok(html.includes(escapeHTML(item.next)));
    assert.ok(item.caveats.length >= 2);
  }
  for (const item of roadmap) assert.ok(html.includes(escapeHTML(item.boundary)));
  assert.ok(roadmap.every((item) => !Object.hasOwn(item, 'priority')));
  assert.doesNotMatch(html, /class="status-badge"|id="status-filter"|Selected tests verified|Not launch-ready/);
  assert.deepEqual([...html.matchAll(/class="candidate" data-id="(\d+)"/g)].map((match) => Number(match[1])),
    catalogCandidates.map((item) => item.id));
  assert.equal(catalogCandidates[0].bundle, 'engineering');
});

test('retired candidates are absent from the artifact and all customer-facing counts agree', () => {
  assert.doesNotMatch(html, /Harbinger|StepFly|(?:solution|candidate-title)-(?:18|20)(?:["-])/i);
  assert.doesNotMatch(html, /\b22(?:-candidate|\s+(?:AI starting points|starting points|candidates|ready apps|solutions))|\ball 22\b/);
  assert.match(html, /class="nav-count">20<\/span>/);
  assert.match(html, /Showing 20 of 20 solutions/);
  assert.match(html, /Explore 20 AI starting points/);
  for (const id of [18, 20]) {
    assert.equal(dossiers[id], undefined);
    assert.equal(onboarding[id], undefined);
  }
  assert.equal(sources.stepfly, undefined);
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
  assert.throws(() => assertPublicContent(`${html}<a href="https://unreviewed.example/">Unreviewed</a>`), /unapproved link/);
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
    [19, /one safety block/],
    [21, /no deployment, call or model request was performed/i],
    [22, /intentionally deploys insecure servers/],
  ];
  for (const [id, pattern] of checks) assert.match(JSON.stringify(candidates.find((item) => item.id === id)), pattern);
  assert.match(candidates.find((item) => item.id === 11).ptu, /documented BYOM route can use compatible PTU/);
  assert.match(candidates.find((item) => item.id === 21).ptu, /not interchangeable with text capacity/);
  assert.match(candidates.find((item) => item.id === 8).ptu, /Batch/);
  for (const phrase of [
    'not a sixth new app', 'Standard', 'Batch',
    'No automatic redaction or release', 'No autonomous high-impact changes',
    'marketing content', '2026-09-12', 'not an official product',
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
  assert.match(css, /--cp-action: var\(--cp-accent\);/);
  assert.match(css, /--cp-action-hover: var\(--cp-accent-hover\);/);
  assert.match(css, /--cp-action-fg: var\(--cp-accent-fg\);/);
  assert.match(css, /--cp-action-soft: var\(--cp-surface-soft\);/);
  assert.match(css, /a:hover \{ color: var\(--cp-action\); text-decoration-thickness: 2px; \}/);
  assert.match(css, /\.hero h1 span \{ color: var\(--cp-accent\); \}/);
  assert.doesNotMatch(css, /\.hero-actions \.primary(?:\:hover)? \{/);
  assert.match(theme, /param \|\| \(window\.matchMedia/);
  assert.match(theme, /param === "light" \|\| param === "dark"/);
  assert.match(css, /prefers-reduced-motion: reduce/);
  assert.match(css, /@media print/);
});

test('escaping protects curated values and all internal anchor targets exist', () => {
  assert.equal(escapeHTML('<img src=x onerror="bad()"> & \''), '&lt;img src=x onerror=&quot;bad()&quot;&gt; &amp; &#39;');
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]));
  for (const [, target] of html.matchAll(/\bhref="#([^"]+)"/g)) assert.ok(ids.has(target), `Missing anchor: ${target}`);
  assert.match(html, /<html lang="en">/);
  assert.equal((html.match(/<h1\b/g) || []).length, 1);
});

test('visual overview preserves planning boundaries without the long pilot and orientation sections', () => {
  assert.match(html, /<figure class="workflow-showcase" aria-labelledby="showcase-title">/);
  assert.equal((html.match(/class="showcase-tile /g) || []).length, 3);
  assert.match(html, /An adoption journey, not a system architecture/);
  assert.equal((html.match(/<details class="bundle-inventory">/g) || []).length, 3);
  assert.match(html, /Results depend on fit and delivery/);
  assert.match(html, /Search, storage, hosting, document processing and speech can cost extra/);
  assert.match(html, /Verify model, API &amp; geography compatibility/);
  assert.match(html, /A development path, not a delivery schedule or completion status/);
  assert.match(html, /A reference design is not a deployment certification/);
  assert.match(html, /class="section wrap pilot-section" data-page="guide"/);
  assert.match(html, /<details class="reference-disclosure" id="program">/);
  assert.doesNotMatch(html, /class="map-layer|What these 22 things|What they are not/);
  const orientation = html.match(/<section[^>]+id="orientation"[\s\S]*?<\/section>/)?.[0];
  const words = orientation.replace(/<[^>]*>/g, ' ').trim().split(/\s+/);
  assert.ok(words.length <= 40, `Keep the orientation brief, not another essay: ${words.length} words`);
  assert.equal((html.match(/class="problem-icon"/g) || []).length, Object.keys(problems).length);
  assert.doesNotMatch(html, /d="undefined"/);
});

test('PTU adoption leads the toolkit without promising universal compatibility or deployment readiness', () => {
  const hero = html.match(/<section[^>]+id="top"[\s\S]*?<\/section>/)?.[0];
  assert.match(hero, /Your PTUs/);
  assert.match(hero, /20 AI starting points/);
  assert.match(hero, /Considering PTUs/);
  assert.match(hero, /Prove demand before investing/);
  assert.match(hero, /Choose your mix/);
  assert.match(html, /Each guide identifies its source, requirements and limits/);
  assert.match(hero, /Compatible workloads only/);
  assert.match(hero, /Other services cost extra/);
  assert.match(html, /PTU utilization &amp; headroom/);
  assert.match(html, /time saved, quality and total service cost against an agreed baseline/);
  assert.match(html, /not a guaranteed saving/);
  assert.match(html, /not deployable applications/);
  for (const name of ['Engineering Modernization', 'Knowledge & Staff Work', 'Procurement & Document Operations']) {
    assert.ok(html.includes(`<h3>${escapeHTML(name)}</h3>`));
  }
  assert.equal((html.match(/class="bundle-tagline"/g) || []).length, 3);
  assert.match(html, /class="adoption-band"[\s\S]*?href="#pilot-gates"/);
});

test('every solution answers what it is, what it does and what it is for, in plain language', () => {
  const jargon = /\b(?:RAG|MACAE|CWYD|DKM|BYOK|BYOM|azd|Bicep|FastAPI|Blazor|KQL|OBO|STAC|AKS)\b/;
  for (const item of candidates) {
    const { plain, kind } = dossiers[item.id];
    assert.deepEqual(Object.keys(plain.brief), ['what', 'does', 'value', 'example']);
    const words = Object.values(plain.brief).join(' ').trim().split(/\s+/).length;
    assert.ok(words >= 70 && words <= 150);
    const card = html.match(new RegExp(`<article class="candidate" data-id="${item.id}"[\\s\\S]*?</article>`))?.[0];
    const solution = html.match(new RegExp(`<section[^>]+id="solution-${item.id}"[\\s\\S]*?<div class="solution-body">`))?.[0];
    assert.ok(card && solution, `${item.id}: missing card or solution introduction`);
    assert.ok(card.includes(escapeHTML(item.value)));
    assert.ok(card.includes(escapeHTML(solutionVisuals[item.id].audience)));
    for (const label of ['What it is', 'How it works', 'Use it for', 'Example scenario']) assert.ok(solution.includes(`<dt>${label}</dt>`));
    for (const value of Object.values(plain.brief)) assert.ok(solution.includes(escapeHTML(value)));
    // The reader is told what would actually arrive before anything else.
    assert.ok(html.includes(escapeHTML(plain.form)), `${item.id}: form`);
    assert.ok(html.includes(escapeHTML(plain.what)), `${item.id}: what`);
    for (const key of ['does', 'benefits', 'chooseIf', 'insteadIf']) {
      for (const line of plain[key]) assert.ok(html.includes(escapeHTML(line)), `${item.id}: ${key}`);
    }
    // Plain language is the point: unexplained shorthand defeats it.
    assert.doesNotMatch(plain.what, jargon, `${item.id}: unexplained shorthand in the plain summary`);
    assert.doesNotMatch(plain.does.join(' '), jargon, `${item.id}: unexplained shorthand in what it does`);
    // A benefit never stands alone; the evidence for that candidate sits beside it.
    assert.ok(html.includes(escapeHTML(item.evidence)), `${item.id}: evidence`);
    assert.ok(html.includes(escapeHTML(plainKinds[kind])), `${item.id}: plain kind`);
  }
  assert.equal((html.match(/How much of that is proven\?/g) || []).length, candidates.length);
  assert.equal((html.match(/id="solution-\d+-plain"/g) || []).length, candidates.length);
  assert.equal((html.match(/class="candidate-area candidate-kind"/g) || []).length, candidates.length);
});

test('visual gallery keeps cards concise and illustrates every solution without external assets', () => {
  assert.deepEqual(Object.keys(solutionVisuals).map(Number), candidates.map((item) => item.id));
  assert.equal((html.match(/class="solution-visual visual-compact"/g) || []).length, 20);
  assert.equal((html.match(/class="solution-visual"/g) || []).length, 20);
  for (const item of candidates) {
    const visual = solutionVisuals[item.id];
    assert.equal(visual.stages.length, 3);
    for (const [icon, label] of visual.stages) {
      assert.ok(visualIcons[icon]);
      assert.ok(html.includes(escapeHTML(label)));
    }
    const card = html.match(new RegExp(`<article class="candidate" data-id="${item.id}"[\\s\\S]*?</article>`))[0];
    const words = card.replace(/<[^>]*>/g, ' ').trim().split(/\s+/).length;
    assert.ok(words <= 95, `Card ${item.id} is too long: ${words} words`);
    const oldExplanation = Object.values(dossiers[item.id].plain.brief).join(' ').split(/\s+/).length;
    const newExplanation = `${item.value} ${visual.audience}`.split(/\s+/).length;
    assert.ok(newExplanation <= oldExplanation / 2, `Card ${item.id}: reduce explanation prose by at least half`);
    assert.match(card, /Illustrative/);
    assert.doesNotMatch(card, /Example scenario|<pre/);
  }
  assert.match(html, /class="command-disclosure"/);
  assert.match(html, /class="workflow-steps delivery-journey"/);
  assert.match(html, /Intended workflow, not a product screenshot or a verified result/);
});

test('customer engagement and code access distinguish assistance from approval or verification', () => {
  assert.match(html, /id="engagement" data-page="guide"/);
  for (const phrase of ['Discover &amp; choose', 'Prepare &amp; get access', 'Deploy &amp; make it work',
    'Hand over &amp; expand', 'central AI teams', 'support responsibilities are agreed before work starts']) {
    assert.ok(html.includes(phrase), phrase);
  }
  assert.match(html, /class="adoption-service"[^>]*>[\s\S]*?href="#engagement"/);
  assert.ok((html.match(/href="#engagement"/g) || []).length >= candidates.length * 2 + 2);
  assert.match(dossiers[3].privateSource, /private.*repository access or an approved code handoff.*owner approval/s);
  assert.ok(html.includes(escapeHTML(dossiers[3].privateSource)));
  assert.equal(dossiers[3].repository, undefined);
  for (const id of [11, 12]) assert.equal(dossiers[id].privateSource, undefined);
  assert.match(dossiers[12].plain.brief.what, /proposed/i);
});

test('How we help leads with delivery choices and a separate shortlist implementation brief', () => {
  assert.match(html, /data-view-link="guide">How we help<\/a>/);
  const introduction = html.match(/<section[^>]+id="capacity"[\s\S]*?<\/section>/)[0];
  assert.match(introduction, /Choose your solutions/);
  assert.match(introduction, /Deploy with your team/);
  assert.match(introduction, /Plan the work with us/);
  assert.doesNotMatch(introduction, /TENANT_STEPS|capacity-choice|tenant-checklist/);
  assert.match(html, /id="print-brief" hidden/);
  assert.match(html, /id="implementation-items"/);
  assert.match(html, /No information is submitted/);
  assert.match(html, /<details class="reference-disclosure" id="preparation">/);
  assert.match(html, /<details class="reference-disclosure" id="selection-review">/);
  assert.match(html, /<details id="capacity-new"><summary>/);
  assert.doesNotMatch(html, /name="capacity"|id="capacity-announcement"/);
});

test('use-case ideas explain customer fit without implying a release commitment or deployable product', () => {
  validateRoadmap();
  const section = html.match(/<section[^>]+id="roadmap"[\s\S]*?<\/section>/)[0];
  assert.match(html, /data-view-link="roadmap">Use-case ideas<\/a>/);
  assert.match(section, /not promised releases/);
  assert.match(section, /No delivery dates, funding or implementation commitments/);
  assert.match(section, /Concepts are not added to the solution shortlist/);
  assert.doesNotMatch(section, /Highest priority|Coming next|data-select|data-plan-pathway|voice-note/);
  assert.equal((section.match(/Concept · Not built or deployed/g) || []).length, 5);
  for (const item of roadmap) {
    for (const key of ['audience', 'output', 'evaluation', 'gap', 'boundary']) {
      assert.ok(section.includes(escapeHTML(item[key])), `${item.id}: missing ${key}`);
    }
    assert.ok(section.includes(`id="idea-${item.id}"`));
    assert.ok(section.includes(`href="#solution-${item.related}"`));
    const copy = structuredClone(roadmap);
    delete copy[0].output;
    assert.throws(() => validateRoadmap(copy), /use-case idea/);
  }
  for (const mutate of [
    (items) => { items[0].related = 999; },
    (items) => { items[1].id = items[0].id; },
    (items) => { items[0].id = 'invalid id'; },
  ]) {
    const copy = structuredClone(roadmap);
    mutate(copy);
    assert.throws(() => validateRoadmap(copy), /use-case idea/);
  }
});

test('a first-time reader is oriented and every unavoidable term is explained', () => {
  assert.match(html, /id="orientation"/);
  assert.match(html, /Microsoft source. Your deployment plan/);
  assert.match(html, /Microsoft-owned code is not a production or support guarantee/);
  assert.match(html, /<details class="reference-disclosure" id="glossary">/);
  for (const [term, meaning] of glossary) {
    assert.ok(html.includes(`<dt>${escapeHTML(term)}</dt>`), `glossary term: ${term}`);
    assert.ok(html.includes(escapeHTML(meaning)), `glossary meaning: ${term}`);
  }
  assert.ok(glossary.length >= 12, 'too few terms to orient a newcomer');
  // Defining a term with the same shorthand it is meant to unpack helps nobody.
  for (const [term, meaning] of glossary) assert.doesNotMatch(meaning, /\bRAG\b|\bIaC\b|\bLLM\b/, term);
  // Every package kind must have a plain reading, or a card would show a blank tag.
  for (const dossier of Object.values(dossiers)) assert.ok(plainKinds[dossier.kind], dossier.kind);
});

test('problem-first hub supplies a complete, honest getting-started path for every candidate', () => {
  assert.match(html, /<title>AI Solutions Hub/);
  assert.doesNotMatch(html, /PTU portfolio|PTU guide/);
  assert.equal((html.match(/data-problem-link="/g) || []).length, Object.keys(problems).length);
  assert.deepEqual(Object.keys(onboarding).map(Number), candidates.map((item) => item.id));
  assert.equal((html.match(/class="technical-architecture"/g) || []).length, 20);
  assert.equal((html.match(/class="component-graph"/g) || []).length, 20);
  assert.doesNotMatch(html, /<dialog\b|app-preview|preview-sidebar|Concept preview|Illustrative grid/);
  assert.deepEqual(Object.keys(dossiers).map(Number), candidates.map((item) => item.id));
  for (const item of candidates) {
    const guide = onboarding[item.id];
    const dossier = dossiers[item.id];
    for (const field of ['audience', 'headline', 'description', 'surface', 'workshop']) {
      assert.ok(html.includes(escapeHTML(dossier[field])), `${item.id}: ${field}`);
    }
    for (const node of dossier.architecture.nodes) {
      assert.ok(html.includes(escapeHTML(node.detail)));
      assert.ok(html.includes(escapeHTML(node.service)));
    }
    for (const steps of [dossier.workflow, dossier.ingestion.stages, dossier.deployment.walkthrough.steps, dossier.specialists]) {
      for (const [title, detail] of steps) {
        assert.ok(html.includes(escapeHTML(title)));
        assert.ok(html.includes(escapeHTML(detail)));
      }
    }
    for (const source of dossier.sources) assert.ok(html.includes(escapeHTML(source.url)));
    for (const problem of guide.problems) assert.ok(problems[problem]);
  }
  for (const source of Object.values(sources)) {
    assert.match(source.revision, /^[a-f0-9]{40}$/);
    assert.match(source.repository, /^https:\/\/github\.com\/(?:microsoft|Azure-Samples)\/[^/]+\/tree\/[a-f0-9]{40}$/);
    assert.equal(source.guide, source.repository.replace('/tree/', '/blob/') + '/README.md');
    // Some pinned inventory references are comparison sources, not the catalog product.
  }
  for (const step of tenantSteps) assert.ok(html.includes(escapeHTML(step)));
  assert.match(html, /Repository not verified/);
  assert.match(html, /not the tested private adaptation/);
  assert.match(html, /class="button primary shortlist-toggle"/);
  assert.match(html, /not a support entitlement or promise of free implementation/);
  assert.match(html, /Selections stay in this page until reload/);
  const sourceLinks = [...html.matchAll(/<a\b([^>]*\btarget="_blank"[^>]*)>([\s\S]*?)<\/a>/g)];
  assert.equal(sourceLinks.length, Object.values(dossiers).reduce((count, item) =>
    count + item.sources.length + (item.repository ? 1 : 0) + (item.deployment.walkthrough.source ? 1 : 0), 0) + catalogReview.length + programSources.length);
  for (const [, attributes, label] of sourceLinks) {
    assert.match(attributes, /rel="noopener noreferrer"/);
    assert.match(label, /opens in a new tab/);
  }
});

test('dossiers reject invalid sources, broken graph relationships and incomplete product guidance', () => {
  const invalid = (mutate, pattern) => {
    const copy = structuredClone(dossiers[1]);
    mutate(copy);
    assert.throws(() => validateDossier(copy, 1), pattern);
  };
  invalid((copy) => { copy.architecture.edges[0][1] = 'missing'; }, /connection/);
  invalid((copy) => { copy.architecture.nodes[1].id = copy.architecture.nodes[0].id; }, /component/);
  invalid((copy) => { copy.architecture.nodes[0].column = 8; }, /grid/);
  invalid((copy) => { copy.sources[0].url = 'https://github.com/microsoft/example/blob/main/README.md'; }, /unpinned/);
  invalid((copy) => { copy.sources[0].url = 'https://unreviewed.example/'; }, /source URL/);
  invalid((copy) => { copy.sources.push(copy.sources[0]); }, /source identity/);
  invalid((copy) => { copy.specialists = []; }, /specialist/);
  invalid((copy) => { copy.ingestion.stages = [['Missing detail']]; }, /ingestion/);
  invalid((copy) => { copy.deployment.prerequisites = []; }, /deployment/);
  invalid((copy) => { delete copy.deployment.walkthrough; }, /deployment walkthrough/);
  invalid((copy) => { copy.deployment.walkthrough.source = 'missing'; }, /deployment walkthrough/);
  invalid((copy) => { copy.deployment.walkthrough.steps[0].push(''); }, /deployment walkthrough/);
  invalid((copy) => { delete copy.plain.brief; }, /customer explanation/);
  invalid((copy) => { copy.plain.brief.value = ''; }, /customer explanation/);
  invalid((copy) => { copy.plain.brief.value = 'Word '.repeat(151); }, /customer explanation/);
  invalid((copy) => { copy.privateSource = ''; }, /private source access/);
  invalid((copy) => { copy.privateSource = 'Private code cannot also be a public repository.'; }, /private source access/);
  const signatures = Object.values(dossiers).map((item) =>
    JSON.stringify([item.workflow, item.architecture.nodes.map((node) => node.service)]));
  assert.equal(new Set(signatures).size, 20, 'Product-specific workflows and components must not be reused as generic filler');
  for (const id of [3, 12]) {
    assert.notEqual(dossiers[id].architecture.basis, 'documented');
    assert.equal(dossiers[id].repository, undefined);
  }
});

test('all 20 deployment walkthroughs expose ordered instructions, source basis and acceptance without invented installs', () => {
  assert.equal((html.match(/class="deployment-walkthrough"/g) || []).length, 20);
  assert.equal((html.match(/Open full deployment manual/g) || []).length, 18);
  for (const item of candidates) {
    const dossier = dossiers[item.id];
    const guide = dossier.deployment.walkthrough;
    assert.equal(guide.steps.length, 5);
    assert.ok(html.includes(escapeHTML(guide.route)));
    assert.ok(html.includes(escapeHTML(guide.verify)));
    for (const [, , command] of guide.steps) {
      if (command) assert.ok(html.includes(`<code>${escapeHTML(command)}</code>`));
    }
    if ([3, 12].includes(item.id)) {
      assert.equal(guide.source, null);
      assert.ok(guide.steps.every((step) => step.length === 2));
    } else assert.ok(dossier.sources.some((source) => source.id === guide.source));
    if (dossier.repository) assert.ok(html.includes(`git checkout --detach ${dossier.revision}`));
  }
  assert.match(dossiers[1].deployment.walkthrough.steps[3][2], /acr_build_push_update[\s\S]+post_deployment_setup/);
  assert.match(dossiers[13].deployment.walkthrough.steps[2][2], /build_and_deploy_images[\s\S]+process_sample_data/);
  assert.match(dossiers[6].deployment.walkthrough.steps[2][1], /no post-provision hook/);
  assert.match(dossiers[8].deployment.walkthrough.steps[1][1], /automatically builds images/);
  assert.match(dossiers[12].deployment.walkthrough.steps[2][1], /different pins/);
  for (const id of [4, 9, 14]) assert.match(dossiers[id].deployment.walkthrough.route, /maintenance gate/);
  assert.match(html, /source-inspected, not deployment-tested/);
  for (const marker of [
    'AZURE_TENANT_ID 11111111-2222-3333-4444-555555555555',
    'AZURE_CLIENT_ID ghp_notarealcredential',
    'AUTH_CLIENT_ID accountId: synthetic',
  ]) assert.throws(() => assertPublicContent(`${html}\n${marker}`), /Public privacy check failed/);
});

test('customer decisions expose provenance, prerequisites and a solution-specific handoff for all 20 entries', () => {
  assert.equal(Object.values(dossiers).filter((dossier) => sourceLabel(dossier) === 'Microsoft-owned public repository').length, 16);
  assert.equal(sourceLabel(dossiers[3]), 'Private owner-led solution');
  assert.equal(sourceLabel(dossiers[12]), 'Proposed custom workflow');
  for (const id of [5, 11]) assert.equal(sourceLabel(dossiers[id]), 'Microsoft / GitHub platform guidance');
  assert.throws(() => sourceLabel({ repository: 'https://github.com/other/example/tree/revision' }), /source ownership/);
  for (const item of candidates) {
    assert.ok(html.includes(`data-discuss="${item.id}"`));
    assert.ok(html.includes(`class="deployment-runbook" id="solution-${item.id}-runbook"`));
    assert.ok(html.includes(`class="solution-section fit-detail" id="solution-${item.id}-plain"`));
  }
  assert.equal((html.match(/1 \/ Understand the solution/g) || []).length, 20);
  assert.equal((html.match(/2 \/ Run it in your environment/g) || []).length, 20);
  assert.equal((html.match(/class="setup-prerequisites"/g) || []).length, 20);
  assert.equal((html.match(/class="setup-costs"/g) || []).length, 20);
  assert.equal((html.match(/class="setup-input"/g) || []).length, 20);
  assert.doesNotMatch(html, /class="source-path"/);
  assert.match(html, /adoption champion and a review date/);
  assert.match(html, /data classification and residency/);
});

test('component diagrams route every connection outside unrelated component boxes', () => {
  const graphs = [...html.matchAll(/<svg class="component-graph"[\s\S]*?<\/svg>/g)].map(([svg]) => svg);
  assert.equal(graphs.length, 20);
  for (const svg of graphs) {
    const boxes = [...svg.matchAll(/class="graph-node[^"]*" transform="translate\((\d+) (\d+)\)"/g)]
      .map(([, x, y]) => ({ left: Number(x), top: Number(y), right: Number(x) + 230, bottom: Number(y) + 120 }));
    for (const [, path] of svg.matchAll(/<path d="([^"]+)"/g)) {
      let point;
      for (const [, command, values] of path.matchAll(/([MLHV])([\d.,-]+)/g)) {
        const coordinates = values.split(',').map(Number);
        const next = command === 'H' ? [coordinates[0], point[1]]
          : command === 'V' ? [point[0], coordinates[0]] : coordinates;
        if (point) {
          assert.ok(point[0] === next[0] || point[1] === next[1], 'Connections must be orthogonal');
          for (const box of boxes) {
            const crosses = point[0] === next[0]
              ? point[0] > box.left && point[0] < box.right
                && Math.max(point[1], next[1]) > box.top && Math.min(point[1], next[1]) < box.bottom
              : point[1] > box.top && point[1] < box.bottom
                && Math.max(point[0], next[0]) > box.left && Math.min(point[0], next[0]) < box.right;
            assert.equal(crosses, false, `Connection crosses a component: ${path}`);
          }
        }
        point = next;
      }
    }
  }
});

test('four main views and 20 solution pages retain native anchors without JavaScript', () => {
  assert.deepEqual([...html.matchAll(/data-view-link="([^"]+)"/g)].map((match) => match[1]),
    ['overview', 'catalog', 'guide', 'roadmap']);
  const sections = [...html.matchAll(/<(?:section|div)\b[^>]*\bdata-page="([^"]+)"[^>]*>/g)];
  assert.equal(sections.length, 33);
  assert.deepEqual([...new Set(sections.map((match) => match[1]))].sort(), ['catalog', 'guide', 'overview', 'roadmap', 'solution']);
  for (const [tag] of sections) assert.doesNotMatch(tag, /\bhidden\b/);
  assert.match(html, /id="bundle-chips"[^>]*role="group"[^>]*hidden/);
  assert.match(html, /id="view-switch"[^>]*role="group"[^>]*hidden/);
  assert.match(html, /data-layout="grid" aria-pressed="true"/);
  assert.match(html, /data-layout="list" aria-pressed="false"/);
});

test('focused pathways retain gates, measurable outcomes and distinct optional extensions', () => {
  assert.deepEqual(pathways.map(({ id, primary }) => [id, primary]), [
    ['engineering', 9], ['knowledge', 1], ['procurement', 6],
  ]);
  assert.equal((html.match(/class="pathway-card"/g) || []).length, 3);
  for (const item of pathways) {
    assert.match(html, new RegExp(`data-plan-pathway="${item.id}"[^>]*hidden`));
    for (const field of ['scope', 'gate', 'boundary', 'extension']) assert.ok(html.includes(escapeHTML(item[field])));
    for (const [label, measure] of item.measures) {
      assert.ok(html.includes(`<dt>${escapeHTML(label)}</dt>`));
      assert.ok(html.includes(escapeHTML(measure)));
    }
  }
  for (const [, detail] of [...pilotGates, ...legacyGuidance]) assert.ok(html.includes(escapeHTML(detail)));
  assert.match(html, /extensions are not automatically added/);
  assert.match(html, /not completed milestones/);
  assert.match(html, /Standard model deployments/);
  assert.match(html, /Evidence|evidence/);
  const badPrimary = structuredClone(pathways);
  badPrimary[0].primary = 99;
  assert.throws(() => validateProgram(badPrimary), /Invalid outcome/);
  const duplicate = structuredClone(pathways);
  duplicate[1].id = duplicate[0].id;
  assert.throws(() => validateProgram(duplicate), /Invalid outcome/);
  const duplicateExtension = structuredClone(pathways);
  duplicateExtension[0].extensions.push(duplicateExtension[0].primary);
  assert.throws(() => validateProgram(duplicateExtension), /Invalid outcome/);
  const noMeasures = structuredClone(pathways);
  noMeasures[0].measures = [];
  assert.throws(() => validateProgram(noMeasures), /Invalid outcome/);
});

test('catalog assessment is pinned, complete and separate from historical functional evidence', () => {
  assert.equal(programReviewDate, '2026-09-20');
  assert.equal(catalogReview.length, 15);
  assert.equal(catalogReview.filter(({ reason }) => reason.includes('no longer maintained')).length, 5);
  for (const { name, url, reason } of catalogReview) {
    assert.ok(html.includes(escapeHTML(name)));
    assert.ok(html.includes(escapeHTML(url)));
    assert.ok(html.includes(escapeHTML(reason)));
  }
  assert.match(html, /not 54 distinct/);
  assert.match(html, /not newly validated additions/);
  assert.match(html, /datetime="2026-09-12"/);
  const unpinned = structuredClone(catalogReview);
  unpinned[0].url = unpinned[0].url.replace(/[a-f0-9]{40}/, 'main');
  assert.throws(() => validateProgram(pathways, unpinned), /pinned public source/);
  assert.throws(() => validateProgram(pathways, catalogReview.slice(1)), /Incomplete catalog/);
});

test('maintenance notices are prominent and travel with printable solution bodies', () => {
  for (const id of [4, 9, 14]) {
    assert.equal(dossiers[id].sourceReview.reviewedOn, programReviewDate);
    assert.match(dossiers[id].sourceReview.summary, /no longer maintained/i);
    const section = html.split(`id="solution-${id}"`)[1].split('<details class="deployment-notes"')[0];
    assert.match(section, /class="solution-body">\s*<aside class="source-review"/);
    assert.ok(section.includes(escapeHTML(dossiers[id].sourceReview.summary)));
    assert.ok(dossiers[id].sources.some(({ url }) => catalogReview.some((item) => item.url === url)));
  }
  const invalid = structuredClone(dossiers[4]);
  invalid.sourceReview.summary = '';
  assert.throws(() => validateDossier(invalid, 4), /source review/);
  assert.equal(candidates.find((item) => item.id === 4).status, 'verified');
  assert.equal(candidates.find((item) => item.id === 9).status, 'verified');
  assert.equal(candidates.find((item) => item.id === 6).status, 'limited');
  assert.equal(candidates.find((item) => item.id === 12).status, 'planned');
});
