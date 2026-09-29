import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { startServer } from '../scripts/serve.mjs';
import { candidates, catalogCandidates, roadmap, topPicks } from '../src/content.mjs';
import { onboarding, problems } from '../src/onboarding.mjs';
import { dossiers } from '../src/dossiers.mjs';
import { solutionVisuals } from '../src/visuals.mjs';
import { resolveSmokeTarget, smokeHelp } from './smoke-options.mjs';
import { assertPublicContent, assertServedPolicy, nonPublicPaths } from './public-contract.mjs';

const options = resolveSmokeTarget(process.argv.slice(2), process.env.SITE_URL || '');
if (options.help) {
  console.log(smokeHelp);
  process.exit(0);
}

// Keep the matching browser download inside ignored site/node_modules/.
process.env.PLAYWRIGHT_BROWSERS_PATH = '0';
const mode = options.url ? 'deployed' : 'local';
const results = new URL(`../test-results/smoke/${mode}/`, import.meta.url);
await mkdir(results, { recursive: true });
const report = {
  mode, target: options.url, status: 'running', startedAt: new Date().toISOString(),
  checkFrom: process.env.SITE_CHECK_FROM || null,
  checks: [], themes: {}, viewports: [], screenshots: [], exposureChecks: [],
  requests: [], externalRequests: [], unexpectedRequests: [], errors: [], cspViolations: [],
};
let server;
let url = options.url;
let browser;
let browserServer;
let page;
let AxeBuilder;
let passed = 0;
async function withDeadline(promise, milliseconds, message) {
  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(message)), milliseconds); }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}
async function stopOwnedBrowser() {
  if (!browserServer) return;
  const child = browserServer.process();
  const stopped = () => {
    if (child.exitCode !== null || child.signalCode !== null) return true;
    try {
      process.kill(child.pid, 0); // Existence probe only; no signal is delivered.
      return false;
    } catch (error) {
      if (error.code === 'ESRCH') return true;
      throw error;
    }
  };
  if (process.platform === 'win32' && !stopped()) {
    assert.ok(Number.isSafeInteger(child.pid) && child.pid > 0);
    // Stop only the process tree launched by this run, by exact numeric IDs.
    // Do not rely on a potentially stalled Windows driver shutdown promise.
    const script = `
      function Stop-OwnedTree([int]$ownedId) {
        Get-CimInstance Win32_Process -Filter "ParentProcessId = $ownedId" |
          ForEach-Object { Stop-OwnedTree ([int]$_.ProcessId) }
        Stop-Process -Id $ownedId -Force -ErrorAction SilentlyContinue
      }
      Stop-OwnedTree ${child.pid}
    `;
    await promisify(execFile)('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', script], {
      windowsHide: true, timeout: 30_000,
    });
  }
  try {
    await withDeadline(browserServer.kill(), process.platform === 'win32' ? 5_000 : 30_000, 'Owned browser termination timed out.');
  } catch (error) {
    // Process exit is the completion criterion, not delayed driver bookkeeping.
    if (!stopped()) throw error;
  }
  assert.ok(stopped(), 'The owned browser process did not exit.');
  report.browserStopped = true;
}
let checksStarted = !report.checkFrom;
const run = async (name, action) => {
  if (!checksStarted) checksStarted = name.startsWith(report.checkFrom);
  if (!checksStarted) return;
  console.log(`RUN  ${name}`);
  const check = { name, status: 'running' };
  report.checks.push(check);
  try {
    await withDeadline(action(), 120_000, `Browser check timed out: ${name}`);
    check.status = 'passed';
    passed += 1;
    console.log(`PASS ${name}`);
  } catch (error) {
    check.status = 'failed';
    check.message = error.message;
    throw error;
  }
};
const visible = (page) => page.locator('.candidate:visible');
const goView = (page, view) => page.locator(`[data-view-link="${view}"]`).click();
const screenshot = async (page, name, fullPage = false) => {
  const scroll = await page.evaluate(() => ({ x: window.scrollX, y: window.scrollY }));
  if (fullPage) await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: fileURLToPath(new URL(name, results)), fullPage, animations: 'disabled', timeout: 60_000 });
  if (fullPage) await page.evaluate(({ x, y }) => window.scrollTo(x, y), scroll);
  report.screenshots.push(name);
};
const assertNoOverflow = async (page) => {
  const widths = await page.evaluate(() => ({
    theme: document.documentElement.dataset.theme, content: document.documentElement.scrollWidth, viewport: innerWidth,
  }));
  report.viewports.push(widths);
  assert.ok(widths.content <= widths.viewport + 1, `Horizontal overflow: ${JSON.stringify(widths)}`);
};
const assertTheme = async (page, theme) => {
  const actual = await page.evaluate(() => {
    const root = getComputedStyle(document.documentElement);
    const body = getComputedStyle(document.body);
    return {
      theme: document.documentElement.dataset.theme,
      backgroundToken: root.getPropertyValue('--cp-bg').trim(),
      accentToken: root.getPropertyValue('--cp-accent').trim(),
      actionToken: root.getPropertyValue('--cp-action').trim(),
      primaryBackground: getComputedStyle(document.querySelector('.button.primary')).backgroundColor,
      primaryForeground: getComputedStyle(document.querySelector('.button.primary')).color,
      primaryBackgrounds: [...new Set([...document.querySelectorAll('.button.primary')]
        .map((button) => getComputedStyle(button).backgroundColor))],
      heroEmphasis: getComputedStyle(document.querySelector('.hero h1 span')).color,
      panelBackground: getComputedStyle(document.querySelector('.showcase-tile')).backgroundColor,
      background: body.backgroundColor,
      font: body.fontFamily,
      cardRadius: getComputedStyle(document.querySelector('.candidate')).borderRadius,
      catalogDisplay: getComputedStyle(document.querySelector('.catalog-grid')).display,
    };
  });
  assert.equal(actual.theme, theme);
  assert.equal(actual.backgroundToken, theme === 'light' ? '#f7f4ef' : '#3d3b3a');
  assert.equal(actual.accentToken, theme === 'light' ? '#b11f4b' : '#fd8ea1');
  assert.equal(actual.actionToken, actual.accentToken);
  assert.equal(actual.primaryBackground, theme === 'light' ? 'rgb(177, 31, 75)' : 'rgb(253, 142, 161)');
  assert.equal(actual.primaryForeground, theme === 'light' ? 'rgb(255, 255, 255)' : 'rgb(26, 26, 26)');
  assert.deepEqual(actual.primaryBackgrounds, [actual.primaryBackground],
    'Homepage, catalog, dossier and guide primary actions must share one accent.');
  assert.equal(actual.heroEmphasis, actual.primaryBackground);
  assert.equal(actual.panelBackground, theme === 'light' ? 'rgb(255, 255, 255)' : 'rgb(41, 41, 41)');
  assert.equal(actual.background, theme === 'light' ? 'rgb(247, 244, 239)' : 'rgb(61, 59, 58)');
  assert.match(actual.font, /^"Segoe UI", Aptos, Calibri,/);
  assert.equal(actual.cardRadius, '16px');
  assert.equal(actual.catalogDisplay, 'grid');
  report.themes[theme] = actual;
};
const audit = async (page) => {
  const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
  assert.deepEqual(result.violations.map((item) => ({
    id: item.id,
    impact: item.impact,
    nodes: item.nodes.map((node) => ({ target: node.target, summary: node.failureSummary })),
  })), []);
};

async function observeContext(context) {
  const allowedPaths = new Set(['/', '/index.html', '/favicon.ico']);
  const allowedRequest = (request) => {
    const target = new URL(request.url());
    return target.origin === new URL(url).origin && allowedPaths.has(target.pathname) && request.method() === 'GET';
  };
  context.on('page', (observedPage) => {
    observedPage.on('pageerror', (error) => report.errors.push(error.message));
    observedPage.on('console', (message) => {
      if (message.type() === 'error') report.errors.push(message.text());
      if (message.text().startsWith('SMOKE_CSP:')) report.cspViolations.push(message.text().slice(10));
    });
  });
  context.on('request', (request) => {
    report.requests.push(request.url());
    if (new URL(request.url()).origin !== new URL(url).origin) report.externalRequests.push(request.url());
    if (!allowedRequest(request)) report.unexpectedRequests.push(request.url());
  });
  await context.addInitScript(() => {
    window.__cspViolations = [];
    document.addEventListener('securitypolicyviolation', (event) => {
      window.__cspViolations.push(event.violatedDirective);
      console.error(`SMOKE_CSP:${event.violatedDirective}`);
    });
  });
  // Never let an unexpected page request download a private path or call an API.
  await context.route('**/*', (route) => allowedRequest(route.request()) ? route.continue() : route.abort());
}

