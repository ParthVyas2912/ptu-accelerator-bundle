# AI Solutions Hub

A problem-first catalog of Microsoft and Azure AI solution starting points: help teams discover relevant capabilities, shortlist candidates, and understand the architecture, source and prerequisites for an approved tenant pilot. Capacity planning follows the workload; it is not the selling proposition.

## [Open the stakeholder website](https://blue-beach-0fb8cd70f.5.azurestaticapps.net/)

Share that link with nontechnical colleagues after the reviewed website update is published. The source now provides six problem entry points, twenty candidates, a multi-solution shortlist and getting-started guidance without exposing this repository's private reports or environment details. Local changes do not update the hosted website until deployment.

**Private engineering workspace.** The stakeholder website is a separate, deliberately sanitized publication. This is not an official Microsoft commercial SKU, a production certification, or a commitment to support the included accelerators.

## Start here

| Audience | Read |
|---|---|
| Stakeholders | [Open the website](https://blue-beach-0fb8cd70f.5.azurestaticapps.net/), or build the self-contained website under [site](site/). |
| Account and solution teams | [Commercial recommendation](PTU-Bundle-Commercial-Recommendation.md): all twenty candidates, three proposed bundles and five priority additions. |
| DRDC account team | [Private DRDC Research Productivity Bundle](docs/DRDC-RESEARCH-BUNDLE.md): a proposed, research-focused composition and gated pilot plan; not public website content or a verified deployment. |
| Engineers | [First-pass evaluation](reports/ptu-bundle-evaluation.md), [continuation evaluation](PTU-Bundle-Continuation-Report.md), and [upstream adaptations](adaptations/README.md). |
| Contributors | [Contribution guide](CONTRIBUTING.md), [publication boundaries](docs/PUBLICATION.md), and [website operations](docs/WEBSITE-OPERATIONS.md). |

## Discover, choose, get started

The public-facing working brand is **AI Solutions Hub**, not an official Microsoft marketplace or commercial SKU. The catalog is curated, not an exhaustive list of Microsoft products.

Visitors choose a problem, compare outcomes and intended users, and open a full solution dossier with product-specific uses, actual workflows, component/connection diagrams, ingestion, deployment prerequisites and a scoped Microsoft specialist engagement. Public sources are pinned where a package is established; platform references and owner-led proposals are distinguished. Shareable section links replace modal dialogs. Visitors can shortlist multiple candidates and print a selected plan. Missing repositories, failed outcomes and custom-build requirements remain documented rather than becoming misleading deployment buttons.

The three existing areas remain useful groupings:

1. **Engineering Modernization** — code understanding, specifications and verified modernization.
2. **Knowledge and Staff Work** — trusted answers, document comparison and controlled drafting.
3. **Procurement and Document Operations** — document intake, evidence-backed review and missing-evidence checks.

Engineering comes first in the overview, problem entry points, area filters and catalog. Customer-facing cards emphasize value rather than lab status badges or readiness filters. Substantive limitations and the unchanged evaluation context live in each solution's deployment notes. Some selected workflows passed bounded tests; others remain partial, inspected only, blocked, or proposed. Dossiers replace synthetic mockups with descriptions of the real interface and workflow. Source inspection is not a functional test; proposed components and unresolved packages remain explicit.

The DRDC composition is a separate private research proposal. It does not publish meeting-derived information, assert customer endorsement, or authorize deployment. The two supplied AI summaries repeat the same material and require customer validation rather than being treated as independent corroboration.

**Current interpretation:** the commercial recommendation qualifies and corrects some earlier conclusions. In particular, Voice Live documents a customer-PTU BYOM path, but the lab did not test that path. Do not reuse historical categorical claims without those qualifications.

Historical report filenames, upstream revisions, repository URL and hosting resource names are retained for provenance. Rebranding the experience does not rewrite past evidence or rename infrastructure.

## Repository layout

| Path | Purpose |
|---|---|
| `site/` | Public-safe stakeholder experience, source, build and tests. Only its generated `dist/` directory is deployed. |
| `reports/`, `PTU-Bundle-*.md` | Internal evaluation reports, recommendations, cost methodology and runbooks. |
| `scripts/` | Evaluation harnesses, guards, deployment helpers and publication checks. Many historical scripts retain MCAPS-specific paths/settings. |
| `infra/` | Lab infrastructure definitions and the separate Free-tier stakeholder website template. |
| `evidence/` | Reviewed private lab evidence. Presence here is not permission to publish it to the website. |
| `test-data/`, `tests/` | Synthetic fixtures and existing evaluation checks. |
| `adaptations/` | Pinned upstream provenance, evaluation patches and authored source overlays instead of vendored dependency trees. |
| `docs/` | Publication policy, hosting metadata and operating instructions. |

## Safety and operating rules

- The site is informational: **no model API, inference credentials, live lab controls or paid-model calls**.
- Historical model allowances are closed. Cloning this repository does not authorize restarting inference, increasing quota, purchasing PTUs or deploying the lab.
- Preserve protected existing applications. Use the lab guard and explicit approvals for lab mutations.
- Synthetic MCAPS tests are not a DND deployment or accreditation. Private DNS and identity designs must be adapted to the approved customer landing zone.
- GitHub privacy does not make credential storage acceptable. Never commit keys, SAS tokens, passwords, personal records or original internal briefing inputs.
- Existing Word/PDF briefing inputs, generated Word exports, caches and operational logs remain local and are intentionally not part of the initial publication. Markdown reports are the reviewed source record.
- Accelerators, their service dependencies and individual model deployments have distinct costs and licenses. Purchasing PTUs does not make the rest of the stack free.

## Website development

Follow [site/README.md](site/README.md) for build and test commands. The production artifact is self-contained and contains only curated public-safe content.

GitHub Actions validates changes and deploys the site on `main` changes to the site or deployment workflow. Historical scripts are **not** automatically executed in CI. Infrastructure provisioning is a separate manual operation; site publishing cannot create or start model-consuming applications.

Six [starter issues](https://github.com/ParthVyas2912/ptu-accelerator-bundle/issues) define the next implementation priorities. Dependency-update pull requests remain subject to review; they are not automatically merged.

## Attribution and licensing

This is a private working collection, not a relicensing of Microsoft or Azure-Samples code. Preserve upstream licenses and notices recorded with each adaptation. Do not redistribute original internal inputs or imply support rights from source availability. No blanket open-source license is granted for the collection.
