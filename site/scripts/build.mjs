import { createHash } from 'node:crypto';
import { lstat, mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { bundles, candidates, evidenceDate, fits, roadmap, statuses } from '../src/content.mjs';

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
  const allowed = new Set(['index.html', 'staticwebapp.config.json']);
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (!allowed.has(entry.name) || !entry.isFile() || entry.isSymbolicLink()) {
      throw new Error('Unexpected output entry. Build stopped; review dist manually before publishing.');
    }
  }
}

export function validateContent() {
  if (evidenceDate !== '2026-09-12') throw new Error('Review the fixed evidence date before updating it.');
  if (candidates.length !== 20 || roadmap.length !== 5) throw new Error('Expected exactly 20 candidates and 5 planned workflows.');
  candidates.forEach((item, index) => {
    if (item.id !== index + 1) throw new Error('Candidate IDs must be ordered, unique and complete.');
    if (!bundles[item.bundle] || !statuses[item.status] || !fits[item.fit]) throw new Error(`Invalid classification for candidate ${item.id}`);
    for (const field of ['name', 'alias', 'value', 'summary', 'evidence', 'ptu', 'next']) {
      if (typeof item[field] !== 'string' || !item[field].trim()) throw new Error(`Missing ${field} for candidate ${item.id}`);
    }
    if (!Array.isArray(item.caveats) || !item.caveats.length) throw new Error('Every candidate needs caveats.');
  });
  roadmap.forEach((item) => {
    if (!bundles[item.bundle] || !item.title || !item.value || !item.boundary) throw new Error('Incomplete roadmap item.');
  });
}

const options = (data) => Object.entries(data).map(([value, label]) => `<option value="${escapeHTML(value)}">${escapeHTML(label)}</option>`).join('');
const details = (item) => `<div class="detail-body">
  <p class="detail-value">${escapeHTML(item.value)}</p>
  <p class="detail-meta">${escapeHTML(bundles[item.bundle])} · ${escapeHTML(statuses[item.status])}</p>
  <h3>What was established</h3><p>${escapeHTML(item.evidence)}</p>
  <h3>Important limits</h3><ul>${item.caveats.map((text) => `<li>${escapeHTML(text)}</li>`).join('')}</ul>
  <h3>PTU fit: ${escapeHTML(fits[item.fit])}</h3><p>${escapeHTML(item.ptu)}</p>
  <h3>The next responsible step</h3><p>${escapeHTML(item.next)}</p>
</div>`;

const renderCard = (item) => `<article class="candidate status-${item.status}" data-id="${item.id}" data-bundle="${item.bundle}" data-status="${item.status}" aria-labelledby="candidate-title-${item.id}">
  <div class="candidate-top"><span class="candidate-index" aria-label="Candidate ${item.id}">${String(item.id).padStart(2, '0')}</span><span class="status-badge">${escapeHTML(statuses[item.status])}</span></div>
  <h3 id="candidate-title-${item.id}">${escapeHTML(item.name)}</h3>
  <p class="candidate-alias">${escapeHTML(item.alias)}</p>
  <p class="candidate-value">${escapeHTML(item.value)}</p>
  <p class="candidate-summary">${escapeHTML(item.summary)}</p>
  <div class="candidate-taxonomy"><p>${escapeHTML(bundles[item.bundle])}</p><p><strong>PTU fit</strong> / ${escapeHTML(fits[item.fit])}</p></div>
  <details class="candidate-fallback"><summary>Evidence &amp; next step</summary>${details(item)}</details>
  <p class="print-only"><strong>Next:</strong> ${escapeHTML(item.next)}</p>
</article>`;

const renderRoadmap = (item, index) => `<li class="roadmap-item">
  <span class="roadmap-index" aria-hidden="true">${String(index + 1).padStart(2, '0')}</span>
  <div><h3>${escapeHTML(item.title)}</h3><span class="roadmap-tag">${escapeHTML(item.priority)} · Not deployed</span><p class="roadmap-bundle">${escapeHTML(bundles[item.bundle])}</p></div>
  <div class="roadmap-explanation"><p>${escapeHTML(item.value)}</p><p class="roadmap-boundary"><strong>Boundary:</strong> ${escapeHTML(item.boundary)}</p></div>
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
    BUNDLE_OPTIONS: options(bundles),
    STATUS_OPTIONS: options(statuses),
    CARDS: candidates.map(renderCard).join('\n'),
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
  await mkdir(dist, { recursive: true });
  await Promise.all([
    writeFile(new URL('index.html', dist), html, 'utf8'),
    writeFile(new URL('staticwebapp.config.json', dist), `${JSON.stringify(config, null, 2)}\n`, 'utf8'),
  ]);
  return { bytes: Buffer.byteLength(html), html, config };
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  const result = await buildSite();
  console.log(`Built dist/index.html (${result.bytes.toLocaleString('en-US')} bytes) and dist/staticwebapp.config.json.`);
  console.log('20 candidates · 5 planned workflows · 2 script hashes · 1 style hash · no runtime dependencies');
}
