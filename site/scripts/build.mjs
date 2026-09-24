import { createHash } from 'node:crypto';
import { lstat, mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { bundles, candidates, catalogCandidates, evidenceDate, fits, glossary, plainKinds, roadmap, statuses } from '../src/content.mjs';
import { onboarding, problems, tenantSteps } from '../src/onboarding.mjs';
import { dossiers, researchDate } from '../src/dossiers.mjs';
import { catalogReview, legacyGuidance, pathways, pilotGates, programReviewDate, programSources } from '../src/program.mjs';

export const siteRoot = fileURLToPath(new URL('../', import.meta.url));
const src = new URL('../src/', import.meta.url);
const dist = new URL('../dist/', import.meta.url);
export const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));
export const hash = (text) => `'sha256-${createHash('sha256').update(text, 'utf8').digest('base64')}'`;
const readSource = async (name) => (await readFile(new URL(name, src), 'utf8')).replace(/\r\n?/g, '\n');

// Fail closed rather than copying, publishing or deleting unexpected material.
// Only directory metadata is inspected; unexpected file contents are never read.
export async function assertSafeOutputDirectory(directory) {
  let info;
  try {
    info = await lstat(directory);
  } catch (error) {
    if (error.code === 'ENOENT') return;
    throw error;
  }
  if (!info.isDirectory() || info.isSymbolicLink()) throw new Error('Output must be a real directory, not a link.');
  const allowed = new Set(['index.html', 'staticwebapp.config.json', 'web.config']);
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (!allowed.has(entry.name) || !entry.isFile() || entry.isSymbolicLink()) {
      throw new Error('Unexpected output entry. Build stopped; review dist manually before publishing.');
    }
  }
}

export function renderWebConfig({ globalHeaders, mimeTypes }) {
  const escape = (value) => value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const headers = Object.entries(globalHeaders)
    .map(([name, value]) => `        <add name="${escape(name)}" value="${escape(value)}" />`)
    .join('\n');
  const mimeMaps = Object.entries(mimeTypes)
    .map(([extension, type]) => `        <remove fileExtension="${escape(extension)}" />\n        <mimeMap fileExtension="${escape(extension)}" mimeType="${escape(type)}" />`)
    .join('\n');
  return `<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <defaultDocument>
      <files>
        <clear />
        <add value="index.html" />
      </files>
    </defaultDocument>
    <staticContent>
${mimeMaps}
    </staticContent>
    <httpProtocol>
      <customHeaders>
        <clear />
${headers}
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
`;
}

export function validateContent() {
  if (evidenceDate !== '2026-09-12') throw new Error('Review the fixed evidence date before updating it.');
  if (candidates.length !== 20 || roadmap.length !== 5) throw new Error('Expected exactly 20 candidates and 5 planned workflows.');
  candidates.forEach((item, index) => {
    // Retain historical IDs and gaps when entries leave the public catalog.
    if (!Number.isSafeInteger(item.id) || item.id <= 0 || (index > 0 && item.id <= candidates[index - 1].id)) {
      throw new Error('Candidate IDs must be positive, unique and ordered.');
    }
    if (!bundles[item.bundle] || !statuses[item.status] || !fits[item.fit]) throw new Error(`Invalid classification for candidate ${item.id}`);
    for (const field of ['name', 'alias', 'value', 'summary', 'evidence', 'ptu', 'next']) {
      if (typeof item[field] !== 'string' || !item[field].trim()) throw new Error(`Missing ${field} for candidate ${item.id}`);
    }
    if (!Array.isArray(item.caveats) || !item.caveats.length) throw new Error('Every candidate needs caveats.');
    const guide = onboarding[item.id];
    if (!guide || !guide.problems.length || guide.problems.some((key) => !problems[key])) {
      throw new Error(`Incomplete getting-started guidance for candidate ${item.id}`);
    }
    validateDossier(dossiers[item.id], item.id);
  });
  validateRoadmap();
  validateProgram();
}

const nonempty = (value) => typeof value === 'string' && Boolean(value.trim());
const stringsValid = (values) => Array.isArray(values) && values.length > 0 && values.every(nonempty);
const pairsValid = (values) => Array.isArray(values) && values.length > 0
  && values.every((pair) => Array.isArray(pair) && pair.length === 2 && pair.every(nonempty));
