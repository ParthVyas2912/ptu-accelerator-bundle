import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { startServer } from '../scripts/serve.mjs';
import { bundles, candidates, statuses } from '../src/content.mjs';
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
const run = async (name, action) => {
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
  await page.screenshot({ path: fileURLToPath(new URL(name, results)), fullPage, animations: 'disabled' });
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
      heroEmphasis: getComputedStyle(document.querySelector('.hero h1 span')).color,
      panelBackground: getComputedStyle(document.querySelector('.map-work')).backgroundColor,
      background: body.backgroundColor,
      font: body.fontFamily,
      cardRadius: getComputedStyle(document.querySelector('.candidate')).borderRadius,
      catalogDisplay: getComputedStyle(document.querySelector('.catalog-grid')).display,
    };
  });
  assert.equal(actual.theme, theme);
  assert.equal(actual.backgroundToken, theme === 'light' ? '#f7f4ef' : '#3d3b3a');
  assert.equal(actual.accentToken, theme === 'light' ? '#b11f4b' : '#fd8ea1');
  assert.equal(actual.actionToken, theme === 'light' ? '#242424' : '#dedede');
  assert.equal(actual.primaryBackground, theme === 'light' ? 'rgb(36, 36, 36)' : 'rgb(222, 222, 222)');
  assert.equal(actual.primaryForeground, theme === 'light' ? 'rgb(247, 244, 239)' : 'rgb(61, 59, 58)');
  assert.equal(actual.heroEmphasis, actual.primaryBackground);
  assert.equal(actual.panelBackground, theme === 'light' ? 'rgb(245, 245, 245)' : 'rgb(46, 46, 46)');
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
  page = await context.newPage();

  await run('served CSP allows the self-contained overview, retains 20 candidates and honors explicit light over dark OS', async () => {
    const response = await page.goto(`${url}/?scoutTheme=light`, { waitUntil: 'networkidle' });
    assert.equal(response.status(), 200, 'Site is unavailable or not deployed: expected HTTP 200.');
    assert.equal(await page.locator('.candidate').count(), 20, 'Expected the PTU portfolio. Publish site/dist/ before running the deployed smoke test.');
    assert.equal(await visible(page).count(), 0, 'The overview should not overwhelm readers with the full catalog.');
    assert.equal(await page.locator('#top').isVisible(), true);
    assert.equal(await page.locator('#bundles').isVisible(), true);
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

  await run('portfolio diagram explains the layers and bundle starting points disclose by keyboard', async () => {
    await goView(page, 'overview');
    const map = page.locator('.portfolio-map');
    assert.equal(await map.locator('.map-layer').count(), 3);
    assert.deepEqual(await map.locator('.capacity-routes strong').allTextContents(), ['PTUs', 'Standard', 'Batch']);
    assert.match(await map.textContent(), /model, API & geography compatibility/);
    assert.match(await map.locator('.map-footnote').textContent(), /not a deployed stack.*separate costs/);
    const disclosures = page.locator('.bundle-inventory');
    assert.equal(await disclosures.count(), 3);
    for (const detail of await disclosures.all()) {
      assert.equal(await detail.getAttribute('open'), null);
      await detail.locator('summary').focus();
      await page.keyboard.press('Enter');
      assert.equal(await detail.locator('div').isVisible(), true);
      await assertNoOverflow(page);
      await audit(page);
      await page.keyboard.press('Space');
      assert.equal(await detail.getAttribute('open'), null);
    }
    await page.locator('#bundles').scrollIntoViewIfNeeded();
    await screenshot(page, 'bundle-panels-light.png');
    await goView(page, 'catalog');
    assert.match(await page.locator('.evidence-key').textContent(), /Readiness.*PTU fit.*not a sizing result/);
    await goView(page, 'roadmap');
    assert.match(await page.locator('.roadmap-item').first().textContent(), /Highest priority.*Not deployed/);
    assert.equal(await page.locator('.roadmap-boundary:visible').count(), 5);
  });

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
      ['catalog', 'catalog'], ['candidate-title-11', 'catalog'], ['bundles', 'overview'],
      ['how-it-works', 'guide'], ['questions', 'guide'], ['sources', 'guide'], ['roadmap', 'roadmap'],
      ['unknown-section', 'overview'], ['%E0%A4%A', 'overview'],
    ]) {
      await page.goto(`${url}/?scoutTheme=light#${hash}`, { waitUntil: 'networkidle' });
      assert.equal(await page.locator('html').getAttribute('data-view'), view, hash);
    }
    await page.keyboard.press('/');
    assert.equal(await page.locator('html').getAttribute('data-view'), 'catalog');
    assert.equal(await page.locator('#catalog-search').evaluate((node) => node === document.activeElement), true);
    await page.keyboard.type('CWYD');
    assert.equal(await visible(page).count(), 1);
    await page.keyboard.press('Escape');
    assert.equal(await visible(page).count(), 20);
    assert.equal(await page.locator('#catalog-search').inputValue(), '');
  });

  await run('search works by aliases and detail text, stays literal and handles zero results', async () => {
    const search = page.locator('#catalog-search');
    await search.fill('CWYD');
    assert.equal(await visible(page).count(), 1);
    assert.equal(await visible(page).first().getAttribute('data-id'), '1');
    await search.fill('  BYOM  ');
    assert.equal(await visible(page).count(), 1);
    assert.equal(await visible(page).first().getAttribute('data-id'), '11');
    await search.fill('<img src=x onerror="window.searchInjected=true">');
    assert.equal(await visible(page).count(), 0);
    assert.equal(await page.locator('#empty-state').isVisible(), true);
    assert.equal(await page.locator('#result-count').textContent(), 'Showing 0 of 20 candidates');
    assert.equal(await page.evaluate(() => window.searchInjected), undefined);
    assert.equal(await page.locator('img').count(), 0);
    await page.locator('#clear-empty').click();
    assert.equal(await visible(page).count(), 20);
    assert.equal(await page.locator('#catalog-search').evaluate((node) => node === document.activeElement), true);
  });

  await run('every bundle and readiness combination returns exactly the matching cards', async () => {
    for (const bundle of ['all', ...Object.keys(bundles)]) {
      for (const status of ['all', ...Object.keys(statuses)]) {
        await page.locator(`[data-bundle-choice="${bundle}"]`).click();
        assert.equal(await page.locator('#bundle-filter').inputValue(), bundle);
        assert.equal(await page.locator(`[data-bundle-choice="${bundle}"]`).getAttribute('aria-pressed'), 'true');
        await page.locator('#status-filter').selectOption(status);
        const expected = candidates.filter((item) => (bundle === 'all' || item.bundle === bundle) && (status === 'all' || item.status === status)).map((item) => item.id);
        const actual = await visible(page).evaluateAll((nodes) => nodes.map((node) => Number(node.dataset.id)));
        assert.deepEqual(actual, expected, `${bundle} / ${status}`);
      }
    }
    await page.locator('#reset-filters').click();
    await goView(page, 'overview');
    await page.locator('[data-bundle-link="procurement"]').click();
    assert.equal(await page.locator('#bundle-filter').inputValue(), 'procurement');
    assert.equal(await visible(page).count(), 2);
    assert.equal(await page.locator('#catalog-search').evaluate((node) => node === document.activeElement), true);
    await page.locator('#catalog-search').fill('contract');
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
    await page.locator('[data-bundle-choice="engineering"]').click();
    await page.locator('#catalog-search').fill('Modernize');
    assert.equal(await visible(page).count(), 1);
    await goView(page, 'guide');
    await goView(page, 'catalog');
    assert.equal(await page.locator('#catalog-search').inputValue(), 'Modernize');
    assert.equal(await page.locator('#bundle-filter').inputValue(), 'engineering');
    assert.equal(await page.locator('#catalog-grid').getAttribute('data-layout'), 'list');
    assert.equal(await visible(page).count(), 1);
    await visible(page).locator('.detail-button').click();
    assert.equal(await page.locator('#candidate-dialog').isVisible(), true);
    await page.keyboard.press('Escape');
    await page.locator('#reset-filters').click();
    await audit(page);
    await screenshot(page, 'catalog-list-light.png');
    await page.locator('#view-switch [data-layout="grid"]').click();
    assert.equal(await page.locator('#view-switch [data-layout="grid"]').getAttribute('aria-pressed'), 'true');
  });

  await run('all 20 dialogs display the correct content and restore focus after Escape', async () => {
    for (const candidate of candidates) {
      const trigger = page.locator(`.candidate[data-id="${candidate.id}"] .detail-button`);
      await trigger.click();
      assert.equal(await page.locator('#candidate-dialog').isVisible(), true);
      assert.equal(await page.locator('#dialog-title').textContent(), candidate.name);
      assert.ok((await page.locator('#dialog-content').textContent()).includes(candidate.evidence));
      assert.ok((await page.locator('#dialog-content').textContent()).includes(candidate.ptu));
      assert.equal(await page.locator('#close-dialog').evaluate((node) => node === document.activeElement), true);
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('#candidate-dialog').isVisible(), false);
      assert.equal(await trigger.evaluate((node) => node === document.activeElement), true);
    }
  });

  await run('keyboard opens dialogs; modal focus stays contained; close button restores the opener', async () => {
    const trigger = page.locator('.candidate[data-id="11"] .detail-button');
    await trigger.focus();
    await page.keyboard.press('Enter');
    for (const key of ['Tab', 'Tab', 'Shift+Tab']) {
      await page.keyboard.press(key);
      assert.equal(await page.evaluate(() => document.querySelector('#candidate-dialog').contains(document.activeElement)), true);
    }
    await audit(page);
    await screenshot(page, 'voice-detail-light.png');
    await page.locator('#close-dialog').click();
    assert.equal(await trigger.evaluate((node) => node === document.activeElement), true);
  });

  await run('capacity choices work by keyboard and expose the correct decision boundary', async () => {
    await goView(page, 'guide');
    const existing = page.locator('input[value="existing"]');
    await existing.focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('input[value="new"]').isChecked(), true);
    assert.equal(await page.locator('#capacity-new').isVisible(), true);
    assert.equal(await page.locator('#capacity-existing').isVisible(), false);
    assert.match(await page.locator('#capacity-announcement').textContent(), /actual demand/);
    await page.keyboard.press('ArrowLeft');
    assert.equal(await existing.isChecked(), true);
    assert.equal(await page.locator('#capacity-existing').isVisible(), true);
    await screenshot(page, 'capacity-guide-light.png');
  });

  await run('native FAQ, readiness legend and skip link are keyboard accessible', async () => {
    const faq = page.locator('.faq-list details').first();
    await faq.locator('summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await faq.getAttribute('open'), '');
    await page.keyboard.press('Space');
    assert.equal(await faq.getAttribute('open'), null);
    await goView(page, 'catalog');
    const legend = page.locator('.legend');
    await legend.locator('summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await legend.getAttribute('open'), '');
    await audit(page);
    await legend.locator('summary').click();
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
    await audit(page);
    await screenshot(page, 'voice-detail-dark.png');
    await page.keyboard.press('Escape');
    await page.goto(`${url}/?scoutTheme=invalid`, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    await page.emulateMedia({ colorScheme: 'light' });
    await page.waitForFunction(() => document.documentElement.dataset.theme === 'light');
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.goto(`${url}/?scoutTheme=dark`, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
  });

  await run('320–1440px layouts have no overflow; mobile light and dark pass accessibility checks', async () => {
    for (const theme of ['light', 'dark']) {
      await page.goto(`${url}/?scoutTheme=${theme}`, { waitUntil: 'networkidle' });
      for (const view of ['overview', 'catalog', 'guide', 'roadmap']) {
        await goView(page, view);
        for (const width of [320, 375, 768, 1024, 1440]) {
          await page.setViewportSize({ width, height: 900 });
          await assertNoOverflow(page);
        }
        await page.setViewportSize({ width: 375, height: 812 });
        if (view === 'overview') {
          assert.equal(await page.locator('.bundle-card h3 br').evaluateAll((nodes) =>
            nodes.every((node) => getComputedStyle(node).display !== 'none')), true,
          'Do not concatenate sentences by hiding editorial line breaks on mobile.');
          const stepTops = await page.locator('.bundle-story').first().locator('.outcome-flow li')
            .evaluateAll((nodes) => nodes.map((node) => node.getBoundingClientRect().top));
          assert.ok(Math.max(...stepTops) - Math.min(...stepTops) < 1,
            'Mobile workflow steps should have aligned columns, not orphaned wrapped arrows.');
        }
        await audit(page);
        await screenshot(page, `mobile-${view}-${theme}.png`);
        await screenshot(page, `mobile-${view}-${theme}-full.png`, true);
      }
      await goView(page, 'overview');
      await page.evaluate(() => window.scrollTo(0, 0));
      await assertTheme(page, theme);
      await audit(page);
      await screenshot(page, `mobile-${theme}.png`);
      await goView(page, 'catalog');
      await page.locator('#view-switch [data-layout="list"]').click();
      await assertNoOverflow(page);
      await audit(page);
      await page.locator('.candidate[data-id="6"] .detail-button').click();
      await assertNoOverflow(page);
      const bounds = await page.locator('#candidate-dialog').boundingBox();
      assert.ok(bounds.x >= 0 && bounds.width <= 375);
      await audit(page);
      await screenshot(page, `mobile-detail-${theme}.png`);
      await page.keyboard.press('Escape');
    }
  });

  await run('print includes all candidates and both capacity paths without losing screen state', async () => {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.locator('#catalog-search').fill('CWYD');
    assert.equal(await visible(page).count(), 1);
    // Mixed open/closed state must survive printing; all starting points print.
    await page.locator('.bundle-inventory').first().evaluate((detail) => { detail.open = true; });
    const disclosureState = await page.locator('.bundle-inventory').evaluateAll((nodes) => nodes.map((node) => node.open));
    await goView(page, 'guide');
    await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.emulateMedia({ media: 'print' });
    assert.equal(await visible(page).count(), 20);
    assert.equal(await page.locator('#capacity-existing').isVisible(), true);
    assert.equal(await page.locator('#capacity-new').isVisible(), true);
    assert.equal(await page.locator('#top').isVisible(), true);
    assert.equal(await page.locator('.roadmap-item:visible').count(), 5);
    assert.equal(await page.locator('.candidate-summary:visible').count(), 20);
    assert.equal(await page.locator('#catalog-filters').isVisible(), false);
    assert.equal(await page.locator('.bundle-inventory[open]').count(), 3);
    assert.equal(await page.locator('.bundle-inventory > div:visible').count(), 3);
    await screenshot(page, 'print-summary.png', true);
    await page.emulateMedia({ media: 'screen' });
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    assert.equal(await page.locator('html').getAttribute('data-view'), 'guide');
    assert.deepEqual(await page.locator('.bundle-inventory').evaluateAll((nodes) => nodes.map((node) => node.open)), disclosureState);
    assert.equal(await visible(page).count(), 0);
    await goView(page, 'catalog');
    assert.equal(await visible(page).count(), 1);
    await page.locator('#reset-filters').click();
    await page.locator('#view-switch [data-layout="grid"]').click();
  });

  await run('with JavaScript disabled all 20 cards, both capacity paths and native details remain readable', async () => {
    const noJS = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' });
    await observeContext(noJS);
    const fallback = await noJS.newPage();
    await fallback.goto(url, { waitUntil: 'networkidle' });
    assert.equal(await visible(fallback).count(), 20);
    assert.equal(await fallback.locator('#catalog-filters').isVisible(), false);
    assert.equal(await fallback.locator('#capacity-existing').isVisible(), true);
    assert.equal(await fallback.locator('#capacity-new').isVisible(), true);
    assert.equal(await fallback.locator('[data-page]:visible').count(), 9);
    assert.equal(await fallback.locator('#bundle-chips').isVisible(), false);
    assert.equal(await fallback.locator('#view-switch').isVisible(), false);
    const bundleDetail = fallback.locator('.bundle-inventory').first();
    await bundleDetail.locator('summary').click();
    assert.equal(await bundleDetail.locator('div').isVisible(), true);
    assert.equal(await fallback.locator('.portfolio-map').isVisible(), true);
    await fallback.locator('[data-view-link="roadmap"]').click();
    assert.equal(await fallback.locator('#roadmap').isVisible(), true);
    const detail = fallback.locator('.candidate-fallback').first();
    await detail.locator('summary').click();
    assert.equal(await detail.locator('.detail-body').isVisible(), true);
    await noJS.close();
  });

  await run('no JavaScript errors, CSP violations or external/unexpected resource requests occurred in any page', async () => {
    assert.deepEqual(report.errors, []);
    assert.deepEqual(report.cspViolations, []);
    assert.deepEqual(report.externalRequests, []);
    assert.deepEqual(report.unexpectedRequests, []);
  });
  report.status = 'passed';
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
if (report.status === 'passed') console.log(`${passed} browser checks passed on Chromium ${report.browser}. No external requests or private-file bodies retrieved.`);
// All reports are flushed and the owned browser is stopped. Close any remaining
// in-process driver sockets so this one-shot CLI cannot linger on Windows.
process.exit(report.status === 'passed' ? 0 : 1);
