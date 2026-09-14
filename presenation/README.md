# Internal Microsoft briefing - 14 September 2026

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