export function validateRoadmap(items = roadmap) {
  const ids = new Set();
  for (const item of items) {
    if (!/^[a-z]+(?:-[a-z]+)*$/.test(item.id) || ids.has(item.id)
      || !bundles[item.bundle]
      || !['title', 'value', 'boundary', 'audience', 'output', 'evaluation', 'gap'].every((key) => nonempty(item[key]))
      || !candidates.some((candidate) => candidate.id === item.related)) {
      throw new Error('Incomplete or invalid use-case idea.');
    }
    ids.add(item.id);
  }
}
export function validateProgram(items = pathways, review = catalogReview) {
  const ids = new Set();
  if (items.length !== 3) throw new Error('Expected three outcome pathways.');
  for (const item of items) {
    if (!bundles[item.id] || ids.has(item.id)
      || !['title', 'lead', 'outcome', 'scope', 'gate', 'boundary', 'extension'].every((key) => nonempty(item[key]))
      || !pairsValid(item.measures) || item.measures.length !== 3
      || !candidates.some((candidate) => candidate.id === item.primary)
      || !Array.isArray(item.extensions) || !item.extensions.length
      || new Set([item.primary, ...item.extensions]).size !== item.extensions.length + 1
      || item.extensions.some((id) => !candidates.some((candidate) => candidate.id === id))) {
      throw new Error('Invalid outcome pathway.');
    }
    ids.add(item.id);
  }
  if (review.length !== 15 || new Set(review.map((item) => item.name)).size !== 15
    || !pairsValid(pilotGates) || !pairsValid(legacyGuidance)) throw new Error('Incomplete catalog selection review.');
  for (const item of review) {
    if (!['name', 'decision', 'reason'].every((key) => nonempty(item[key]))
      || !/^https:\/\/github\.com\/(?:microsoft|Azure-Samples)\/[^/]+\/blob\/[a-f0-9]{40}\/README\.md$/.test(item.url)) {
      throw new Error('Catalog selection needs a pinned public source.');
    }
  }
}
export function validateDossier(dossier, id) {
  const fail = (detail) => { throw new Error(`Invalid dossier ${id}: ${detail}`); };
  if (!dossier || ['name', 'kind', 'alias', 'headline', 'description', 'audience', 'surface', 'workshop']
    .some((key) => !nonempty(dossier[key]))) fail('missing product description');
  if (dossier.privateSource !== undefined && (!nonempty(dossier.privateSource) || dossier.repository)) fail('private source access');
  if (dossier.sourceReview && (dossier.sourceReview.reviewedOn !== programReviewDate
    || !nonempty(dossier.sourceReview.summary))) fail('source review');
  if (!nonempty(plainKinds[dossier.kind])) fail('no plain-language reading of the package kind');
  // A first-time reader gets an explicit answer to what it is, what it does and what it is for.
  const { plain } = dossier;
  if (!plain || ['form', 'what'].some((key) => !nonempty(plain[key]))) fail('plain-language summary');
  if (!plain.brief || !['what', 'does', 'value', 'example'].every((key) => nonempty(plain.brief[key]))) fail('customer explanation');
  const explanationWords = Object.values(plain.brief).join(' ').trim().split(/\s+/).length;
  if (explanationWords < 70 || explanationWords > 150) fail('customer explanation must contain 70–150 words');
  for (const key of ['does', 'benefits', 'chooseIf', 'insteadIf']) {
    if (!stringsValid(plain[key])) fail(`plain-language ${key}`);
  }
  if (plain.what.length < 120) fail('plain-language summary is too thin to judge a fit against');
  if (plain.does.length < 2 || plain.benefits.length < 2) fail('plain-language detail');
  for (const key of ['useCases', 'deliverables', 'boundaries', 'bring', 'acceptance']) {
    if (!stringsValid(dossier[key])) fail(key);
  }
  if (!pairsValid(dossier.workflow) || !pairsValid(dossier.specialists)) fail('workflow or specialist roles');
  const { architecture, ingestion, deployment } = dossier;
  if (!ingestion || !nonempty(ingestion.input) || !nonempty(ingestion.check)
    || !pairsValid(ingestion.stages)) fail('ingestion');
  if (!deployment || !nonempty(deployment.method) || !pairsValid(deployment.steps)
    || !stringsValid(deployment.prerequisites) || !stringsValid(deployment.costs)) fail('deployment');
  if (!architecture || !nonempty(architecture.summary)
    || !['documented', 'proposed', 'unresolved'].includes(architecture.basis)
    || !Array.isArray(architecture.notes) || !architecture.notes.every(nonempty)
    || !Array.isArray(architecture.nodes) || architecture.nodes.length < 2
    || !Array.isArray(architecture.edges) || !architecture.edges.length) fail('architecture');
  const nodeIds = new Set();
  const positions = new Set();
  for (const node of architecture.nodes) {
    if (!/^[a-z][a-z0-9-]*$/.test(node.id) || nodeIds.has(node.id)
      || !['title', 'service', 'detail'].every((key) => nonempty(node[key]))
      || ![node.column, node.row].every((value) => Number.isInteger(value) && value >= 0 && value <= 3)
      || positions.has(`${node.column}:${node.row}`)) fail('component or grid position');
    nodeIds.add(node.id);
    positions.add(`${node.column}:${node.row}`);
  }
  for (const edge of architecture.edges) {
    if (!Array.isArray(edge) || edge.length !== 3 || !nodeIds.has(edge[0])
      || !nodeIds.has(edge[1]) || edge[0] === edge[1] || !nonempty(edge[2])) fail('connection');
  }
  const sourceIds = new Set();
  if (!Array.isArray(dossier.sources) || !dossier.sources.length) fail('sources');
  for (const source of dossier.sources) {
    if (!/^[a-z][a-z0-9-]*$/.test(source.id) || sourceIds.has(source.id) || !nonempty(source.label)) fail('source identity');
    const url = new URL(source.url);
    if (url.protocol !== 'https:' || url.username || url.password
      || !['github.com', 'learn.microsoft.com', 'docs.github.com', 'code.visualstudio.com'].includes(url.hostname)) fail('source URL');
    if (url.hostname === 'github.com' && !/\/(?:blob|tree)\/[a-f0-9]{40}(?:\/|$)/.test(url.pathname)) fail('unpinned source');
    sourceIds.add(source.id);
  }
}

