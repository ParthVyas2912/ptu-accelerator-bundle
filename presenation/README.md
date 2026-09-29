# Presentation materials

## What to share with customers

Everything you need for a customer conversation is in `customer/`:

| File | Use it for |
|------|------------|
| `PTU-Accelerator-One-Pager.docx` / `.pdf` | A single-page introduction to attach to an email or leave behind. |
| `PTU-Accelerator-Two-Pager.docx` / `.pdf` | The fuller overview: top picks, three starter pilots and all 20 solutions. |
| `PTU-Accelerator-Customer-Deck.pptx` / `.pdf` | A 14-slide, Microsoft-branded deck with speaker notes for a 20-30 minute meeting. |

All three present the PTU accelerator as one catalog of 20 Microsoft and Azure AI
solutions in customer-priority order (no bundles) and link to the AI Solutions Hub at
https://ai-solutions-hub-ca.azurewebsites.net/. Share the PDFs by default; the Office
files are for tailoring. They are subject to normal account-team approval and contain
only the same public-safe material as the website: business outcomes, generalized
readiness language and public links. They are a curated catalog, not an official
commercial SKU, and promise no delivery, funding or PTU compatibility.

### Rebuild the customer materials

All customer copy lives in `customer-content.cjs`. The build checks it against
`..\site\src\content.mjs` and `onboarding.mjs` and fails if the catalog order, top picks,
names or problem mappings drift from the website.

```powershell
Set-Location presenation
npm ci --ignore-scripts               # pptxgenjs for the deck
$env:NODE_PATH = (npm root -g)        # docx for the documents, e.g. npm install -g docx
npm run build:customer
npm run render:customer               # needs PowerShell 7 (pwsh); PDFs, length/overflow checks, customer-preview\ PNGs
```

`render-customer.ps1` uses installed desktop Word and PowerPoint through COM and fails
unless the one-pager is one page, the two-pager is two pages and the deck is 10-20 slides
with no text overflowing its box. Review `customer-preview\` visually before sharing.

`archive/` (ignored) holds superseded collateral from before the single catalog; do not
share it.

# Internal Microsoft briefing - 14 September 2026 (not for customers)

For the 2:00 PM internal discussion. These materials are **private**, not website
inputs or customer-approved collateral. No new inference, deployment, capacity
purchase or customer result is implied.

## Present

- `PTU-Accelerator-Internal-2026-09-14.pptx`: editable 16:9 deck, 13 main slides
  plus three appendix slides, with embedded speaker notes.
- `Talking-Points-2026-09-14.md`: opening, slide-by-slide script, safe website
  walkthrough, likely questions and closing asks.
- `PTU-Accelerator-Internal-2026-09-14.pdf`: slide-only offline backup.
- `preview/`: locally rendered slides for visual review.

Allow about 13 minutes for the main story, optionally two minutes for the static
website, then discussion. For a five-minute slot use slides 1, 3, 4, 8 and 13.
Use PowerPoint Presenter View to see notes. Open `..\site\dist\index.html` for the
locally rebuilt website; the hosted website requires separate publication.

The story starts with customer outcomes, shows what the bounded evaluation
established, distinguishes existing-PTU adoption from new-capacity qualification,
and ends with candidate-account nominations and named delivery roles. No customer
savings, revenue forecast, fixed PTU quantity or production readiness is claimed.
The 30-day sequence is a proposed qualification sprint, not a delivery commitment.

## Rebuild locally

Requires Node.js and the pinned local generator. Rendering uses installed desktop
PowerPoint through COM; it does not send documents to an online conversion service.
```powershell
Set-Location presenation
npm ci --ignore-scripts
npm run build
.\render-deck.ps1
python verify-deck.py
```

Generated presentation/PDF binaries and preview/QA outputs are kept local and
ignored. Authored generation source and talking points are private repository
material. Never copy this directory into `site/` or its deployment artifact.

Source of interpretation: `..\PTU-Bundle-Commercial-Recommendation.md`, dated
12 September 2026, which qualifies earlier reports. Selected factual results are
grounded in `..\reports\ptu-bundle-evaluation.md`. References appear in the slide
notes and talking-points guide. Public product documentation cited by the
recommendation was not refreshed for this deck; recheck it when quoting.

`verify-deck.py` uses Pillow for local contact sheets and standard-library XML
checks for notes, text, sensitive-identifier exclusions and render coverage.
`qa/powerpoint-layout.json` contains native PowerPoint text-height and slide-bound
checks. Those checks supplement, rather than replace, visual review.
