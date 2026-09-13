# PTU Accelerator Bundle

An evolving, evidence-led solution portfolio: help strategic customers adopt useful AI applications, then size the compatible Azure OpenAI provisioned capacity behind their actual demand.

**Private engineering workspace.** The stakeholder website is a separate, deliberately sanitized publication. This is not an official Microsoft commercial SKU, a production certification, or a commitment to support the included accelerators.

## Start here

| Audience | Read |
|---|---|
| Stakeholders | The deployed website listed in [deployment metadata](docs/website-deployment.json), or build the self-contained website under [site](site/). |
| Account and solution teams | [Commercial recommendation](PTU-Bundle-Commercial-Recommendation.md): all twenty candidates, three proposed bundles and five priority additions. |
| Engineers | [First-pass evaluation](reports/ptu-bundle-evaluation.md), [continuation evaluation](PTU-Bundle-Continuation-Report.md), and [upstream adaptations](adaptations/README.md). |
| Contributors | [Contribution guide](CONTRIBUTING.md), [publication boundaries](docs/PUBLICATION.md), and [website operations](docs/WEBSITE-OPERATIONS.md). |

## The proposed offer

1. **Knowledge and Staff Work** — trusted answers, document comparison and controlled drafting.
2. **Procurement and Document Operations** — document intake, evidence-backed review and missing-evidence checks.
3. **Engineering Modernization** — code understanding, specifications and verified modernization.

Readiness is intentionally explicit. Some selected workflows passed bounded tests; others remain partial, inspected only, blocked, or proposed. An application making model calls is not proof it is production-ready or economically suited to PTUs.

**Current interpretation:** the commercial recommendation qualifies and corrects some earlier conclusions. In particular, Voice Live documents a customer-PTU BYOM path, but the lab did not test that path. Do not reuse historical categorical claims without those qualifications.

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

## Attribution and licensing

This is a private working collection, not a relicensing of Microsoft or Azure-Samples code. Preserve upstream licenses and notices recorded with each adaptation. Do not redistribute original internal inputs or imply support rights from source availability. No blanket open-source license is granted for the collection.