const options = (data) => Object.entries(data).map(([value, label]) => `<option value="${escapeHTML(value)}">${escapeHTML(label)}</option>`).join('');
const list = (values) => `<ul>${values.map((value) => `<li>${escapeHTML(value)}</li>`).join('')}</ul>`;
const external = (url, label, className = '') => `<a${className ? ` class="${className}"` : ''} href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(label)}<span class="sr-only"> (opens in a new tab)</span></a>`;
const renderSteps = (steps) => steps.map(([title, detail]) => `<li><h4>${escapeHTML(title)}</h4><p>${escapeHTML(detail)}</p></li>`).join('');
const problemIcons = {
  engineering: 'm8 6-6 6 6 6m8-12 6 6-6 6M14 3l-4 18',
  answers: 'M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Zm-2 5 6 6M7 8h6m-6 4h4',
  documents: 'M6 2h9l5 5v15H6V2Zm9 0v6h5M10 12h6m-6 4 2 2 4-4',
  drafting: 'm15 4 5 5M4 20l5-1L21 7a2 2 0 0 0-5-5L4 14v6Zm8 1h9',
  service: 'M4 13V10a8 8 0 0 1 16 0v3M4 11H2v7h4v-7H4Zm16 0h2v7h-4v-7h2Zm0 7v2l-5 2h-3',
  data: 'M3 3v18h19M7 16v-5m5 5V6m5 10V9',
};
const renderPathways = () => pathways.map((item) => `<article class="pathway-card" id="pathway-${item.id}" data-primary="${item.primary}" aria-labelledby="pathway-${item.id}-title">
  <p class="eyebrow">${escapeHTML(item.lead)}</p><h3 id="pathway-${item.id}-title">${escapeHTML(item.title)}</h3>
  <p class="pathway-outcome">${escapeHTML(item.outcome)}</p>
  <div class="pathway-brief"><h4>First pilot scope</h4><p>${escapeHTML(item.scope)}</p>
    <h4>Resolve before deployment</h4><p>${escapeHTML(item.gate)}</p>
    <h4>Measure against an agreed baseline</h4><dl class="pilot-measures">${item.measures.map(([label, detail]) => `<div><dt>${escapeHTML(label)}</dt><dd>${escapeHTML(detail)}</dd></div>`).join('')}</dl>
    <p class="pathway-boundary"><strong>Decision boundary:</strong> ${escapeHTML(item.boundary)}</p>
    <h4>Later, only if needed</h4><p>${escapeHTML(item.extension)}</p>
  </div>
  <a class="text-link" href="#solution-${item.primary}">Explore ${escapeHTML(candidates.find((candidate) => candidate.id === item.primary).name)} <span aria-hidden="true">→</span></a>
  <button class="button primary" type="button" data-plan-pathway="${item.id}" aria-describedby="pathway-${item.id}-planning" hidden>Plan ${item.id} pilot</button>
  <p class="pathway-planning" id="pathway-${item.id}-planning">Adds the starting candidate and a pilot brief to your shortlist. Existing selections stay; extensions are not automatically added.</p>
  <details class="pathway-options"><summary>Inspect optional extension guides</summary><ul>${item.extensions.map((id) => `<li><a href="#solution-${id}">${escapeHTML(candidates.find((candidate) => candidate.id === id).name)}</a></li>`).join('')}</ul></details>
</article>`).join('\n');
const wrapLabel = (text, max = 25) => {
  const lines = [''];
  for (const word of text.split(' ')) {
    if (lines.at(-1).length + word.length + 1 > max) lines.push(word);
    else lines[lines.length - 1] += `${lines.at(-1) ? ' ' : ''}${word}`;
  }
  return lines;
};
const renderGraph = (architecture, id) => {
  const minColumn = Math.min(...architecture.nodes.map((node) => node.column));
  const minRow = Math.min(...architecture.nodes.map((node) => node.row));
  const width = (Math.max(...architecture.nodes.map((node) => node.column)) - minColumn + 1) * 290;
  const height = (Math.max(...architecture.nodes.map((node) => node.row)) - minRow + 1) * 200;
  const positions = new Map(architecture.nodes.map((node) => [node.id, {
    x: (node.column - minColumn) * 290 + 30, y: (node.row - minRow) * 200 + 40,
  }]));
  const edges = architecture.edges.map(([from, to], index) => {
    const a = positions.get(from);
    const b = positions.get(to);
    const horizontal = a.x !== b.x;
    const forward = horizontal ? b.x > a.x : b.y > a.y;
    const x1 = a.x + (horizontal ? (forward ? 230 : 0) : 115);
    const y1 = a.y + (horizontal ? 60 : (forward ? 120 : 0));
    const x2 = b.x + (horizontal ? (forward ? 0 : 230) : 115);
    const y2 = b.y + (horizontal ? 60 : (forward ? 0 : 120));
    const adjacent = horizontal ? a.y === b.y && Math.abs(a.x - b.x) === 290
      : Math.abs(a.y - b.y) === 200;
    // Route non-adjacent edges through the gutters, never through another component.
    const lane = 12 + (index % 3) * 6;
    const exit = x1 + (forward ? lane : -lane);
    const entry = x2 + (forward ? -lane : lane);
    const gutterY = b.y > a.y ? a.y + 120 + lane : a.y - lane;
    const gutterX = a.x + 230 + lane;
    const path = adjacent ? `M${x1},${y1} L${x2},${y2}` : horizontal
      ? `M${x1},${y1} H${exit} V${gutterY} H${entry} V${y2} H${x2}`
      : `M${x1},${y1} V${y1 + (forward ? lane : -lane)} H${gutterX} V${y2 + (forward ? -lane : lane)} H${x2} V${y2}`;
    const arrow = horizontal
      ? `${x2},${y2} ${x2 + (forward ? -8 : 8)},${y2 - 5} ${x2 + (forward ? -8 : 8)},${y2 + 5}`
      : `${x2},${y2} ${x2 - 5},${y2 + (forward ? -8 : 8)} ${x2 + 5},${y2 + (forward ? -8 : 8)}`;
    return `<g class="graph-edge"><path d="${path}"/><polygon points="${arrow}"/><title>${index + 1}. ${escapeHTML(architecture.edges[index][2])}</title></g>`;
  }).join('');
  const nodes = architecture.nodes.map((node, index) => {
    const { x, y } = positions.get(node.id);
    return `<g class="graph-node${node.optional ? ' graph-optional' : ''}" transform="translate(${x} ${y})"><rect width="230" height="120" rx="10"/>
      <text x="14" y="23" class="graph-index">${String(index + 1).padStart(2, '0')}${node.optional ? ' / OPTIONAL' : ''}</text>
      <text x="14" y="48" class="graph-title">${wrapLabel(node.title).map((line, i) => `<tspan x="14" dy="${i ? 18 : 0}">${escapeHTML(line)}</tspan>`).join('')}</text>
      <text x="14" y="91" class="graph-service">${wrapLabel(node.service, 29).map((line, i) => `<tspan x="14" dy="${i ? 16 : 0}">${escapeHTML(line)}</tspan>`).join('')}</text></g>`;
  }).join('');
  const caption = { documented: 'Source-informed component architecture', proposed: 'Proposed component architecture', unresolved: 'Qualification steps - runtime architecture unknown' };
  return `<figure class="technical-architecture"><figcaption id="${id}-diagram-title">${caption[architecture.basis]}<span>Arrows show data or control flow. Scroll the diagram on narrow screens, or read the component responsibilities and connections below.</span></figcaption>
    <div class="graph-scroll" role="region" aria-label="Component diagram; scroll horizontally on small screens" tabindex="0"><svg class="component-graph" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="${id}-diagram-title"><desc>${escapeHTML(architecture.summary)}</desc>${edges}${nodes}</svg></div>
    <ol class="component-details">${architecture.nodes.map((node) => `<li><h4>${escapeHTML(node.title)}</h4><p class="component-service">${escapeHTML(node.service)}${node.optional ? ' / optional' : ''}</p><p>${escapeHTML(node.detail)}</p></li>`).join('')}</ol>
    <details class="connection-details"><summary>Read all ${architecture.edges.length} connections</summary><ol class="connection-list">${architecture.edges.map(([from, to, label]) => `<li><strong>${escapeHTML(architecture.nodes.find((node) => node.id === from).title)} <span aria-hidden="true">→</span><span class="sr-only"> to </span> ${escapeHTML(architecture.nodes.find((node) => node.id === to).title)}</strong><p>${escapeHTML(label)}</p></li>`).join('')}</ol></details>
    ${list(architecture.notes)}</figure>`;
};
const renderBrief = (brief, className) => `<dl class="${className}">${[['what', 'What it is'], ['does', 'How it works'], ['value', 'Use it for'], ['example', 'Example scenario']].map(([key, label]) => `<div${key === 'example' ? ' class="summary-example"' : ''}><dt>${label}</dt><dd>${escapeHTML(brief[key])}</dd></div>`).join('')}</dl>`;
const renderSolution = (item) => {
  const dossier = dossiers[item.id];
  const { architecture, ingestion, deployment, plain } = dossier;
  const id = `solution-${item.id}`;
  return `<section class="solution-page section wrap" id="${id}" data-page="solution" data-id="${item.id}" aria-labelledby="${id}-title">
    <a class="text-link solution-back" href="#candidate-title-${item.id}"><span aria-hidden="true">←</span> Back to solutions</a>
    <header class="solution-heading"><div><p class="eyebrow">${escapeHTML(bundles[item.bundle])} / ${escapeHTML(dossier.kind)}</p><h2 id="${id}-title">${escapeHTML(item.name)}</h2><p class="solution-headline">${escapeHTML(dossier.headline)}</p></div>
    <div class="solution-actions"><button class="button primary shortlist-toggle" data-select="${item.id}" type="button" aria-pressed="false" hidden>Add to shortlist</button><a class="text-link" href="#shortlist">View my shortlist <span aria-hidden="true">→</span></a></div></header>
    ${renderBrief(plain.brief, 'solution-summary')}
    <dl class="solution-facts"><div><dt>Who it helps</dt><dd>${escapeHTML(dossier.audience)}</dd></div><div><dt>What you get</dt><dd>${escapeHTML(dossier.deliverables.join(' / '))}</dd></div></dl>
    <nav class="solution-nav" aria-label="${escapeHTML(item.name)} sections"><a href="#${id}-plain">In plain terms</a><a href="#${id}-workflow">Uses &amp; workflow</a><a href="#${id}-architecture">Architecture</a><a href="#${id}-ingestion">Data &amp; ingestion</a><a href="#${id}-setup">Deployment &amp; code access</a><a href="#${id}-specialists">Deployment assistance</a><a href="#${id}-sources">Code &amp; sources</a><a href="#${id}-notes">Evaluation notes</a></nav>
    <div class="solution-body">
      ${dossier.sourceReview ? `<aside class="source-review" aria-labelledby="${id}-review-title"><h3 id="${id}-review-title">Upstream maintenance review</h3><p>Reviewed <time datetime="${dossier.sourceReview.reviewedOn}">${dossier.sourceReview.reviewedOn}</time>. ${escapeHTML(dossier.sourceReview.summary)}</p><a class="text-link" href="#${id}-sources">Read the pinned source references <span aria-hidden="true">→</span></a></aside>` : ''}
      <section class="solution-section" id="${id}-plain" aria-labelledby="${id}-plain-title">
        <div class="solution-section-heading"><div><p class="eyebrow">00 / Never seen this before</p><h3 id="${id}-plain-title">In plain terms.</h3></div><p>${escapeHTML(plain.what)}</p></div>
        <div class="product-surface"><h4>What you actually receive</h4><p>${escapeHTML(plain.form)}</p></div>
        <div class="fit-layout"><div><h4>What it does</h4>${list(plain.does)}</div><div><h4>What you would gain</h4>${list(plain.benefits)}</div></div>
        <div class="pilot-milestone"><strong>How much of that is proven?</strong><p>Those gains describe what this package is built to produce. They are not a claim about what was measured here. What this catalog actually established: ${escapeHTML(item.evidence)}</p><a class="text-link" href="#${id}-notes">Read the evaluation notes <span aria-hidden="true">→</span></a></div>
        <div class="fit-layout"><div><h4>Choose this if</h4>${list(plain.chooseIf)}</div><div><h4>Consider something else if</h4>${list(plain.insteadIf)}</div></div>
      </section>
      <section class="solution-section" id="${id}-workflow" aria-labelledby="${id}-workflow-title">
        <div class="solution-section-heading"><div><p class="eyebrow">01 / Use it for the right job</p><h3 id="${id}-workflow-title">Where it earns its place.</h3></div><p>${escapeHTML(dossier.description)}</p></div>
        <div class="fit-layout"><div><h4>Best uses</h4>${list(dossier.useCases)}</div><div><h4>Know the boundary</h4>${list(dossier.boundaries)}</div></div>
        <div class="product-surface"><h4>${architecture.basis === 'documented' ? 'How people use it' : 'Experience and implementation to confirm'}</h4><p>${escapeHTML(dossier.surface)}</p></div>
        <ol class="workflow-steps">${renderSteps(dossier.workflow)}</ol>
      </section>
      <section class="solution-section" id="${id}-architecture" aria-labelledby="${id}-architecture-title">
        <div class="solution-section-heading"><div><p class="eyebrow">02 / Under the hood</p><h3 id="${id}-architecture-title">Components and how they connect.</h3></div><p>${escapeHTML(architecture.summary)}</p></div>
        ${renderGraph(architecture, id)}
      </section>
      <section class="solution-section" id="${id}-ingestion" aria-labelledby="${id}-ingestion-title">
        <div class="solution-section-heading"><div><p class="eyebrow">03 / Prepare the inputs</p><h3 id="${id}-ingestion-title">From your data to useful output.</h3></div><p>${escapeHTML(ingestion.input)}</p></div>
        <ol class="ingestion-steps">${renderSteps(ingestion.stages)}</ol><p class="pilot-milestone">${escapeHTML(ingestion.check)}</p>
      </section>
      <section class="solution-section" id="${id}-setup" aria-labelledby="${id}-setup-title">
        <div class="solution-section-heading"><div><p class="eyebrow">04 / Make a start</p><h3 id="${id}-setup-title">Your path to a tenant pilot.</h3></div><p>${escapeHTML(deployment.method)}</p></div>
        <div class="setup-layout"><div class="setup-source"><div class="code-access"><h4>Code &amp; access</h4>${dossier.repository ? external(dossier.repository, 'Open public repository (pinned)', 'button primary') : dossier.privateSource ? `<p>${escapeHTML(dossier.privateSource)}</p>` : '<p><strong>Repository not verified for this catalog entry.</strong> Platform documentation or a proposed design is not an installable application.</p>'}<a class="text-link" href="#engagement">Arrange access or deployment help <span aria-hidden="true">→</span></a></div><h4>Before you begin</h4>${list(deployment.prerequisites)}<h4>Budget separately for</h4>${list(deployment.costs)}<p>No deployment commands run from this site.</p></div><ol class="setup-steps">${renderSteps(deployment.steps)}</ol></div>
      </section>
      <section class="solution-section" id="${id}-specialists" aria-labelledby="${id}-specialists-title">
        <div class="solution-section-heading"><div><p class="eyebrow">05 / From selection to adoption</p><h3 id="${id}-specialists-title">Deploy with your team—or with our help.</h3></div><p>We can work with your AI and platform teams from code access and architecture through approved deployment, evaluation, handover and onboarding more teams. Agree scope, delivery roles, funding and support with the program/account team; this is not a support entitlement or promise of free implementation.</p></div>
        <a class="text-link" href="#engagement">See the end-to-end engagement <span aria-hidden="true">→</span></a>
        <ul class="specialist-roles">${renderSteps(dossier.specialists)}</ul>
        <div class="fit-layout"><div><h4>Bring to the session</h4>${list(dossier.bring)}</div><div><h4>Agree how to judge success</h4>${list(dossier.acceptance)}</div></div>
        <div class="pilot-milestone"><strong>First working session</strong><p>${escapeHTML(dossier.workshop)}</p><a class="text-link" href="#preparation">Shared preparation checklist <span aria-hidden="true">→</span></a></div>
      </section>
      <section class="solution-section" id="${id}-sources" aria-labelledby="${id}-sources-title">
        <div class="solution-section-heading"><div><p class="eyebrow">06 / Inspect the basis</p><h3 id="${id}-sources-title">Code, guides and references.</h3></div><p>Public source review: ${researchDate}. Documentation and code inspection are not functional testing or deployment certification.</p></div>
        <ul class="dossier-sources">${dossier.sources.map((source) => `<li>${external(source.url, source.label)}${source.supports ? `<p>${escapeHTML(source.supports)}</p>` : ''}<p class="source-path">${escapeHTML(source.url)}</p></li>`).join('')}</ul>
        ${dossier.revision ? `<p class="source-note">Pinned revision <code>${escapeHTML(dossier.revision)}</code>. Public upstream starting point, not the tested private adaptation. Review its license and operating requirements.</p>` : '<p class="source-note">Platform references explain the integration or design option only; they do not verify a portfolio-specific package.</p>'}
      </section>
      <details class="deployment-notes" id="${id}-notes"><summary>Deployment notes &amp; implementation considerations</summary>
        <div><h3>Package and integration</h3><p>${escapeHTML(item.next)}</p><h3>Evaluation context</h3><p>${escapeHTML(item.evidence)}</p>
        <ul>${item.caveats.map((text) => `<li>${escapeHTML(text)}</li>`).join('')}</ul><h3>Model capacity and cost</h3><p>${escapeHTML(item.ptu)}</p>
        <p>A reference design is not a deployment certification. Confirm licensing, supported components, identity, network design and operations ownership for your tenant.</p></div>
      </details>
    </div>
  </section>`;
};

