# Working on this repository

- Read README.md and docs/PUBLICATION.md first.
- `site/` is public; everything else is private unless separately approved.
- Preserve the Clawpilot theme and keep the generated website self-contained, accessible and free of analytics/model calls.
- Never copy internal reports, resource identifiers, user data, credentials or raw evidence into the website.
- Do not execute historical deployment or inference scripts as a generic test suite.
- Existing allowances are closed; do not silently increase them, use protected applications, purchase capacity, relax network policy or delete resources.
- Keep upstream repositories pinned; store reviewed patches/overlays in `adaptations/`, not whole upstream dependency trees.
- After changes, run the smallest relevant tests, the publication scanner and the website build when applicable.
- Update claims conservatively: selected test pass, partial, inspected, prerequisite-gated and planned are different statuses.
- Avoid a blanket PTU guarantee: verify model/API/geography routing and distinguish model capacity from separately billed services.
