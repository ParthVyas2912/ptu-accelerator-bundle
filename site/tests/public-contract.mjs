import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { platformGuides, sources } from '../src/onboarding.mjs';
import { dossiers } from '../src/dossiers.mjs';
import { catalogReview, programSources } from '../src/program.mjs';

export const repositoryURL = 'https://github.com/ParthVyas2912/ptu-accelerator-bundle';
export const deployedURL = 'https://blue-beach-0fb8cd70f.5.azurestaticapps.net/';

export function assertPublicContent(output, additionalPublicURLs = []) {
  const scrubbed = output.replaceAll(repositoryURL, '');
  const forbidden = [
    /\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/i,
    /\b[A-Z]:[\\/]|\\\\[a-z0-9_-]+\\/i,
    /\/(?:subscriptions|tenants|resourcegroups|providers\/microsoft)\//i,
    /(?:subscription|tenant|resource|client|object|account)[_-]?id["'\s:=]/i,
    /(?:resource[ _-]?group|azure[ _-]?account|storage[ _-]?account)[ _-]?(?:name|id)["'\s:=]/i,
    /\brg-[a-z0-9]+(?:-[a-z0-9]+)+\b/i,
    /\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b/i,
    /\b(?:\d{1,3}\.){3}\d{1,3}\b/,
    /privatelink|private[ -]endpoint|\.azurewebsites\.net|\.openai\.azure\.com/i,
    /partvyas|parth\s+vyas|OneDrive|Desktop[\\/]|Users[\\/]/i,
    /deployment-contract|azure-resources-before|raw[ -]evidence|raw[ -]logs/i,
    /BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|ghp_[a-z0-9]+|AccountKey=|SharedAccessSignature=/i,
    /\b(?:trusted by|used by customers|customer success story|officially endorsed)\b/i,
    /\bDRDC\b|\bJDCP\b|Research Productivity Bundle|Maritime Information Warfare/i,
  ];
  // Report the rule, never the matching content.
  for (const pattern of forbidden) assert.equal(pattern.test(scrubbed), false, `Public privacy check failed: ${pattern}`);
  const allowed = new Set([
    repositoryURL,
    deployedURL,
    'https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput',
    'https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-bring-your-own-model',
    ...Object.values(sources).flatMap(({ repository, guide }) => [repository, guide]),
    ...Object.values(platformGuides),
    ...Object.values(dossiers).flatMap((dossier) => dossier.sources.map(({ url }) => url)),
    ...catalogReview.map(({ url }) => url),
    ...programSources.map(({ url }) => url),
    ...additionalPublicURLs,
  ]);
  for (const [, href] of output.matchAll(/\bhref="([^"]+)"/g)) {
    assert.ok(href.startsWith('#') || allowed.has(href), 'Public page contains an unapproved link.');
  }
  assert.match(output, /The project repository is public/);
  assert.match(output, /repository access does not grant customer-environment access/);
  assert.doesNotMatch(output, /The repository is private|Private GitHub repository|Contributor access required/);
}

export function assertServedPolicy(html, headers) {
  const policy = headers['content-security-policy'] || '';
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
  const styles = [...html.matchAll(/<style>([\s\S]*?)<\/style>/g)].map((match) => match[1]);
  assert.equal(scripts.length, 2, 'Expected the two self-contained script blocks.');
  assert.equal(styles.length, 1, 'Expected the self-contained stylesheet.');
  for (const text of [...scripts, ...styles]) {
    const hash = `'sha256-${createHash('sha256').update(text).digest('base64')}'`;
    assert.ok(policy.includes(hash), 'Delivered CSP does not hash the exact delivered content.');
  }
  for (const rule of ["connect-src 'none'", "frame-ancestors 'none'", "base-uri 'none'", "form-action 'none'"]) {
    assert.ok(policy.includes(rule), `Missing HTTP CSP directive: ${rule}`);
  }
  assert.doesNotMatch(policy, /unsafe-inline|unsafe-eval|\*/);
  assert.equal(headers['x-content-type-options'], 'nosniff');
  assert.equal(headers['x-frame-options'], 'DENY');
  assert.equal(headers['referrer-policy'], 'no-referrer');
}

// HEAD only; never retrieve bodies from these paths. A 200 fallback is a failure.
export const nonPublicPaths = [
  '/package.json',
  '/package-lock.json',
  '/README.md',
  '/src/content.mjs',
  '/scripts/build.mjs',
  '/tests/browser.mjs',
  '/node_modules/playwright/package.json',
  '/.env',
  '/.git/config',
  '/reports/',
  '/evidence/',
  '/logs/',
  '/infra/',
  '/docs/DRDC-RESEARCH-BUNDLE.md',
  '/src/onboarding.mjs',
  '/src/experiences.mjs',
  '/src/dossiers.mjs',
  '/src/program.mjs',
  '/deployment-contract.json',
  '/azure-resources-before.json',
  '/__smoke_missing_route__',
];