const renderCard = (item) => `<article class="candidate" data-id="${item.id}" data-bundle="${item.bundle}" data-problems="${onboarding[item.id].problems.join(' ')}" aria-labelledby="candidate-title-${item.id}">
  <div class="candidate-top"><span class="candidate-area">${escapeHTML(bundles[item.bundle])}</span><span class="candidate-area candidate-kind">${escapeHTML(plainKinds[dossiers[item.id].kind])}</span></div>
  <h3 id="candidate-title-${item.id}">${escapeHTML(item.name)}</h3>
  <p class="candidate-alias">${escapeHTML(dossiers[item.id].alias)}</p>
  ${renderBrief(dossiers[item.id].plain.brief, 'candidate-value solution-summary')}
  <div class="candidate-taxonomy"><p>${escapeHTML(dossiers[item.id].audience)}</p></div>
  <a class="detail-button" href="#solution-${item.id}" aria-label="Explore and get started: ${escapeHTML(item.name)}">Explore &amp; get started <span aria-hidden="true">→</span></a>
</article>`;

const renderRoadmap = (item) => `<li class="roadmap-item" id="idea-${item.id}" aria-labelledby="idea-${item.id}-title">
  <div><span class="roadmap-tag">Concept · Not built or deployed</span><h3 id="idea-${item.id}-title">${escapeHTML(item.title)}</h3><p class="roadmap-bundle">${escapeHTML(item.audience)}</p></div>
  <div class="roadmap-explanation"><p>${escapeHTML(item.value)}</p>
    <dl class="idea-output"><dt>What your team would receive</dt><dd>${escapeHTML(item.output)}</dd></dl>
    <p class="roadmap-boundary"><strong>Human decision:</strong> ${escapeHTML(item.boundary)}</p>
    <details class="idea-detail"><summary>How to explore this idea</summary><div>
      <h4>Start small and measure</h4><p>${escapeHTML(item.evaluation)}</p>
      <h4>Related starting point to assess</h4><a href="#solution-${item.related}">${escapeHTML(candidates.find((candidate) => candidate.id === item.related).name)}</a><p>${escapeHTML(item.gap)}</p>
      <a class="text-link" href="#idea-discussion">Prepare a use-case discussion <span aria-hidden="true">→</span></a>
    </div></details>
  </div>
</li>`;

