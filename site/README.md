# PTU portfolio stakeholder website

An independent, public-safe explanation of three outcome bundles, 20 curated
candidates and five **planned** workflows. It is not an official product,
customer reference, production certification or support commitment.

## Stakeholder experience

- **Overview:** a spacious editorial introduction, a workflow → platform →
  capacity diagram, and three outcome-led bundle panels. Each panel shows a
  simple task-to-review pattern; native expanders reveal candidate starting
  points, evidence labels and planned work without repeating a full catalog.
- **Solutions:** an evidence-first library distinguishing readiness from PTU fit,
  20 candidate cards, outcome chips, readiness filters, search and a card/list
  toggle. “View details” exposes evidence, limitations, PTU fit and the next
  responsible step.
- **PTU guide:** distinct existing-capacity adoption/renewal and new-purchase
  decisions, three prerequisite checks, a connected human-review reference
  pattern, common questions, public references and printing.
- **Next steps:** controlled drafts receive a larger first-priority panel;
  the other four planned workflows remain clearly labeled with visible review
  boundaries. A development-path strip is explicitly not a delivery schedule
  or completion indicator. Voice Live BYOM stays a separate integration test.

### Design principles

The editorial layout uses bold Segoe UI typography, generous spacing, graphite
and warm-ivory surfaces drawn from the exact Clawpilot light/dark base tokens.
Semantic `--cp-action*` tokens select neutral foregrounds, buttons and panels;
the base rose tokens remain defined but are not used by website components.
Both light and dark views use this neutral treatment, including focus, selection,
navigation, filters, diagrams and native controls. No external illustration,
font, icon library, analytics or runtime dependency is required. The diagram is
semantic HTML and CSS; it explains a reference pattern, **not** a deployed stack.
PTUs, Standard and Batch are presented as legitimate choices, with compatible
model/API/geography routing and separate service costs stated alongside them.

Outcome panels replace the old three-column bundle cards; the roadmap separates
the first priority from subsequent work. The library still supports both dense
comparison via its list layout and browsing via cards. Progressive disclosure
does not hide roadmap safety boundaries or imply production readiness.
Neutral panels use opaque surfaces so their contrast does not depend on
whichever background sits behind them.