try {
  const { chromium } = await import('playwright');
  ({ default: AxeBuilder } = await import('@axe-core/playwright'));
  if (!url) ({ server, url } = await startServer(0));
  report.target = url;
  console.log(`Smoke target: ${url} (${mode})`);
  // A dedicated loopback driver gives this run ownership of its browser process,
  // including a deterministic termination path if graceful shutdown stalls.
  browserServer = await chromium.launchServer({ headless: true, host: '127.0.0.1' });
  browser = await chromium.connect(browserServer.wsEndpoint());
  report.browser = browser.version();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 }, colorScheme: 'dark', reducedMotion: 'reduce', serviceWorkers: 'block',
  });
  context.setDefaultTimeout(15_000);
  context.setDefaultNavigationTimeout(30_000);
  await observeContext(context);
  await context.addInitScript(() => {
    window.__problemClickRegistrations = [];
    window.__discussClickRegistrations = [];
    const addEventListener = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function (type, listener, options) {
      if (type === 'click' && this instanceof HTMLAnchorElement && this.hasAttribute('data-problem-link')) {
        window.__problemClickRegistrations.push(this.dataset.problemLink);
      }
      if (type === 'click' && this instanceof HTMLButtonElement && this.hasAttribute('data-discuss')) {
        window.__discussClickRegistrations.push(this.dataset.discuss);
      }
      return addEventListener.call(this, type, listener, options);
    };
  });
  page = await context.newPage();

  await run('served CSP allows the self-contained overview, retains 20 candidates and honors explicit light over dark OS', async () => {
    const response = await page.goto(`${url}/?scoutTheme=light`, { waitUntil: 'networkidle' });
    assert.equal(response.status(), 200, 'Site is unavailable or not deployed: expected HTTP 200.');
    assert.equal(await page.locator('.candidate').count(), 20, 'Expected the 20-entry AI Solutions Hub. Publish site/dist/ before running the deployed smoke test.');
    assert.equal(await visible(page).count(), 0, 'The overview should not overwhelm readers with the full catalog.');
    assert.equal(await page.locator('#top').isVisible(), true);
    assert.equal(await page.locator('#start').isVisible(), true);
    assert.equal(await page.locator('[data-view-link="overview"]').getAttribute('aria-current'), 'page');
    const html = await response.text();
    assertPublicContent(html, [url, `${url}/`]);
    assertServedPolicy(html, response.headers());
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await assertTheme(page, 'light');
    assert.equal(await page.locator('.detail-button').count(), 20);
    assert.equal(await page.locator('.roadmap-item').count(), 5);
    await assertNoOverflow(page);
    assert.deepEqual(await page.evaluate(() => window.__cspViolations), []);
    await screenshot(page, 'desktop-light.png');
    await screenshot(page, 'desktop-light-full.png', true);
  });

  await run('private/source paths and unknown routes do not serve files or an index fallback (HEAD only)', async () => {
    for (const path of nonPublicPaths) {
      const response = await context.request.head(new URL(path, url).href, {
        maxRedirects: 0, failOnStatusCode: false, timeout: 15_000,
      });
      const status = response.status();
      report.exposureChecks.push({ path, method: 'HEAD', status });
      await response.dispose();
      assert.ok([401, 403, 404, 410].includes(status), `Non-public path returned ${status}: ${path}. Check artifact scope and fallback rules.`);
    }
  });

  await run('all four light-theme views pass automated WCAG 2.1 AA checks', async () => {
    for (const view of ['overview', 'catalog', 'guide', 'roadmap']) {
      await goView(page, view);
      await audit(page);
      await screenshot(page, `${view}-light-full.png`, true);
    }
  });

  await run('concise visual overview keeps discovery prominent and leads with top picks from one catalog', async () => {
    await goView(page, 'overview');
    const map = page.locator('.workflow-showcase');
    assert.equal(await map.locator('.showcase-tile').count(), 3);
    assert.match(await map.locator('figcaption').textContent(), /An adoption journey, not a system architecture/);
    assert.match(await map.locator('.showcase-boundary').textContent(), /Results depend on fit and delivery/);
    assert.ok((await page.locator('.hero-copy').innerText()).trim().split(/\s+/).length <= 75);
    assert.ok((await page.locator('#orientation').innerText()).trim().split(/\s+/).length <= 40);
    assert.ok((await page.locator('main').innerText()).trim().split(/\s+/).length <= 500,
      'Keep the default overview scannable; detailed planning belongs in the guide.');
    assert.equal(await page.locator('#program').isVisible(), false);
    assert.equal(await page.locator('#glossary').isVisible(), false);
    assert.equal(await page.locator('.problem-icon:visible').count(), 6);
    assert.match(await page.locator('#hero-title').innerText(), /Useful AI/);
    assert.match(await page.locator('.hero-description').innerText(), /Choose your mix/);
    assert.match(await map.locator('.showcase-boundary').innerText(), /Compatible workloads only/);
    assert.deepEqual(await page.locator('.top-pick strong').allTextContents(),
      topPicks.map((id) => candidates.find((item) => item.id === id).name));
    assert.equal(await page.locator('.bundle-card, .bundle-inventory, [data-bundle-link], #bundle-filter').count(), 0);
    await page.locator('.hero-actions .primary').click();
    assert.equal(new URL(page.url()).hash, '#start');
    assert.equal(await page.locator('#start-title').evaluate((node) => node === document.activeElement), true);
    await goView(page, 'overview');
    await page.locator('.adoption-band .text-link').click();
    assert.equal(new URL(page.url()).hash, '#pilot-gates');
    assert.equal(await page.locator('html').getAttribute('data-view'), 'guide');
    assert.match(await page.locator('#pilot-gates').innerText(), /baseline.*PTU utilization and headroom.*total service cost/s);
    await goView(page, 'overview');
    await page.locator('.adoption-service a').click();
    assert.equal(new URL(page.url()).hash, '#engagement');
    assert.equal(await page.locator('html').getAttribute('data-view'), 'guide');
    assert.equal(await page.locator('#engagement-title').evaluate((node) => node === document.activeElement), true);
    assert.equal(await page.locator('#engagement .workflow-steps li').count(), 4);
    await page.locator('#implementation-brief a[href="#shortlist"]').click();
    assert.equal(await page.locator('html').getAttribute('data-view'), 'catalog');
    await page.locator('#catalog .section-heading a[href="#engagement"]').click();
    assert.equal(new URL(page.url()).hash, '#engagement');
    await goView(page, 'overview');
    await page.locator('#top-picks').scrollIntoViewIfNeeded();
    await screenshot(page, 'top-picks-light.png');
    await page.locator(`.top-pick a[href="#solution-${topPicks[1]}"]`).focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('html').getAttribute('data-view'), 'solution');
    assert.equal(await page.locator(`#solution-${topPicks[1]}`).isVisible(), true);
    await goView(page, 'overview');
    await page.locator('#top-picks a[href="#catalog"]').click();
    assert.equal(await page.locator('html').getAttribute('data-view'), 'catalog');
    await goView(page, 'overview');
    assert.equal(await page.locator('[data-problem-link]').first().getAttribute('data-problem-link'), 'engineering');
    await goView(page, 'catalog');
    assert.equal(await page.locator('.status-badge, #status-filter, .evidence-key').count(), 0);
    assert.doesNotMatch(await page.locator('#catalog').textContent(), /Selected tests verified|Not launch-ready|Readiness/);
    assert.deepEqual(await page.locator('[data-problem-choice]').evaluateAll((nodes) => nodes.map((node) => node.dataset.problemChoice)),
      ['all', ...Object.keys(problems)]);
    assert.deepEqual(await page.locator('.candidate').evaluateAll((nodes) => nodes.map((node) => Number(node.dataset.id))),
      catalogCandidates.map((item) => item.id));
    assert.equal(await page.locator('.candidate .top-pick-badge').count(), topPicks.length);
    await goView(page, 'roadmap');
    assert.match(await page.locator('.roadmap-item').first().textContent(), /Concept.*Not built or deployed/);
    assert.equal(await page.locator('.roadmap-boundary:visible').count(), 5);
  });

  for (const id of ['program', 'glossary', 'preparation', 'selection-review']) {
    for (const theme of ['light', 'dark']) {
      await run(`${id} disclosure supports keyboard, reflow and accessibility in ${theme} theme`, async () => {
        await page.goto(`${url}/?scoutTheme=${theme}#capacity`, { waitUntil: 'networkidle' });
        const detail = page.locator(`#${id}`);
        assert.equal(await detail.getAttribute('open'), null);
        const content = detail.locator('.reference-content');
        assert.equal(await content.isVisible(), false);
        await detail.locator(':scope > summary').focus();
        await page.keyboard.press('Enter');
        assert.equal(await content.isVisible(), true);
        for (const width of [320, 1440]) {
          await page.setViewportSize({ width, height: 1000 });
          await assertNoOverflow(page);
          await audit(page);
        }
        await detail.locator(':scope > summary').focus();
        await page.keyboard.press('Space');
        assert.equal(await content.isVisible(), false);
      });
    }
  }

  await run('navigation supports focused views, keyboard focus, history, deep links and safe invalid fragments', async () => {
    const views = { overview: '#hero-title', catalog: '#catalog-title', guide: '#capacity-title', roadmap: '#roadmap-title' };
    for (const [view, heading] of Object.entries(views)) {
      await goView(page, view);
      assert.equal(await page.locator('html').getAttribute('data-view'), view);
      assert.deepEqual(await page.locator('[data-page]:visible').evaluateAll((nodes) =>
        [...new Set(nodes.map((node) => node.dataset.page))]), [view]);
      assert.equal(await page.locator(heading).evaluate((node) => node === document.activeElement), true);
      assert.equal(await page.locator('[aria-current="page"]').count(), 1);
    }
    await page.goBack();
    await page.waitForFunction(() => document.documentElement.dataset.view === 'guide');
    await page.goForward();
    await page.waitForFunction(() => document.documentElement.dataset.view === 'roadmap');
    for (const [hash, view] of [
      ['catalog', 'catalog'], ['candidate-title-11', 'catalog'], ['start', 'overview'], ['top-picks', 'overview'],
      ['program', 'guide'], ['pathway-answers', 'guide'], ['glossary', 'guide'], ['selection-review', 'guide'],
      ['how-it-works', 'guide'], ['questions', 'guide'], ['sources', 'guide'], ['roadmap', 'roadmap'],
      ['solution-18', 'overview'], ['solution-20', 'overview'], ['solution-18-architecture', 'overview'],
      ['unknown-section', 'overview'], ['%E0%A4%A', 'overview'],
    ]) {
      await page.goto(`${url}/?scoutTheme=light#${hash}`, { waitUntil: 'networkidle' });
      assert.equal(await page.locator('html').getAttribute('data-view'), view, hash);
      if (['program', 'pathway-answers', 'glossary'].includes(hash)) {
        assert.equal(await page.locator(`#${hash}`).isVisible(), true);
        assert.equal(await page.locator(`#${hash}`).evaluate((node) => node.closest('details').open), true);
      }
    }
    await page.keyboard.press('/');
    assert.equal(await page.locator('html').getAttribute('data-view'), 'catalog');
    assert.equal(await page.locator('#catalog-search').evaluate((node) => node === document.activeElement), true);
    await page.keyboard.type('CWYD');
    assert.deepEqual(await visible(page).evaluateAll((nodes) => nodes.map((node) => node.dataset.id)), ['1', '4']);
    await page.keyboard.press('Escape');
    assert.equal(await visible(page).count(), 20);
    assert.equal(await page.locator('#catalog-search').inputValue(), '');
  });

  await run('search works by aliases and detail text, stays literal and handles zero results', async () => {
    await page.goto(`${url}/?scoutTheme=light#catalog`);
    const search = page.locator('#catalog-search');
    const images = await page.locator('img').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('src')));
    for (const retired of ['Harbinger', 'StepFly']) {
      await search.fill(retired);
      assert.equal(await visible(page).count(), 0);
      assert.equal(await page.locator('#result-count').textContent(), 'Showing 0 of 20 solutions');
    }
    await search.fill('CWYD');
    // DKM's maintenance guidance now explicitly recommends CWYD for general knowledge work.
    assert.deepEqual(await visible(page).evaluateAll((nodes) => nodes.map((node) => node.dataset.id)), ['1', '4']);
    assert.equal(await visible(page).first().getAttribute('data-id'), '1');
    await search.fill('  BYOM  ');
    assert.equal(await visible(page).count(), 1);
    assert.equal(await visible(page).first().getAttribute('data-id'), '11');
    await search.fill('<img src=x onerror="window.searchInjected=true">');
    assert.equal(await visible(page).count(), 0);
    assert.equal(await page.locator('#empty-state').isVisible(), true);
    assert.equal(await page.locator('#result-count').textContent(), 'Showing 0 of 20 solutions');
    assert.equal(await page.evaluate(() => window.searchInjected), undefined);
    assert.deepEqual(await page.locator('img').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('src'))), images);
    assert.equal(await page.locator('img[src="x"], [onerror]').count(), 0);
    await page.locator('#clear-empty').click();
    assert.equal(await visible(page).count(), 20);
    assert.equal(await page.locator('#catalog-search').evaluate((node) => node === document.activeElement), true);
  });

  await run('every problem chip returns matching solutions in customer-priority order', async () => {
    for (const problem of ['all', ...Object.keys(problems)]) {
      await page.locator(`[data-problem-choice="${problem}"]`).click();
      assert.equal(await page.locator('#problem-filter').inputValue(), problem);
      assert.equal(await page.locator(`[data-problem-choice="${problem}"]`).getAttribute('aria-pressed'), 'true');
      const expected = catalogCandidates.filter((item) => problem === 'all'
        || onboarding[item.id].problems.includes(problem)).map((item) => item.id);
      const actual = await visible(page).evaluateAll((nodes) => nodes.map((node) => Number(node.dataset.id)));
      assert.deepEqual(actual, expected, problem);
    }
    await page.locator('#reset-filters').click();
    assert.equal(await page.locator('[data-problem-choice="all"]').getAttribute('aria-pressed'), 'true');
    await page.locator('#catalog-search').fill('proposal');
    assert.equal(await visible(page).count(), 1);
    assert.equal(await visible(page).first().getAttribute('data-id'), '12');
    await page.locator('#reset-filters').click();
    await page.locator('#catalog').scrollIntoViewIfNeeded();
    await screenshot(page, 'catalog-light.png');
  });

  await run('card/list controls preserve results and filters across navigation without losing evidence access', async () => {
    await page.locator('#view-switch [data-layout="list"]').click();
    assert.equal(await page.locator('#catalog-grid').getAttribute('data-layout'), 'list');
    assert.equal(await page.locator('#view-switch [data-layout="list"]').getAttribute('aria-pressed'), 'true');
    assert.equal(await visible(page).count(), 20);
    await page.locator('[data-problem-choice="engineering"]').click();
    await page.locator('#catalog-search').fill('conversion');
    const conversionResults = await visible(page).evaluateAll((nodes) => nodes.map((node) => node.dataset.id));
    assert.ok(conversionResults.includes('9'));
    assert.ok(conversionResults.length < 20);
    await goView(page, 'guide');
    await goView(page, 'catalog');
    assert.equal(await page.locator('#catalog-search').inputValue(), 'conversion');
    assert.equal(await page.locator('#problem-filter').inputValue(), 'engineering');
    assert.equal(await page.locator('#catalog-grid').getAttribute('data-layout'), 'list');
    assert.deepEqual(await visible(page).evaluateAll((nodes) => nodes.map((node) => node.dataset.id)), conversionResults);
    await page.locator('.candidate[data-id="9"] .detail-button').click();
    assert.equal(await page.locator('#solution-9').isVisible(), true);
    await page.locator('#solution-9 .solution-back').click();
    assert.equal(await page.locator('#candidate-title-9').evaluate((node) => node === document.activeElement), true);
    await page.locator('#reset-filters').click();
    await audit(page);
    await screenshot(page, 'catalog-list-light.png');
    await page.locator('#view-switch [data-layout="grid"]').click();
    assert.equal(await page.locator('#view-switch [data-layout="grid"]').getAttribute('aria-pressed'), 'true');
  });

  for (const candidate of candidates) {
    await run(`dossier ${candidate.id}: workflow, graph, sources, deployment, specialist guidance and all section links`, async () => {
      if (page.url() === 'about:blank') {
        await page.goto(`${url}/?scoutTheme=light#catalog`, { waitUntil: 'networkidle' });
      }
      const trigger = page.locator(`.candidate[data-id="${candidate.id}"] .detail-button`);
      await trigger.click();
      const solution = page.locator(`#solution-${candidate.id}`);
      assert.equal(new URL(page.url()).hash, `#solution-${candidate.id}`);
      assert.equal(await page.locator('.solution-page:visible').count(), 1);
      assert.equal(await solution.locator('h2').textContent(), candidate.name);
      assert.equal(await solution.locator('h2').evaluate((node) => node === document.activeElement), true);
      const dossier = dossiers[candidate.id];
      assert.deepEqual(await solution.locator('.solution-lead .solution-summary dt').allTextContents(),
        ['What it is', 'How it works', 'Use it for', 'Example scenario']);
      assert.deepEqual(await solution.locator('.solution-lead .solution-summary dd').allTextContents(),
        Object.values(dossier.plain.brief));
      assert.equal(await page.locator(`.candidate[data-id="${candidate.id}"] .candidate-value`).textContent(), candidate.value);
      assert.equal(await solution.locator('.solution-visual .visual-flow li').count(), 3);
      assert.deepEqual(await solution.locator('.visual-flow li > span').allTextContents(),
        solutionVisuals[candidate.id].stages.map(([, label]) => label));
      const codeAccess = solution.locator('.code-access');
      if (dossier.repository) {
        assert.equal(await codeAccess.locator('a[target="_blank"]').getAttribute('href'), dossier.repository);
        assert.match(await codeAccess.textContent(), /Open public repository \(pinned\)/);
      } else {
        assert.equal(await codeAccess.locator('a[target="_blank"]').count(), 0);
        assert.ok((await codeAccess.textContent()).includes(dossier.privateSource || 'Repository not verified'));
      }
      assert.equal(await codeAccess.locator('a[href="#engagement"]').count(), 1);
      if (dossier.sourceReview) {
        assert.equal(await solution.locator('.source-review').isVisible(), true);
        assert.ok((await solution.locator('.source-review').textContent()).includes(dossier.sourceReview.summary));
      }
      assert.ok((await solution.textContent()).includes(dossier.workshop));
      const plainText = await solution.locator(`#solution-${candidate.id}-plain`).textContent();
      assert.ok(plainText.includes(dossier.plain.what), 'plain summary');
      assert.ok(plainText.includes(dossier.plain.form), 'what arrives');
      assert.ok(plainText.includes(candidate.evidence), 'benefits are qualified by evidence in place');
      assert.equal(await solution.locator('.app-preview').count(), 0);
      assert.equal(await solution.locator('.workflow-steps li').count(), dossier.workflow.length);
      assert.equal(await solution.locator('.component-graph .graph-node').count(), dossier.architecture.nodes.length);
      assert.equal(await solution.locator('.component-graph .graph-edge').count(), dossier.architecture.edges.length);
      const labelIssues = await solution.locator('.graph-node').evaluateAll((nodes) => nodes.flatMap((node) => {
        const labels = [...node.querySelectorAll('text')].map((text) => ({
          label: text.textContent, box: text.getBBox(),
        }));
        return labels.flatMap(({ label, box }, index) => {
          const outside = box.x < 0 || box.y < 0 || box.x + box.width > 230 || box.y + box.height > 120;
          const overlap = index > 0 && box.y < labels[index - 1].box.y + labels[index - 1].box.height;
          return outside || overlap ? [label] : [];
        });
      }));
      assert.deepEqual(labelIssues, [], 'Diagram labels must fit their component without overlapping');
      assert.equal(await solution.locator('.ingestion-steps li').count(), dossier.ingestion.stages.length);
      assert.equal(await solution.locator('.setup-steps li').count(), dossier.deployment.walkthrough.steps.length);
      assert.equal(await solution.locator('.specialist-roles li').count(), dossier.specialists.length);
      assert.equal(await solution.locator('.dossier-sources a').count(), dossier.sources.length);
      assert.equal(await solution.locator('.solution-nav [aria-current="location"]').textContent(), 'Overview');
      const navHashes = await solution.locator('.solution-nav a')
        .evaluateAll((nodes) => nodes.map((node) => node.getAttribute('href')));
      assert.equal(new Set(navHashes).size, navHashes.length, 'Section links must address distinct sections');
      for (const hash of navHashes) {
        const link = solution.locator(`.solution-nav a[href="${hash}"]`);
        await link.focus();
        await link.press('Enter');
        await page.waitForFunction((value) => window.location.hash === value, hash);
        assert.equal(new URL(page.url()).hash, hash);
        assert.equal(await page.locator(hash).isVisible(), true);
      }
      await solution.locator('.connection-details summary').click();
      assert.equal(await solution.locator('.connection-list li:visible').count(), dossier.architecture.edges.length);
      await solution.locator('.connection-details summary').click();
      await solution.locator('.deployment-notes summary').click();
      assert.equal(await solution.locator('.deployment-notes').getAttribute('open'), null);
      for (const link of await solution.locator('a[target="_blank"]').all()) {
        assert.equal(await link.getAttribute('target'), '_blank');
        assert.equal(await link.getAttribute('rel'), 'noopener noreferrer');
        assert.match(await link.textContent(), /opens in a new tab/);
      }
      await solution.locator(`.solution-nav a[href="#solution-${candidate.id}-notes"]`).click();
      assert.ok((await solution.locator('.deployment-notes').textContent()).includes(candidate.evidence));
      assert.ok((await solution.locator('.deployment-notes').textContent()).includes(candidate.ptu));
      assert.equal(await solution.locator('.deployment-notes').getAttribute('open'), '');
      await audit(page);
      if (candidate.id === 3) {
        await solution.locator('.code-access a[href="#engagement"]').click();
        assert.equal(await page.locator('#engagement').isVisible(), true);
        await page.goBack();
        assert.equal(await solution.isVisible(), true);
      }
      await solution.locator('.solution-back').click();
      assert.equal(await page.locator(`#candidate-title-${candidate.id}`).evaluate((node) => node === document.activeElement), true);
    });
  }

  await run('problem discovery intersects existing filters and resets predictably', async () => {
    assert.deepEqual(await page.evaluate(() => window.__problemClickRegistrations), Object.keys(problems));
    for (const key of Object.keys(problems)) {
      await goView(page, 'overview');
      await page.locator(`[data-problem-link="${key}"]`).click();
      assert.equal(await page.locator('#problem-filter').inputValue(), key);
      assert.equal(await page.locator('html').getAttribute('data-view'), 'overview');
      const expected = catalogCandidates.filter((item) => onboarding[item.id].problems.includes(key)).map((item) => item.id);
      assert.equal(await page.locator('#finder-matches article').count(), Math.min(3, expected.length));
      assert.equal(await page.locator('#finder-title').evaluate((node) => node === document.activeElement), true);
      await page.locator('#finder-results a[href="#catalog"]').click();
      assert.equal(await page.locator('html').getAttribute('data-view'), 'catalog');
      assert.deepEqual(await visible(page).evaluateAll((nodes) => nodes.map((node) => Number(node.dataset.id))), expected);
    }
    await page.locator('#reset-filters').click();
    assert.equal(await page.locator('#problem-filter').inputValue(), 'all');
    assert.equal(await visible(page).count(), 20);
  });

  await run('shortlist supports multiple solutions, removal, navigation and selected-plan printing', async () => {
    await page.goto(`${url}/?scoutTheme=light#catalog`, { waitUntil: 'networkidle' });
    for (const id of [1, 12]) {
      await page.locator(`.candidate[data-id="${id}"] .detail-button`).click();
      await page.locator(`[data-select="${id}"]`).click();
      assert.equal(await page.locator(`[data-select="${id}"]`).getAttribute('aria-pressed'), 'true');
      await page.locator(`#solution-${id} a[href="#shortlist"]`).click();
      await page.waitForFunction(() => document.activeElement?.id === 'shortlist-title');
      assert.equal(new URL(page.url()).hash, '#shortlist');
      assert.equal(await page.locator('#shortlist').isVisible(), true);
    }
    assert.equal(await page.locator('.shortlist-item').count(), 2);
    assert.equal(await page.locator('.selected-guide .solution-summary').count(), 2);
    const ids = await page.locator('[id]').evaluateAll((nodes) => nodes.map((node) => node.id));
    assert.equal(ids.length, new Set(ids).size, 'Shortlist clones must not duplicate anchor/label IDs.');
    await page.locator('#catalog-search').fill('CWYD');
    await goView(page, 'guide');
    await goView(page, 'catalog');
    assert.equal(await page.locator('.shortlist-item').count(), 2);
    await page.locator('.selected-guide summary').first().click();
    await audit(page);
    await assertNoOverflow(page);
    const viewport = page.viewportSize();
    await page.setViewportSize({ width: 320, height: 850 });
    await audit(page);
    await assertNoOverflow(page);
    await screenshot(page, 'shortlist-mobile-light.png', true);
    await page.setViewportSize(viewport);
    await page.evaluate(() => { window.print = () => window.dispatchEvent(new Event('beforeprint')); });
    await page.locator('#print-plan').click();
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('#shortlist').isVisible(), true);
    assert.equal(await page.locator('.candidate:visible').count(), 0);
    assert.equal(await page.locator('.selected-guide .technical-architecture:visible').count(), 2);
    assert.equal(await page.locator('.selected-guide .deployment-notes[open]').count(), 2);
    assert.equal(await page.locator('.solution-page:visible').count(), 0);
    assert.equal(await page.locator('.plan-only li:visible').count(), 10);
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    await page.emulateMedia({ media: 'screen' });
    assert.equal(await page.locator('html').getAttribute('data-print-plan'), null);
    assert.equal(await page.locator('.selected-guide').first().getAttribute('open'), '');
    assert.equal(await page.locator('.selected-guide').last().getAttribute('open'), null);
    await page.getByRole('button', { name: 'Remove Enterprise Knowledge from shortlist', exact: true }).click();
    assert.equal(await page.locator('.shortlist-item').count(), 1);
    await page.locator('#clear-shortlist').click();
    assert.equal(await page.locator('.shortlist-item').count(), 0);
    await page.locator('#reset-filters').click();
    await page.locator('.candidate[data-id="1"] .detail-button').click();
    await page.locator('[data-select="1"]').click();
    await page.locator('#solution-1 a[href="#shortlist"]').click();
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('.shortlist-item').count(), 0);
  });

  await run('the toolkit allows all 20 starting points in one shortlist without treating selection as deployment', async () => {
    for (const candidate of catalogCandidates) {
      await goView(page, 'catalog');
      await page.locator(`.candidate[data-id="${candidate.id}"] .detail-button`).click();
      await page.locator(`[data-select="${candidate.id}"]`).click();
    }
    await page.locator('.active-solution a[href="#shortlist"]').click();
    assert.equal(await page.locator('.shortlist-item').count(), 20);
    assert.equal(await page.locator('[data-select][aria-pressed="true"]').count(), 20);
    assert.match(await page.locator('#shortlist-count').innerText(), /20 solutions selected for planning/);
    assert.match(await page.locator('#shortlist > p').nth(1).innerText(), /unresolved gates/);
    await page.locator('#clear-shortlist').click();
    assert.equal(await page.locator('.shortlist-item').count(), 0);
  });

  await run('starter pilots build a gated printable pilot without adding extensions or losing selections', async () => {
    await page.goto(`${url}/?scoutTheme=light#program`, { waitUntil: 'networkidle' });
    await page.locator('[data-plan-pathway="answers"]').click();
    assert.equal(await page.locator('#shortlist-title').evaluate((node) => node === document.activeElement), true);
    assert.equal(await page.locator('.shortlist-item').count(), 1);
    assert.match(await page.locator('#pilot-brief').textContent(), /Trusted answers.*pilot brief/s);
    assert.match(await page.locator('#pilot-brief').textContent(), /baseline.*target.*named owners/s);
    assert.equal(await page.locator('[data-select="4"]').getAttribute('aria-pressed'), 'false');
    await goView(page, 'guide');
    await page.locator('[data-plan-pathway="answers"]').click();
    assert.equal(await page.locator('.shortlist-item').count(), 1, 'Repeated planning must not duplicate selections');
    await goView(page, 'guide');
    await page.locator('[data-plan-pathway="modernize"]').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('.shortlist-item').count(), 2);
    assert.match(await page.locator('#pilot-brief').textContent(), /no longer maintained/);
    assert.match(await page.locator('#pilot-plan-status').textContent(), /Existing shortlist entries retained/);
    await goView(page, 'guide');
    await page.locator('[data-plan-pathway="documents"]').click();
    assert.equal(await page.locator('.shortlist-item').count(), 3);
    assert.equal(await page.locator('[data-select="12"]').getAttribute('aria-pressed'), 'false');
    assert.match(await page.locator('#pilot-brief').textContent(), /missed evidence/);
    const ids = await page.locator('[id]').evaluateAll((nodes) => nodes.map((node) => node.id));
    assert.equal(ids.length, new Set(ids).size);
    await audit(page);
    await page.evaluate(() => { window.print = () => window.dispatchEvent(new Event('beforeprint')); });
    await page.locator('#print-plan').click();
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('#pilot-brief').isVisible(), true);
    assert.equal(await page.locator('#program').isVisible(), false);
    assert.equal(await page.locator('.plan-only li:visible').count(), 10);
    assert.equal(await page.locator('#plan-solution-9-review-title').isVisible(), true);
    await screenshot(page, 'pilot-selected-print.png', true);
    await page.emulateMedia({ media: 'screen' });
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    await page.getByRole('button', { name: 'Remove Content Processing from shortlist', exact: true }).click();
    assert.equal(await page.locator('#pilot-brief').isVisible(), false);
    assert.equal(await page.locator('.shortlist-item').count(), 2);
    assert.match(await page.locator('#pilot-plan-status').textContent(), /starting candidate was removed/);
    await goView(page, 'guide');
    await page.locator('[data-plan-pathway="answers"]').click();
    await page.locator('.candidate[data-id="1"] .detail-button').click();
    await page.locator('[data-select="1"]').click();
    await page.locator('#solution-1 a[href="#shortlist"]').click();
    assert.equal(await page.locator('#pilot-brief').isVisible(), false);
    await page.locator('#clear-shortlist').click();
    assert.equal(await page.locator('.shortlist-item').count(), 0);
    await goView(page, 'guide');
    await page.locator('[data-plan-pathway="answers"]').click();
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('#pilot-brief').isVisible(), false);
    assert.equal(await page.locator('.shortlist-item').count(), 0);
    assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length]), [0, 0]);
  });

  await run('catalog decisions are accessible, readable on mobile and restore disclosure state after printing', async () => {
    await page.goto(`${url}/?scoutTheme=light#selection-review`, { waitUntil: 'networkidle' });
    const review = page.locator('.catalog-review');
    await review.locator('summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await review.locator('tbody tr').count(), 15);
    const viewport = page.viewportSize();
    for (const theme of ['light', 'dark']) {
      if (await page.locator('html').getAttribute('data-theme') !== theme) await page.locator('#theme-toggle').click();
      await page.setViewportSize({ width: 320, height: 850 });
      await assertNoOverflow(page);
      await audit(page);
      await screenshot(page, `catalog-decisions-mobile-${theme}.png`);
    }
    await review.locator('summary').click();
    await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
    assert.equal(await review.getAttribute('open'), '');
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    assert.equal(await review.getAttribute('open'), null);
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    await page.locator('#theme-toggle').click();
    await page.setViewportSize(viewport);
    await goView(page, 'catalog');
  });

  await run('solution links support keyboard, section deep links, history and individual printing', async () => {
    const trigger = page.locator('.candidate[data-id="9"] .detail-button');
    await trigger.focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#solution-9-title').evaluate((node) => node === document.activeElement), true);
    await screenshot(page, 'modernize-experience-light.png', true);
    await page.locator('#solution-9 .solution-nav a[href="#solution-9-architecture"]').click();
    assert.equal(await page.locator('#solution-9-architecture-title').evaluate((node) => node === document.activeElement), true);
    await page.goBack();
    await page.waitForFunction(() => location.hash === '#solution-9');
    await page.goForward();
    await page.waitForFunction(() => location.hash === '#solution-9-architecture');
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('#solution-9').isVisible(), true);
    assert.equal(await page.locator('#solution-9 .solution-nav [aria-current="location"]').textContent(), 'Architecture');
    await audit(page);
    await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('.solution-page:visible').count(), 1);
    assert.equal(await page.locator('#solution-9').isVisible(), true);
    assert.equal(await visible(page).count(), 0);
    assert.equal(await page.locator('#solution-9 .deployment-notes[open]').count(), 1);
    assert.equal(await page.locator('#solution-9 .connection-details[open]').count(), 1);
    await page.emulateMedia({ media: 'screen' });
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    assert.equal(await page.locator('#solution-9 .deployment-notes').getAttribute('open'), null);
    assert.equal(await page.locator('#solution-9 .connection-details').getAttribute('open'), null);
    await page.locator('#solution-9 .solution-back').click();
  });

  await run('implementation brief follows the shortlist, retains gates and prints without technical dossiers', async () => {
    await page.goto(`${url}/?scoutTheme=dark#capacity`, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('[data-view-link="guide"]').textContent(), 'How we help');
    assert.equal(await page.title(), 'How we help · AI Solutions Hub');
    assert.equal(await page.locator('.delivery-options article').count(), 2);
    assert.equal(await page.locator('#print-brief').isVisible(), false);
    assert.match(await page.locator('#implementation-count').textContent(), /No solutions selected/);
    assert.equal(await page.locator('#selection-review').getAttribute('open'), null);
    for (const id of [3, 9, 12]) {
      await goView(page, 'catalog');
      await page.locator(`.candidate[data-id="${id}"] .detail-button`).click();
      await page.locator(`[data-select="${id}"]`).click();
    }
    await goView(page, 'guide');
    await page.locator('#capacity a[href="#implementation-brief"]').click();
    assert.equal(await page.locator('#implementation-title').evaluate((node) => node === document.activeElement), true);
    assert.equal(await page.locator('#implementation-items > li').count(), 3);
    const brief = await page.locator('.implementation-brief').innerText();
    for (const id of [3, 9, 12]) assert.ok(brief.includes(candidates.find((item) => item.id === id).next));
    assert.ok(brief.includes(dossiers[3].privateSource));
    assert.ok(brief.includes(dossiers[9].sourceReview.summary));
    assert.match(brief, /Repository not verified/);
    assert.equal(await page.locator('#implementation-items .solution-body').count(), 0);
    assert.equal(await page.evaluate(() => {
      const ids = [...document.querySelectorAll('[id]')].map((node) => node.id);
      return ids.length === new Set(ids).size;
    }), true);
    await audit(page);
    await page.setViewportSize({ width: 320, height: 850 });
    await assertNoOverflow(page);
    await screenshot(page, 'implementation-brief-mobile.png', true);
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.evaluate(() => { window.print = () => window.dispatchEvent(new Event('beforeprint')); });
    await page.locator('#print-brief').click();
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('html').getAttribute('data-print-plan'), 'brief');
    assert.equal(await page.locator('[data-page]:visible').count(), 1);
    assert.equal(await page.locator('#implementation-items > li:visible').count(), 3);
    assert.equal(await page.locator('.brief-prompts').isVisible(), true);
    assert.equal(await page.locator('.selected-guide:visible, .solution-page:visible, #preparation:visible').count(), 0);
    await screenshot(page, 'implementation-brief-print.png', true);
    await page.emulateMedia({ media: 'screen' });
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    assert.equal(await page.locator('html').getAttribute('data-print-plan'), null);
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    assert.equal(await page.locator('#preparation').getAttribute('open'), null);
    await page.locator('#implementation-brief a[href="#shortlist"]').click();
    await page.getByRole('button', { name: 'Remove Modernize from shortlist', exact: true }).click();
    assert.equal(await page.locator('#implementation-items > li').count(), 2);
    assert.doesNotMatch(await page.locator('#implementation-items').textContent(), /Maintenance:/);
    await page.locator('#clear-shortlist').click();
    assert.equal(await page.locator('#implementation-items > li').count(), 0);
    await goView(page, 'guide');
    assert.equal(await page.locator('#print-brief').isVisible(), false);
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('#implementation-items > li').count(), 0);
  });

  await run('preparation and new-capacity guidance stay secondary and work by keyboard and deep link', async () => {
    await page.goto(`${url}/?scoutTheme=light#capacity`, { waitUntil: 'networkidle' });
    const preparation = page.locator('#preparation');
    await preparation.locator('summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#capacity-existing').isVisible(), true);
    assert.match(await preparation.innerText(), /persisted agent settings/);
    await page.keyboard.press('Space');
    assert.equal(await page.locator('#capacity-existing').isVisible(), false);
    await page.goto(`${url}/?scoutTheme=light#how-it-works`, { waitUntil: 'networkidle' });
    assert.equal(await preparation.getAttribute('open'), '');
    assert.equal(await page.locator('#how-it-works').isVisible(), true);
    await page.goto(`${url}/?scoutTheme=light#capacity-new`, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('#capacity-new').getAttribute('open'), '');
    assert.match(await page.locator('#capacity-new').innerText(), /actual demand.*Standard, Batch.*No fixed PTU quantity/s);
    await page.locator('#capacity-new summary').focus();
    await page.keyboard.press('Space');
    assert.equal(await page.locator('#capacity-new').getAttribute('open'), null);
    await screenshot(page, 'how-we-help-light.png');
  });

  await run('native FAQ and skip link are keyboard accessible', async () => {
    const faq = page.locator('.faq-list details').first();
    await faq.locator('summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await faq.getAttribute('open'), '');
    await page.keyboard.press('Space');
    assert.equal(await faq.getAttribute('open'), null);
    await audit(page);
    await page.goto(`${url}/?scoutTheme=light`, { waitUntil: 'networkidle' });
    await page.keyboard.press('Tab');
    assert.equal(await page.locator('.skip-link').evaluate((node) => node === document.activeElement), true);
    await page.keyboard.press('Enter');
    assert.equal(new URL(page.url()).hash, '#main');
    assert.equal(await page.locator('#main').evaluate((node) => node === document.activeElement), true);
    await goView(page, 'catalog');
    await page.locator('.skip-link').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('html').getAttribute('data-view'), 'catalog');
    assert.equal(await page.locator('#main').evaluate((node) => node === document.activeElement), true);
  });

  await run('dark mode, theme toggle, invalid overrides and system preferences behave correctly', async () => {
    await page.goto(`${url}/?scoutTheme=dark`, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    await assertTheme(page, 'dark');
    await audit(page);
    await assertNoOverflow(page);
    await screenshot(page, 'desktop-dark.png');
    await page.locator('#theme-toggle').click();
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.locator('#theme-toggle').click();
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    for (const view of ['guide', 'roadmap', 'catalog']) {
      await goView(page, view);
      await audit(page);
      await screenshot(page, `${view}-dark-full.png`, true);
    }
    await page.locator('.candidate[data-id="11"] .detail-button').click();
    await page.locator('#solution-11 .solution-actions .text-link').hover();
    assert.equal(await page.locator('#solution-11 .solution-actions .text-link')
      .evaluate((link) => getComputedStyle(link).color), 'rgb(253, 142, 161)');
    await audit(page);
    await screenshot(page, 'voice-detail-dark.png');
    await page.goto(`${url}/?scoutTheme=invalid`, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    await page.emulateMedia({ colorScheme: 'light' });
    await page.waitForFunction(() => document.documentElement.dataset.theme === 'light');
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.goto(`${url}/?scoutTheme=dark`, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
  });

  for (const theme of ['light', 'dark']) {
    await run(`320–1440px ${theme} layouts have no overflow and pass accessibility checks`, async () => {
      await page.goto(`${url}/?scoutTheme=${theme}`, { waitUntil: 'networkidle' });
      for (const view of ['overview', 'catalog', 'guide', 'roadmap']) {
        await goView(page, view);
        for (const width of [320, 375, 768, 1024, 1440]) {
          await page.setViewportSize({ width, height: 900 });
          await assertNoOverflow(page);
          if (view === 'overview') {
            const boxes = await page.locator('.top-pick').evaluateAll((nodes) =>
              nodes.map((node) => { const { x, y, width } = node.getBoundingClientRect(); return { x, y, width }; }));
            assert.equal(boxes.length, 6);
            const columns = new Set(boxes.map((box) => Math.round(box.x))).size;
            assert.equal(columns, width > 1100 ? 3 : width > 580 ? 2 : 1, `Top picks column count at ${width}px`);
            const hierarchy = await page.locator('.top-pick').evaluateAll((nodes) => nodes.map((node) => ({
              name: parseFloat(getComputedStyle(node.querySelector('strong')).fontSize),
              value: parseFloat(getComputedStyle(node.querySelector('.top-pick-value')).fontSize),
            })));
            assert.ok(hierarchy.every(({ name, value }) => name >= 20 && value <= 16 && name >= value * 1.4),
              'Solution names must be visibly larger than their value statements at every screen size.');
          }
        }
        await page.setViewportSize({ width: 375, height: 812 });
        await audit(page);
        await screenshot(page, `mobile-${view}-${theme}.png`);
        await screenshot(page, `mobile-${view}-${theme}-full.png`, true);
      }
      await goView(page, 'overview');
      await page.evaluate(() => window.scrollTo(0, 0));
      await assertTheme(page, theme);
      await audit(page);
      await screenshot(page, `mobile-${theme}.png`);
    });

    for (const id of [1, 3, 6, 9, 10, 16, 17, 21, 22]) {
      await run(`320–1440px ${theme} solution ${id} has no overflow and passes accessibility checks`, async () => {
      await page.goto(`${url}/?scoutTheme=${theme}`, { waitUntil: 'networkidle' });
      await page.setViewportSize({ width: 375, height: 812 });
      await goView(page, 'catalog');
      await page.locator('#view-switch [data-layout="list"]').click();
      await assertNoOverflow(page);
      await audit(page);
        await page.locator(`.candidate[data-id="${id}"] .detail-button`).click();
        for (const width of [320, 375, 768, 1024, 1440]) {
          await page.setViewportSize({ width, height: 900 });
          await assertNoOverflow(page);
        }
        await page.setViewportSize({ width: 375, height: 812 });
        await audit(page);
        const bounds = await page.locator(`#solution-${id}`).boundingBox();
        assert.ok(bounds.x >= 0 && bounds.width <= 375);
        await screenshot(page, `solution-${id}-mobile-${theme}.png`, true);
        if ([3, 9, 10, 17].includes(id)) {
          await page.setViewportSize({ width: 1440, height: 1000 });
          const chrome = page.locator('.site-header, .solution-nav, .skip-link');
          const hidden = await chrome.evaluateAll((nodes) => nodes.map((node) => node.hidden));
          try {
            await chrome.evaluateAll((nodes) => nodes.forEach((node) => { node.hidden = true; }));
            await page.locator(`#solution-${id} .technical-architecture`).screenshot({
              path: fileURLToPath(new URL(`architecture-${id}-${theme}.png`, results)),
              animations: 'disabled',
            });
          } finally {
            await chrome.evaluateAll((nodes, states) => nodes.forEach((node, index) => {
              node.hidden = states[index];
            }), hidden);
          }
          report.screenshots.push(`architecture-${id}-${theme}.png`);
          await page.setViewportSize({ width: 375, height: 812 });
        }
        await page.locator(`#solution-${id} .solution-back`).click();
      });
    }
  }

  await run('portfolio print includes all candidates and preparation without losing screen state', async () => {
    await page.goto(`${url}/?scoutTheme=dark#catalog`, { waitUntil: 'networkidle' });
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.locator('#catalog-search').fill('CWYD');
    assert.equal(await visible(page).count(), 2);
    // Mixed open/closed state must survive printing; all starting points print.
    await page.locator('.reference-disclosure').first().evaluate((detail) => { detail.open = true; });
    const printDisclosures = page.locator('.reference-disclosure');
    const disclosureState = await printDisclosures.evaluateAll((nodes) => nodes.map((node) => node.open));
    await goView(page, 'guide');
    await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.emulateMedia({ media: 'print' });
    assert.equal(await visible(page).count(), 20);
    assert.equal(await page.locator('#capacity-existing').isVisible(), true);
    assert.equal(await page.locator('#top').isVisible(), true);
    assert.equal(await page.locator('.roadmap-item:visible').count(), 5);
    assert.equal(await page.locator('.candidate-value:visible').count(), 20);
    assert.equal(await page.locator('.solution-page:visible').count(), 0);
    assert.equal(await page.locator('#catalog-filters').isVisible(), false);
    assert.equal(await page.locator('.top-pick:visible').count(), 6);
    assert.equal(await page.locator('.reference-disclosure[open]').count(), 4);
    await screenshot(page, 'print-summary.png', true);
    await page.emulateMedia({ media: 'screen' });
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    assert.equal(await page.locator('html').getAttribute('data-view'), 'guide');
    assert.deepEqual(await printDisclosures.evaluateAll((nodes) => nodes.map((node) => node.open)), disclosureState);
    assert.equal(await visible(page).count(), 0);
    await goView(page, 'catalog');
    assert.equal(await visible(page).count(), 2);
    await page.locator('#reset-filters').click();
    await page.locator('#view-switch [data-layout="grid"]').click();
  });

  await run('with JavaScript disabled all 20 cards and complete solution guides remain readable', async () => {
    const noJS = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' });
    await observeContext(noJS);
    const fallback = await noJS.newPage();
    await fallback.goto(url, { waitUntil: 'networkidle' });
    assert.equal(await visible(fallback).count(), 20);
    assert.equal(await fallback.locator('#catalog-filters').isVisible(), false);
    assert.equal(await fallback.locator('#capacity-existing').isVisible(), false);
    await fallback.locator('#preparation > summary').click();
    assert.equal(await fallback.locator('#capacity-existing').isVisible(), true);
    assert.equal(await fallback.locator('#capacity-new').isVisible(), true);
    assert.equal(await fallback.locator('[data-page]:visible').count(), 33);
    assert.equal(await fallback.locator('.pathway-card:visible').count(), 0);
    await fallback.locator('#program > summary').click();
    assert.equal(await fallback.locator('.pathway-card:visible').count(), 3);
    assert.equal(await fallback.locator('[data-plan-pathway]:visible').count(), 0);
    await fallback.locator('#selection-review > summary').click();
    await fallback.locator('.catalog-review summary').click();
    assert.equal(await fallback.locator('.catalog-review tbody tr:visible').count(), 15);
    assert.equal(await fallback.locator('#problem-chips').isVisible(), false);
    assert.equal(await fallback.locator('#problem-filter').isVisible(), false);
    assert.equal(await fallback.locator('#view-switch').isVisible(), false);
    assert.equal(await fallback.locator('.top-pick').count(), 6);
    await fallback.locator(`.top-pick a[href="#solution-${topPicks[0]}"]`).click();
    assert.equal(new URL(fallback.url()).hash, `#solution-${topPicks[0]}`);
    assert.equal(await fallback.locator('.workflow-showcase').isVisible(), true);
    assert.equal(await fallback.locator('.glossary-list').isVisible(), false);
    await fallback.locator('#glossary > summary').click();
    assert.equal(await fallback.locator('.glossary-list').isVisible(), true);
    await fallback.locator('[data-view-link="roadmap"]').click();
    assert.equal(await fallback.locator('#roadmap').isVisible(), true);
    await fallback.locator('.candidate[data-id="1"] .detail-button').click();
    assert.equal(new URL(fallback.url()).hash, '#solution-1');
    assert.equal(await fallback.locator('#solution-1 .workflow-steps').isVisible(), true);
    const detail = fallback.locator('#solution-1 .deployment-notes');
    await detail.locator('summary').click();
    assert.equal(await detail.locator('div').isVisible(), true);
    await noJS.close();
  });

  for (const theme of ['light', 'dark']) {
    await run(`use-case ideas: ${theme} customer content, keyboard disclosures and responsive accessibility`, async () => {
      await page.goto(`${url}/?scoutTheme=${theme}#roadmap`, { waitUntil: 'networkidle' });
      assert.equal(await page.title(), 'Use-case ideas · AI Solutions Hub');
      assert.equal(await page.locator('[data-view-link="roadmap"]').textContent(), 'Use-case ideas');
      assert.equal(await page.locator('.roadmap-item:visible').count(), 5);
      assert.equal(await page.locator('.roadmap-boundary:visible').count(), 5);
      assert.equal(await page.locator('#roadmap [data-select], #roadmap button').count(), 0);
      assert.doesNotMatch(await page.locator('#roadmap').innerText(), /Highest priority|Voice Live|Coming next/);
      assert.match(await page.locator('.roadmap-gate').innerText(), /No delivery dates/);
      for (const item of roadmap) {
        const idea = page.locator(`#idea-${item.id}`);
        assert.ok((await idea.innerText()).includes(item.audience));
        assert.ok((await idea.innerText()).includes(item.output));
        const detail = idea.locator('details');
        assert.equal(await detail.getAttribute('open'), null);
        await detail.locator('summary').focus();
        await page.keyboard.press('Enter');
        assert.ok((await detail.innerText()).includes(item.evaluation));
        assert.ok((await detail.innerText()).includes(item.gap));
      }
      for (const width of [320, 375, 768, 1024, 1440]) {
        await page.setViewportSize({ width, height: 900 });
        await assertNoOverflow(page);
      }
      await audit(page);
      await screenshot(page, `use-case-ideas-${theme}-expanded.png`, true);
      await page.setViewportSize({ width: 375, height: 812 });
      await audit(page);
      await screenshot(page, `use-case-ideas-${theme}-mobile.png`, true);
      await page.locator('.idea-actions .primary').click();
      assert.equal(await page.locator('#idea-discussion-title').evaluate((node) => node === document.activeElement), true);
      await page.locator('#idea-discussion a[href="#engagement"]').click();
      assert.equal(await page.locator('#engagement-title').evaluate((node) => node === document.activeElement), true);
      await page.goBack();
      await page.waitForFunction(() => location.hash === '#idea-discussion');
      assert.equal(await page.locator('html').getAttribute('data-view'), 'roadmap');
    });
  }

  await run('use-case ideas: related guides, deep links and printing preserve planning boundaries', async () => {
    await page.goto(`${url}/?scoutTheme=dark#idea-drafting`, { waitUntil: 'networkidle' });
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('html').getAttribute('data-view'), 'roadmap');
    for (const item of roadmap) {
      const detail = page.locator(`#idea-${item.id} details`);
      await detail.locator('summary').click();
      await detail.locator(`a[href="#solution-${item.related}"]`).click();
      assert.equal(await page.locator(`#solution-${item.related}`).isVisible(), true);
      await goView(page, 'roadmap');
    }
    await page.locator('#idea-drafting details summary').click();
    const state = await page.locator('.idea-detail').evaluateAll((nodes) => nodes.map((node) => node.open));
    await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('.idea-detail[open]').count(), 5);
    assert.equal(await page.locator('.roadmap-item:visible').count(), 5);
    assert.equal(await page.locator('.roadmap-boundary:visible').count(), 5);
    assert.equal(await page.locator('#idea-discussion').isVisible(), true);
    await page.emulateMedia({ media: 'screen' });
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    assert.deepEqual(await page.locator('.idea-detail').evaluateAll((nodes) => nodes.map((node) => node.open)), state);
    assert.equal(await page.locator('.shortlist-item').count(), 0);
    const noJS = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 375, height: 812 }, serviceWorkers: 'block' });
    await observeContext(noJS);
    const fallback = await noJS.newPage();
    await fallback.goto(`${url}/#roadmap`, { waitUntil: 'networkidle' });
    assert.equal(await fallback.locator('.roadmap-item:visible').count(), 5);
    await fallback.locator('#idea-drafting summary').click();
    assert.ok((await fallback.locator('#idea-drafting').innerText()).includes(roadmap[0].evaluation));
    await assertNoOverflow(fallback);
    await noJS.close();
  });

  for (let offset = 0; offset < candidates.length; offset += 5) {
    await run(`deployment guides: solutions ${offset + 1}-${offset + 5} mobile steps, sources and commands`, async () => {
      await page.setViewportSize({ width: 375, height: 812 });
      for (const item of candidates.slice(offset, offset + 5)) {
        await page.goto(`${url}/?scoutTheme=dark#solution-${item.id}-setup`, { waitUntil: 'networkidle' });
        const section = page.locator(`#solution-${item.id}-setup`);
        const guide = dossiers[item.id].deployment.walkthrough;
        assert.equal(await section.isVisible(), true);
        assert.equal(await section.locator('.setup-steps li').count(), 5);
        assert.ok((await section.locator('.deployment-verify').innerText()).includes(guide.verify));
        const manual = section.getByRole('link', { name: 'Open full deployment manual' });
        assert.equal(await manual.count(), guide.source ? 1 : 0);
        if (guide.source) assert.equal(await manual.getAttribute('href'),
          dossiers[item.id].sources.find((source) => source.id === guide.source).url);
        await section.locator('.deployment-runbook').evaluate((node) => { node.open = true; });
        for (const block of await section.locator('.command-disclosure').all()) {
          assert.equal(await block.getAttribute('open'), null);
          await block.evaluate((node) => { node.open = true; });
        }
        const checkout = section.locator('.deployment-checkout');
        if (await checkout.count()) {
          await checkout.evaluate((node) => { node.open = true; });
          assert.ok((await checkout.innerText()).includes(dossiers[item.id].revision));
        }
        for (const [, , command] of guide.steps) {
          if (command) assert.ok((await section.innerText()).includes(command));
        }
        await assertNoOverflow(page);
      }
    });
  }
  await run('deployment guides: accessibility, shared guidance, shortlist and print', async () => {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(`${url}/?scoutTheme=light#solution-1-setup`, { waitUntil: 'networkidle' });
    await page.reload({ waitUntil: 'networkidle' });
    await audit(page);
    await page.locator('#solution-1 .deployment-safety a').click();
    assert.equal(await page.locator('#preparation').getAttribute('open'), '');
    assert.equal(await page.locator('#deployment-safety').isVisible(), true);
    await page.goto(`${url}/#solution-1`);
    await page.locator('#solution-1 .shortlist-toggle').click();
    await page.goto(`${url}/#solution-3`);
    await page.locator('#solution-3 .shortlist-toggle').click();
    await page.goto(`${url}/#shortlist`);
    assert.equal(await page.locator('.selected-guide .deployment-walkthrough').count(), 2);
    assert.equal(await page.locator('.selected-guide .deployment-route a').count(), 1);
    await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('.selected-guide .deployment-checkout[open]').count(), 1);
    assert.equal(await page.locator('.selected-guide .deployment-verify:visible').count(), 2);
    await page.emulateMedia({ media: 'screen' });
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    const noJS = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 375, height: 812 }, serviceWorkers: 'block' });
    await observeContext(noJS);
    const fallback = await noJS.newPage();
    await fallback.goto(`${url}/#solution-1-setup`, { waitUntil: 'networkidle' });
    assert.equal(await fallback.locator('.deployment-walkthrough:visible').count(), 20);
    await fallback.locator('#solution-1 .deployment-runbook > summary').click();
    await fallback.locator('#solution-1 .deployment-checkout summary').click();
    assert.ok((await fallback.locator('#solution-1 .deployment-checkout').innerText()).includes(dossiers[1].revision));
    await assertNoOverflow(fallback);
    await noJS.close();
  });

  await run('customer journey: business fit to architecture, deployment requirements and an accurate implementation brief', async () => {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(`${url}/?scoutTheme=light#top`, { waitUntil: 'networkidle' });
    await page.reload({ waitUntil: 'networkidle' });
    await page.locator('.hero-capacity a').click();
    assert.equal(await page.locator('#capacity-new').getAttribute('open'), '');
    await page.locator('[data-view-link="catalog"]').click();
    await page.locator('.candidate[data-id="1"] .detail-button').click();
    const solution = page.locator('#solution-1');
    assert.equal(await solution.locator('.fit-detail').getAttribute('open'), null);
    assert.match(await solution.locator('.solution-provenance').innerText(), /Microsoft-owned public repository/);
    await solution.locator('.solution-decisions a').first().click();
    await solution.locator('#solution-1-workflow a[href="#solution-1-architecture"]').click();
    assert.equal(await solution.locator('.component-graph').isVisible(), true);
    await screenshot(page, 'customer-architecture-light.png');
    await solution.locator('.solution-decisions a').last().click();
    assert.equal(await solution.locator('.setup-prerequisites').isVisible(), true);
    assert.equal(await solution.locator('.setup-costs').isVisible(), true);
    assert.equal(await solution.locator('.deployment-runbook').getAttribute('open'), null);
    await screenshot(page, 'customer-requirements-light.png');
    await solution.locator('.deployment-runbook > summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await solution.locator('.setup-steps li:visible').count(), 5);
    await solution.locator('[data-discuss="1"]').click();
    assert.equal(await page.locator('#implementation-title').evaluate((node) => node === document.activeElement), true);
    const brief = page.locator('#implementation-items');
    assert.equal(await brief.locator('li').count(), 1);
    for (const value of [dossiers[1].ingestion.input, ...dossiers[1].deployment.prerequisites, ...dossiers[1].deployment.costs]) {
      assert.ok((await brief.innerText()).includes(value));
    }
    for (const id of [3, 12]) {
      await page.goto(`${url}/?scoutTheme=light#solution-${id}-setup`);
      await page.locator(`#solution-${id} [data-discuss]`).click();
    }
    assert.equal(await page.locator('.shortlist-item').count(), 3);
    assert.match(await brief.innerText(), /Private package - access required/);
    assert.match(await brief.innerText(), /Custom implementation required/);
    assert.equal(await page.locator('.selected-guide [data-discuss]').count(), 0);
    await page.goto(`${url}/?scoutTheme=light#solution-1-setup`);
    await solution.locator('[data-discuss="1"]').click();
    assert.equal(await page.locator('.shortlist-item').count(), 3, 'Planning twice must retain, not toggle or duplicate');
    assert.deepEqual(await page.evaluate(() => [...window.__discussClickRegistrations].sort()),
      candidates.map((item) => String(item.id)).sort(), 'Each planning action is wired once, not on every shortlist update');
    await audit(page);
  });

  await run('customer journey: mobile dark-theme overview, requirements and runbook deep links', async () => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(`${url}/?scoutTheme=dark#solution-6`, { waitUntil: 'networkidle' });
    await page.reload({ waitUntil: 'networkidle' });
    await assertNoOverflow(page);
    await audit(page);
    await screenshot(page, 'customer-solution-mobile-dark.png');
    await page.locator('#solution-6 .solution-decisions a').last().click();
    await assertNoOverflow(page);
    await screenshot(page, 'customer-requirements-mobile-dark.png');
    await page.goto(`${url}/?scoutTheme=dark#solution-6-runbook`);
    assert.equal(await page.locator('#solution-6 .deployment-runbook').getAttribute('open'), '');
    assert.equal(await page.locator('#solution-6 .setup-steps li:visible').count(), 5);
    await page.goto(`${url}/?scoutTheme=dark#solution-6-plain`);
    assert.equal(await page.locator('#solution-6 .fit-detail').getAttribute('open'), '');
    await assertNoOverflow(page);
    await audit(page);
  });

  await run('visual showroom: responsive graphics and meaningful compact cards', async () => {
    for (const width of [320, 768, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto(`${url}/?scoutTheme=light#catalog`);
      await assertNoOverflow(page);
      const measurements = await page.locator('.candidate').evaluateAll((cards) => cards.map((card) => {
        const visual = card.querySelector('.solution-visual');
        const box = visual.getBoundingClientRect();
        return {
          id: card.dataset.id,
          words: card.innerText.trim().split(/\s+/).length,
          labelsFit: [...visual.querySelectorAll('.visual-flow li > span')].every((label) => {
            const rect = label.getBoundingClientRect();
            return rect.left >= box.left && rect.right <= box.right && label.scrollWidth <= label.clientWidth + 1;
          }),
        };
      }));
      assert.ok(measurements.every((item) => item.words <= 85), 'Visible cards must remain concise');
      assert.deepEqual(measurements.filter((item) => !item.labelsFit), [], 'Illustration labels must fit');
      await goView(page, 'overview');
      for (const link of await page.locator('.toolkit-grid a').all()) {
        const target = await link.getAttribute('href');
        await link.click();
        assert.equal(new URL(page.url()).hash, target);
        assert.equal(await page.locator(`${target} h2`).evaluate((node) => node === document.activeElement), true);
        await goView(page, 'overview');
      }
    }
  });
  await run('visual showroom: command and delivery disclosures support keyboard and complete printing', async () => {
    await page.goto(`${url}/?scoutTheme=light#solution-1-runbook`);
    const commands = page.locator('#solution-1 .command-disclosure');
    const first = commands.first();
    assert.equal(await first.getAttribute('open'), null);
    await first.locator('summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await first.locator('code').isVisible(), true);
    await page.keyboard.press('Enter');
    assert.equal(await first.getAttribute('open'), null);
    await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
    assert.equal(await commands.locator('code:visible').count(), await commands.count());
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    assert.equal(await first.getAttribute('open'), null);
    await page.goto(`${url}/?scoutTheme=dark#engagement`);
    const delivery = page.locator('.delivery-journey details').first();
    await delivery.locator('summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await delivery.locator('p').isVisible(), true);
    await audit(page);
    await page.emulateMedia({ reducedMotion: 'reduce' });
    const motion = await page.locator('.toolkit-grid a').first().evaluate((node) => getComputedStyle(node).transitionDuration);
    assert.equal(motion, '0s');
    await page.emulateMedia({ reducedMotion: 'no-preference' });
  });
  await run('brand assets: approved inline logos load in both themes without distortion or network calls', async () => {
    for (const theme of ['light', 'dark']) {
      for (const width of [320, 1440]) {
        await page.setViewportSize({ width, height: 1000 });
        await page.goto(`${url}/?scoutTheme=${theme}#top`);
        assert.equal(await page.locator(`.brand-${theme}:visible`).count(), 2);
        assert.equal(await page.locator(`.brand-${theme === 'light' ? 'dark' : 'light'}:visible`).count(), 0);
        const images = await page.locator('img').evaluateAll((nodes) => nodes.map((image) => ({
          loaded: image.complete && image.naturalWidth > 0,
          embedded: image.src.startsWith('data:image/png;base64,'),
          alternative: Boolean(image.alt),
        })));
        assert.ok(images.every((image) => image.loaded && image.embedded && image.alternative));
        await assertNoOverflow(page);
        await audit(page);
        await screenshot(page, `branded-overview-${width}-${theme}.png`);
        await goView(page, 'guide');
        const logo = page.locator('.platform-signature img');
        const ratio = await logo.evaluate((image) => {
          const box = image.getBoundingClientRect();
          return Math.abs(box.width / box.height - image.naturalWidth / image.naturalHeight);
        });
        assert.ok(ratio < 0.01, 'Keep the official logo aspect ratio');
        await assertNoOverflow(page);
        await audit(page);
        await screenshot(page, `branded-guide-${width}-${theme}.png`);
      }
    }
  });
  await run('product experience: organization-to-outcomes journey and branded navigation at every viewport', async () => {
    for (const theme of ['light', 'dark']) {
      for (const width of [320, 768, 1440]) {
        await page.setViewportSize({ width, height: 1000 });
        await page.goto(`${url}/?scoutTheme=${theme}#top`);
        assert.equal(await page.locator(`.site-header .brand-${theme}`).isVisible(), true);
        assert.equal(await page.locator('.header-plan').isVisible(), true);
        assert.equal(await page.locator('.showcase-tile:visible').count(), 3);
        assert.deepEqual(await page.locator('.adoption-map h3').allTextContents(),
          ['Your organization', 'Your AI toolkit', 'Success you can measure']);
        for (const link of await page.locator('.toolkit-grid a').all()) {
          const target = await link.getAttribute('href');
          await link.focus();
          await page.keyboard.press('Enter');
          assert.equal(new URL(page.url()).hash, target);
          assert.equal(await page.locator(target).isVisible(), true);
          await goView(page, 'overview');
        }
        const overlap = await page.locator('.site-header').evaluate((header) => {
          const items = [...header.querySelectorAll('.header-microsoft, .brand, nav, .theme-button, .header-plan')]
            .map((node) => node.getBoundingClientRect());
          return items.some((a, i) => items.slice(i + 1).some((b) =>
            Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1
            && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1));
        });
        assert.equal(overlap, false, `Header overlaps at ${width}px`);
        await assertNoOverflow(page);
        await audit(page);
        await page.evaluate(() => window.scrollTo(0, 0));
        await screenshot(page, `product-home-${width}-${theme}.png`);
      }
    }
  });
  await run('product experience: guided discovery preserves honest matches and catalog filter context', async () => {
    await page.goto(`${url}/?scoutTheme=light#top`);
    for (const key of Object.keys(problems)) {
      await page.locator(`[data-problem-link="${key}"]`).click();
      const expected = catalogCandidates.filter((item) => onboarding[item.id].problems.includes(key));
      assert.equal(new URL(page.url()).hash, '#finder-results');
      assert.equal(await page.locator('#finder-title').textContent(), problems[key]);
      assert.deepEqual(await page.locator('#finder-matches h4 a').allTextContents(), expected.slice(0, 3).map((item) => item.name));
      assert.match(await page.locator('#finder-status').textContent(), new RegExp(`^${expected.length} relevant`));
      await page.locator('#finder-results a[href="#catalog"]').click();
      assert.equal(await page.locator('#filter-context').textContent(), problems[key]);
      assert.equal(await visible(page).count(), expected.length);
      await page.locator('#reset-filters').click();
      assert.equal(await visible(page).count(), 20);
      await goView(page, 'overview');
      await page.locator('#finder-results a[href="#catalog"]').click();
      assert.equal(await visible(page).count(), expected.length, 'Returning to finder must restore its filter');
      await goView(page, 'overview');
    }
    await page.locator('#finder-title').scrollIntoViewIfNeeded();
    await screenshot(page, 'product-finder.png');
    await audit(page);
    await page.goto(`${url}/?scoutTheme=light#finder-results`);
    await page.reload();
    assert.equal(await page.locator('#start').isVisible(), true);
    assert.equal(await page.locator('#finder-results').isVisible(), false);
    await page.locator('.problem-link').first().click();
    assert.equal(await page.locator('#finder-title').evaluate((node) => node === document.activeElement), true);
  });
  await run('product experience: choose any combination without comparison, with accessible quick-save and planning', async () => {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(`${url}/?scoutTheme=light#catalog`);
    await page.reload();
    assert.equal(await page.locator('#planning-dock').isVisible(), false);
    assert.equal(await page.locator('[data-compare], #comparison, #dock-compare').count(), 0);
    assert.equal(await page.getByRole('button', { name: /^Compare / }).count(), 0);
    assert.equal(await page.locator('[data-quick-select]').count(), 20);
    await page.locator('[data-quick-select="3"]').click();
    assert.equal(await page.locator('#header-plan-count').textContent(), '1');
    assert.equal(await page.locator('[data-select="3"]').getAttribute('aria-pressed'), 'true');
    for (const item of candidates.filter((item) => item.id !== 3)) {
      await page.locator(`[data-quick-select="${item.id}"]`).click();
    }
    assert.equal(await page.locator('#header-plan-count').textContent(), '20');
    assert.equal(await page.locator('#dock-plan-count').textContent(), '20');
    assert.equal(await page.locator('#dock-summary').textContent(), '20 saved for your team');
    await page.locator('#planning-dock a[href="#shortlist"]').click();
    assert.equal(await page.locator('.shortlist-item').count(), 20);
    await audit(page);
    await screenshot(page, 'product-plan-desktop.png');
    await page.setViewportSize({ width: 320, height: 900 });
    await assertNoOverflow(page);
    await audit(page);
    await screenshot(page, 'product-plan-mobile.png');
    assert.equal(await page.locator('#planning-dock').isVisible(), true);
    await page.locator('.header-plan').click();
    await page.locator('#clear-shortlist').click();
    assert.equal(await page.locator('#planning-dock').isVisible(), false);
    await goView(page, 'catalog');
    assert.equal(await page.locator('[data-quick-select="3"]').getAttribute('aria-pressed'), 'false');
    await page.locator('[data-quick-select="1"]').click();
    await page.reload();
    assert.equal(await page.locator('#header-plan-count').textContent(), '0');
    assert.equal(await page.locator('#planning-dock').isVisible(), false);
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(`${url}/?scoutTheme=light#solution-1`);
    assert.equal(await page.locator('#solution-1 .solution-nav').evaluate((node) => getComputedStyle(node).position), 'sticky');
    await screenshot(page, 'product-solution-desktop.png', true);
  });
  await run('no JavaScript errors, CSP violations or external/unexpected resource requests occurred in any page', async () => {
    assert.deepEqual(report.errors, []);
    assert.deepEqual(report.cspViolations, []);
    assert.deepEqual(report.externalRequests, []);
    assert.deepEqual(report.unexpectedRequests, []);
  });
  assert.ok(passed > 0, 'No checks matched SITE_CHECK_FROM.');
  report.status = report.checkFrom ? 'selected-checks-passed' : 'passed';
} catch (error) {
  console.error(error);
  report.status = 'failed';
  report.failure = error.message;
  if (page && !page.isClosed()) {
    try { await screenshot(page, 'failure.png'); } catch { /* The report still records a browser/navigation failure. */ }
  }
  process.exitCode = 1;
} finally {
  try {
    if (browser) {
      await withDeadline(Promise.all(browser.contexts().map(async (context) => {
        await context.unrouteAll({ behavior: 'ignoreErrors' });
        await context.request.dispose();
        await context.close();
      })), 15_000, 'Graceful context cleanup timed out; terminating the owned test browser.');
      // For connect(), close() disconnects this client; it does not terminate the
      // launchServer process. Disconnect before stopping its WebSocket server.
      await withDeadline(browser.close(), 15_000, 'Browser client disconnect timed out.');
    }
  } catch (error) {
    report.cleanupWarning = error.message;
    console.warn(error.message);
  } finally {
    try {
      // Kill only the dedicated browser owned by this run, never a user's browser.
      // All screenshots and HEAD responses are already finished/disposed.
      await stopOwnedBrowser();
    } catch (error) {
      report.status = 'failed';
      report.cleanupFailure = error.message;
      console.error(error.message);
      process.exitCode = 1;
    }
    if (server) {
      server.closeAllConnections();
      await new Promise((resolveClose, reject) => server.close((error) => error ? reject(error) : resolveClose()));
    }
    report.finishedAt = new Date().toISOString();
    await writeFile(new URL('smoke-results.json', results), `${JSON.stringify(report, null, 2)}\n`);
    console.log(`Results: test-results/smoke/${mode}/smoke-results.json (screenshots alongside)`);
  }
}
const successful = ['passed', 'selected-checks-passed'].includes(report.status);
if (successful) console.log(`${passed} ${report.checkFrom ? 'selected ' : ''}browser checks passed on Chromium ${report.browser}. No external requests or private-file bodies retrieved.`);
// All reports are flushed and the owned browser is stopped. Close any remaining
// in-process driver sockets so this one-shot CLI cannot linger on Windows.
process.exit(successful ? 0 : 1);