export async function buildSite() {
  await assertSafeOutputDirectory(dist);
  validateContent();
  const [template, theme, css, app] = await Promise.all(['index.html', 'theme.js', 'styles.css', 'app.js'].map(readSource));
  const sharedCSP = [
    "default-src 'none'",
    `script-src ${hash(theme)} ${hash(app)}`,
    "script-src-attr 'none'",
    `style-src ${hash(css)}`,
    "style-src-attr 'none'",
    "img-src 'none'",
    "font-src 'none'",
    "connect-src 'none'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'none'",
  ].join('; ');
  const replacements = {
    META_CSP: escapeHTML(sharedCSP),
    THEME: theme,
    CSS: css,
    APP: app,
    CANDIDATE_COUNT: candidates.length,
    BUNDLE_OPTIONS: options(bundles),
    PROBLEM_OPTIONS: options(problems),
    PROBLEM_LINKS: Object.entries(problems).map(([key, label]) => `<a class="problem-link" href="#catalog" data-problem-link="${key}"><svg class="problem-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${problemIcons[key]}"/></svg><span>${escapeHTML(label)}</span><span class="problem-arrow" aria-hidden="true">→</span></a>`).join('\n'),
    TENANT_STEPS: tenantSteps.map((step) => `<li>${escapeHTML(step)}</li>`).join(''),
    GLOSSARY: glossary.map(([term, meaning]) => `<div><dt>${escapeHTML(term)}</dt><dd>${escapeHTML(meaning)}</dd></div>`).join(''),
    PATHWAYS: renderPathways(),
    PILOT_GATES: renderSteps(pilotGates),
    PROGRAM_REVIEW_DATE: programReviewDate,
    CATALOG_REVIEW: catalogReview.map((item) => `<tr><th scope="row">${external(item.url, item.name)}</th><td>${escapeHTML(item.decision)}</td><td>${escapeHTML(item.reason)}</td></tr>`).join(''),
    PROGRAM_SOURCES: programSources.map(({ url, label }) => external(url, label, 'text-link')).join(' '),
    LEGACY_GUIDANCE: renderSteps(legacyGuidance),
    CARDS: catalogCandidates.map(renderCard).join('\n'),
    SOLUTIONS: catalogCandidates.map(renderSolution).join('\n'),
    ROADMAP: roadmap.map(renderRoadmap).join('\n'),
  };
  const html = template.replace(/@@([A-Z_]+)@@/g, (_, key) => {
    if (!(key in replacements)) throw new Error(`Unknown template token: ${key}`);
    return replacements[key];
  });
  if (/@@[A-Z_]+@@/.test(html)) throw new Error('Unresolved template token.');
  const config = {
    globalHeaders: {
      'Content-Security-Policy': `${sharedCSP}; frame-ancestors 'none'`,
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer',
      'X-Frame-Options': 'DENY',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=()',
      'Strict-Transport-Security': 'max-age=31536000',
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Resource-Policy': 'same-origin',
      'Cache-Control': 'no-cache',
    },
    mimeTypes: { '.html': 'text/html' },
  };
  const webConfig = renderWebConfig(config);
  await mkdir(dist, { recursive: true });
  await Promise.all([
    writeFile(new URL('index.html', dist), html, 'utf8'),
    writeFile(new URL('staticwebapp.config.json', dist), `${JSON.stringify(config, null, 2)}\n`, 'utf8'),
    writeFile(new URL('web.config', dist), webConfig, 'utf8'),
  ]);
  return { bytes: Buffer.byteLength(html), html, config, webConfig };
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  const result = await buildSite();
  console.log(`Built dist/index.html (${result.bytes.toLocaleString('en-US')} bytes), dist/staticwebapp.config.json and dist/web.config.`);
  console.log(`${candidates.length} candidates · ${roadmap.length} planned workflows · 2 script hashes · 1 style hash · no runtime dependencies`);
}
