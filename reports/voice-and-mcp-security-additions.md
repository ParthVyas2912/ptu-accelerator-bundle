# Catalog additions 21–22: real-time voice agents and MCP security

**Date:** 16 September 2026
**Requested by:** portfolio owner, to extend the PTU enablement catalog from 20 to 22 candidates.
**Status of this record:** source review only. No deployment, no model request, no Azure mutation.

## Summary

Two public Azure-Samples repositories were added to the catalog. Both were cloned, pinned and
reviewed from source. Neither was deployed, and neither is claimed to have been functionally
tested.

| # | Name | Upstream | Pinned revision | License | Catalog status |
|---|---|---|---|---|---|
| 21 | Real-time voice agents (ART) | `Azure-Samples/art-voice-agent-accelerator` | `a2e1ce2edbf103661c56a861cccef73c30acacee` | MIT | Conditional / untested |
| 22 | MCP security workshop (Sherpa) | `Azure-Samples/sherpa` | `12be921ec85bd915105d9c6b5335cffe8c680966` | MIT | Conditional / untested |

Public status and license were confirmed on 16 September 2026 through read-only repository
metadata. Both are public, non-archived and MIT-licensed.

## Why these two are different from each other

They were requested together but they are not the same kind of asset, and the catalog should not
pretend otherwise.

**ART is an application accelerator** and is the single most PTU-relevant item in the portfolio.
It supplies the plumbing for real-time voice agents — telephony, bidirectional media streaming,
turn taking and orchestration — and allows the audio path to be selected by configuration between
a separated speech pipeline and the managed voice-to-voice service. This connects directly to the
existing "Voice Live on the customer's PTU model" priority, which documents a bring-your-own-model
route capable of using a customer's provisioned deployment.

**Sherpa is an enablement workshop**, not a deployable product. It teaches engineers to secure the
Model Context Protocol servers that agents use to reach tools and data. It consumes little or no
model capacity and must never be positioned as a capacity driver.

## Deployment assessment

The request included deploying both and leaving them running. Neither was deployed. The reasons
are specific, not precautionary.

### ART — blocked by cost and purchase requirements, not by difficulty

The reviewed Terraform definition provisions substantially more than a single application:

- Azure Managed Redis (Enterprise tier), default size `MemoryOptimized_M10`
- Cosmos DB for MongoDB vCore cluster, default `M30`
- Container registry, two container-app environments and five container apps
- Two App Service plans and two web apps
- Key Vault, App Configuration (Standard), Log Analytics, Application Insights, Event Grid
- Communication Services and Email Communication Services
- Model deployments whose checked-in capacity defaults are 150, 150, 100, 50 and 4

Three findings determine the outcome:

1. **There is no free configuration.** Managed Redis at the smallest supported size is
   **USD 0.23 per hour** (public retail rate, Canada Central, checked 16 September 2026). The
   Mongo vCore cluster, registry, container environments and App Service plans are additional and
   also have no free tier. The combined fixed hourly cost exceeds the `1.5` USD/hour review limits
   that govern comparable entries in the deployment contract.
2. **The default model capacities are far larger than an evaluation needs** — roughly five to
   fifteen times the capacity-10 deployments used elsewhere in this evaluation. Deploying the
   defaults unmodified would be a silent allowance increase.
3. **Telephony requires a purchase.** A usable PSTN number is acquired separately after
   provisioning and carries rental and per-minute charges. That is a purchasing decision.

Under the current contract, new billable infrastructure must be coordinated before creation, and
allowances are closed with no central reserve remaining. ART therefore cannot be deployed as part
of this change. It is recorded as prerequisite-gated.

**If it is later approved**, the minimum honest scope is: reduce every model capacity to the
smallest supported value, use the smallest Redis and cluster sizes, skip telephony for the first
pass and test the browser audio path only, and measure one call intent end to end including
interruptions and handoff. Budget approval should cover the whole stack, not only model usage.

### Sherpa — deliberately not deployed, for safety rather than cost

Sherpa ships intentionally vulnerable MCP servers alongside working exploit scripts; the starting
camp contains both a weak server and a hardened counterpart. Its documented method is to deploy
something insecure, attack it, fix it and re-test.

Standing that up in the shared MCAPS subscription would be an unnecessary and avoidable risk, and
it conflicts with the requirement that publicly reachable model-consuming routes be authenticated
or CIDR-restricted before exposure. The correct way to "run" this asset is a time-boxed session in
a disposable, isolated environment with no production connectivity, torn down immediately
afterwards. That is how it is described in the catalog.

## Why nothing was added to `adaptations/`

`adaptations/` preserves reviewed **adaptations** — patches and authored overlays — not upstream
repositories. No patch, overlay or authored source was produced for either repository, because
neither was built or run. Adding empty entries would also invalidate the existing archive
verification record, which hashes every archive file. Provenance for both is therefore recorded
where it is actually used: the pinned revisions in the public site's source references, and the
table above.

## What changed in the repository

- `site/src/onboarding.mjs` — two pinned public sources and problem mappings for 21 and 22.
- `site/src/content.mjs` — candidates 21 and 22.
- `site/src/dossiers.mjs` — full dossiers for 21 and 22, including component diagrams.
- `site/src/index.html`, `site/scripts/build.mjs` — candidate count 20 to 22.
- `site/tests/*` — count assertions updated; new evidence-phrase assertions for 21 and 22.
- `PTU-Bundle-Commercial-Recommendation.md` — ART added under the existing Voice Live priority; a
  new engineering-enablement subsection for Sherpa.

Historical statements were not rewritten. Section 4 still reads "all twenty original candidates",
because that verdict covered the original twenty; the dated talking points were left untouched.

## Honest status

- Selected tests passed: **none** for these two candidates.
- Source inspected: **both**, at the pinned revisions above.
- Deployed: **neither**.
- Prerequisite-gated: **ART**, pending explicit budget and capacity approval.
- Environment-restricted: **Sherpa**, pending a disposable isolated environment.

Source inspection is not a functional test. Nothing in this record should be cited as evidence
that either package works in this tenant.