Navigation uses shareable hash links and supports browser Back/Forward. Filters,
layout and capacity selection persist while moving between views in the same
page; nothing is saved to browser storage. Press **/** outside a form field to
open and focus search; **Escape** clears the search text or closes an open dialog.
Selected navigation and filters are exposed to assistive technology. Without
JavaScript, the site remains one readable document with native anchors and
evidence expanders. Print restores all summary sections regardless of the
selected view, filters or layout. Printing temporarily opens all bundle
starting-point expanders, then restores their individual open/closed states.

## Build and preview

Requires Node.js 22 or newer. The site and build have **zero runtime dependencies**.
From this directory:

```powershell
npm run build
npm test
npm run preview
```

The preview is loopback-only and serves only the generated page. It applies the
same security headers as the generated Azure Static Web Apps configuration.
Stop it with Ctrl+C. Opening `dist/index.html` directly also works offline.

## Parent CI contract

The parent CI uses **Node.js 22**, with its working directory set to `site`:

```sh
npm ci --ignore-scripts
npm test && npm run build
```

`package-lock.json` is included and must stay alongside `package.json`, even
though there are no production dependencies. Test-tool versions are pinned.
Installation does not need lifecycle scripts, a browser download or cloud access.
`npm test` runs the Node-only artifact checks and builds its own fixtures, so it
also works before the explicit build step on a clean checkout. Browser checks
are separate and are not invoked by the parent's `npm test` command.

The build always writes to **`site/dist/`**, independent of the caller's working
directory. No private inputs or deployment secrets are build inputs.

## Full browser checks

Install the pinned development dependencies from the lockfile, then run:

```powershell
npm ci
npm run check
```

The browser suite uses Playwright Chromium matched to the pinned development
dependency. If that browser is unavailable, install it:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "0"
npx playwright install chromium
npm run test:browser
```

`PLAYWRIGHT_BROWSERS_PATH=0` keeps the browser download under the ignored
`node_modules/` subtree. The browser test sets this value automatically when running.

Browser and accessibility packages are development-only. Neither they nor their
code are included in the public output. The tests serve the built artifact locally,
do not click outbound links, and flag unexpected external page requests.

Tests cover:

- Byte-identical repeat builds; output-file and size budgets.
- All 20 candidates, all five planned workflows and material evidence caveats.
- Exact inline script/style hashes, restrictive CSP and public-content privacy checks.
- All bundle/readiness combinations, alias/detail search, literal malicious-looking
  input, zero results and reset.
- Four-view navigation, deep links, Back/Forward, focus transfer, search shortcuts,
  outcome chips, list/card layout and filter preservation between views.
- Reference-diagram structure and capacity alternatives; keyboard-operated bundle
  expanders; mobile workflow-column alignment and preserved heading line breaks.
- All 20 modal detail views, keyboard opening, focus containment, Escape and focus return.
- Radio-button capacity selection, native FAQ, readiness legend and skip navigation.
- Explicit light/dark query overrides (including the required snippet’s light
  precedence correction), system preference and manual switching.
- Automated axe WCAG 2.1 AA checks across all four views in light, dark and mobile,
  plus list layouts and modal details.
- Horizontal overflow checks across all four views at 320, 375, 768, 1024 and 1440 pixels.
- Print summary with all 20 candidates, both capacity options and all bundle
  starting points even when filtered; restores disclosure and theme state afterward.
- Graceful no-JavaScript reading with native evidence expanders.

Screenshots are generated in ignored `test-results/` for human visual inspection.
The local suite writes `test-results/smoke/local/`, including:

- `desktop-light.png` / `desktop-dark.png` — editorial hero and diagram.
- `overview-light-full.png` and `bundle-panels-light.png` — outcome panels.
- `{catalog,guide,roadmap}-{light,dark}-full.png` — complete secondary views.
- `mobile-{overview,catalog,guide,roadmap}-{light,dark}-full.png` — full 375px views.
- `voice-detail-{light,dark}.png`, `mobile-detail-{light,dark}.png` and
  `print-summary.png` — detail and print review.

These are review artifacts, not pixel-baseline assertions. Review the current
run’s JSON screenshot list, and visually inspect typography, diagram connectors,
small-screen wrapping and expanded content when changing layout rules.
Automated accessibility checks are not a claim of complete WCAG certification.
Before wider use, manually test with a screen reader (for example NVDA or VoiceOver)
and review in the browsers used by the intended audience.

## Reusable deployed-site smoke test

From `site/`, after the parent has published `dist/`:

```powershell
npm run test:smoke -- --url https://blue-beach-0fb8cd70f.5.azurestaticapps.net/
```

Or supply the target using an environment variable:

```powershell
$env:SITE_URL = "https://blue-beach-0fb8cd70f.5.azurestaticapps.net/"
npm run test:smoke
```

Equivalent Linux/GitHub Actions command, with `working-directory: site`:

```sh
SITE_URL="https://blue-beach-0fb8cd70f.5.azurestaticapps.net/" npm run test:smoke
```

The smoke test reuses the browser suite—no separate source review or copied test
logic is needed. With a URL it **does not build or start a local server**. Without a
URL it tests the existing local `dist/`. `--url` overrides `SITE_URL`; `--local`
explicitly selects local output even if `SITE_URL` is set.

```sh
npm run test:smoke -- --help
npm run test:smoke -- --local
```

The URL must be an HTTPS site origin, without credentials, query strings or
subpaths. HTTP is accepted only for loopback preview targets. Do not provide a
deployment token or an Azure/GitHub credential; none is needed.

On a fresh Linux browser-test runner, install the pinned dependencies and browser:

```sh
npm ci --ignore-scripts
PLAYWRIGHT_BROWSERS_PATH=0 npx playwright install --with-deps chromium
npm run test:smoke -- --url https://blue-beach-0fb8cd70f.5.azurestaticapps.net/
```

This browser preparation is **separate** from the parent's Node-only
`npm test && npm run build` contract. `npm ci` can remove an earlier local browser
download; use the documented installation command if the browser test reports a
missing executable.

### Smoke coverage and results

- Checks the delivered HTTP CSP hashes against the actual delivered inline
  CSS/JavaScript, plus security headers and the public-content privacy rules.
- Verifies rendered Clawpilot theme tokens, applied body colors, typography,
  card shape, explicit light/dark overrides and theme switching.
- Exercises all 20 candidates, all bundle/readiness combinations, search, empty
  state, capacity radios, keyboard navigation, all 20 dialogs, Escape and focus return.
- Checks 320–1440px reflow, light/dark/mobile/modal automated accessibility, printing
  and no-JavaScript reading.
- Uses **HEAD only**, without following redirects or reading response bodies, for
  a fixed set of source/private paths and an unknown route. Those paths must return
  401/403/404/410; even a 200 index fallback is a failure.
- Blocks and fails any unexpected external or same-origin resource/API request;
  external documentation and GitHub links are checked but never followed.

Exit **0** means all checks passed. A nonzero exit means unavailable, not yet
deployed, or a failed check—it never silently treats a placeholder page as success.
The report distinguishes passed checks from failures; later checks are not claimed
as passed after an early failure.

Outputs stay ignored and outside the deploy artifact:

```text
test-results/smoke/local/
test-results/smoke/deployed/
  smoke-results.json
  desktop-light.png
  desktop-dark.png
  mobile-light.png
  mobile-dark.png
  ...catalog, dialog, print and failure screenshots as applicable
```

The JSON report records the target, browser version, individual check results,
theme measurements, viewport checks, HEAD statuses, request/CSP/error observations
and screenshots generated in that run. It contains no downloaded private-file
bodies. Use its screenshot list rather than assuming every image left in the
directory belongs to the latest run. Do not publish either result directory.

## Public deploy boundary

**Publish only the contents of `site/dist/`.** The build produces exactly:

```text
dist/
  index.html
  staticwebapp.config.json
```

The build explicitly reads only its named public source files; there is no
recursive copy from the project root. It fails closed if `dist/` is a link or
contains unexpected files, directories or links. It does not read or delete
unexpected content. There is no SPA navigation fallback or error rewrite that
maps unknown paths to the public page. The deployed smoke test checks this
boundary independently using HEAD requests.

The parent workflow handles Azure Static Web Apps **Free** deployment in
**East US 2 (`eastus2`)**, the selected deployment region because Canada is
unavailable for the parent's SWA deployment. This hosting choice is not a
statement about model deployment geography or Canadian data residency.

Keep the deployment token in a **GitHub Actions secret**, used only by the parent
deployment step. Never put it in this subtree, browser code, build output or
workflow logs. Deploy only `site/dist/`, with no API directory and no additional
build or transformation of the already-hashed HTML.

This project does not deploy, create a repository, commit, push or configure cloud
resources. No Azure identifiers or credentials are required to build or read it.

The page is a single self-contained HTML file with inline CSS and JavaScript.
There are no external fonts, scripts, stylesheets, images, model calls, API calls,
analytics, cookies or browser-storage dependencies. Outbound links navigate only
when selected by a reader. The GitHub link points exactly to
`https://github.com/ParthVyas2912/ptu-accelerator-bundle` and explicitly notes that
granted contributor access is required.

### Security configuration

The build hashes the exact normalized UTF-8 contents of both script blocks and
the style block using SHA-256. It generates a matching HTTP CSP in
`staticwebapp.config.json`, plus a meta CSP for local-file use. The HTTP-only
`frame-ancestors 'none'` directive is intentionally absent from the meta policy.

The policy denies connections, images, fonts, frames/objects, form submission,
inline event handlers and unapproved scripts/styles. No `unsafe-inline`, eval,
dynamic HTML insertion or broad source wildcard is needed. Additional headers
include no-referrer, nosniff, DENY framing, a restrictive Permissions Policy,
HSTS and same-origin isolation boundaries. The file is revalidated rather than
cached indefinitely.

Rebuild after any source change. Do not edit or minify the output after hashing.
Deploy `index.html` and its generated configuration together. The hosting
platform’s final header behavior must be checked by the deployment owner.
Public-content scans are defense in depth, not a replacement for editorial review.

## Files and maintenance

| File | Purpose |
| --- | --- |
| `package.json`, `package-lock.json` | Node 22 scripts and reproducible development dependency lock |
| `src/content.mjs` | Curated public-safe data; 20 candidates and five planned workflows |
| `src/index.html` | Semantic structure and explanatory content |
| `src/styles.css` | Exact Clawpilot base tokens, responsive layouts and print rules |
| `src/theme.js` | Required first theme snippet plus explicit valid override correction |
| `src/app.js` | Hash navigation, search, outcome chips, filters, layouts, radio choices, theme and modal details |
| `scripts/build.mjs` | Deterministic HTML renderer and CSP generator |
| `scripts/serve.mjs` | Fixed-route, loopback-only preview |
| `tests/build.test.mjs` | Artifact, privacy, content and security-policy contracts |
| `tests/browser.mjs` | Functional, automated accessibility and screenshot checks |
| `tests/smoke-options.mjs` | URL/environment selection and smoke CLI help |
| `tests/public-contract.mjs` | Shared public-content, delivered-CSP and HEAD-path contracts |

Only hand-curated, public-safe summaries belong in source. The build does not read
parent directories, reports, evidence, logs, deployment configuration or environment
secrets. Do not add source artifacts or private material to `dist/`.

Evidence snapshot: **12 September 2026**. Future content changes should preserve
the distinction between selected test results, untested integrations, proposed
workflows and production readiness. In particular:

- Voice Live’s documented PTU BYOM path is conditional and untested here, not
  categorically excluded. Speech fees are separate.
- Controlled drafts are a new implementation, not the compiled marketing repository.
- Reserved capacity does not itself improve answer quality.
- Existing-capacity adoption/renewal and new-purchase justification are different decisions.
- Standard and Batch remain legitimate alternatives.

Official public references:

- https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput
- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-bring-your-own-model
