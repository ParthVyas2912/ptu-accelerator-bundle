# MACAE persistent cloud START / PAUSE / verification runbook

Scope: subscription `1feb53b2-854a-4ea7-b5a6-709b7d804f70`, app `ptu-macae`
in `rg-ptu-macae-demo`. No PTUs, new capacity, account keys, network changes,
protected resources, or ledger resets are authorized by this runbook.

Run from:
`C:\Users\partvyas\OneDrive - Microsoft\Desktop\projects\PTU accelerator Bundle`.
Use authenticated Azure CLI for control-plane operations; native cloud runtime
uses UAMI `id-ptu-macae`. Never save CLI bearer tokens, `.env`, connection
strings, registry passwords or credential exports to the bundle.

## Current state and call boundary

- Latest pinned backend: `acrptubundle7d804f70.azurecr.io/macae/backend@sha256:edb14961ca638605bc54a1f456e1f15ddf6b08eaabf977266b9f3df193b44ad9`.
- Frontend: `acrptubundle7d804f70.azurecr.io/macae/frontend@sha256:3e0c65062ff728b59fcf62e9935746174470344a3cdb886da83b91adac204d7a`.
- MCP: `acrptubundle7d804f70.azurecr.io/macae/mcp@sha256:ebf39b21927c0397035a14bac4dd941ca07dd819030985d270f3421e2306ea0b`.
- The original partial onboarding ran on eval2; the final advisory run used
  the current24-cap image on revision9 before pausing on revision10.
- **Cosmos ledger used24/limit24. No further attempts are available.**
- The fresh authorized two-specialist advisory run returned a genuine terminal
  error at the cap, not completed synthesis. Do not restart, resume or replay
  it. Old checkpoints were memory-only; current accounting must never reset.
- Limit24 was explicitly approved using two reclaimed Modernize attempts.
  Both migrations preserved all previously used records.
- Current parameter file leaves inferencefalse and min0/max1.
- Search Basic continues billing ~USD0.101/hour even when ACA is zero.
- START requests at most1vCPU/2GiB, fully active referenceUSD0.108/hour plus
  requests; shared ACR/PE/DNS and data/model charges are separate.

## Networking classification and current authorization

MACAE uses local MAF orchestration in ACA with prompt-agent definitions and
the project Responses API, **not Foundry custom-container Hosted Agents**.
HR/IT MCP runs client-side; native KB MCP runs as server-side Responses tools.
The Hosted-agent creation-time restriction does not establish mandatory
account recreation for this app.

Foundry private tool egress is unconfigured; exact existing-account enablement
is unverified. Official capability-host/customerSubnet and existing-project
modules are a conditional reuse candidate, not a ready-to-run fix. See
`evidence\macae\network-agent-type-correction.json` and the current report.
An inbound PE alone does not provide outbound tool routing.

The latest request authorized **read-only correction only**, not START, a
new subnet/capability host, RFP probes or more inference. The commands below
are persistent operational instructions for a separately authorized future
inspection; they were not run during this correction.

## START for inspection, without inference

```powershell
.\scripts\Set-MacaeCloudMode.ps1 -Mode Start
.\scripts\Invoke-MacaeCloudTest.ps1 -Action probe
.\scripts\Invoke-MacaeCloudTest.ps1 -Action ledger
```

START sets min1/max1 and **keeps live inference disabled**. It redeploys the
digest-pinned native three-container composition; it does not create another
environment, registry, network or model. Probe is zero-model: actual private
DNS, managed-identity data access and native frontend `/config`.

URL:
`https://ptu-macae.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`.
Only CIDR `174.112.74.34/32` is allowed. Cloud browser access returned403 in this
evaluation. Do not widen the rule or use an alternate public inference route.
Use authenticated `az containerapp exec` for the approved internal checks.
Native frontend auth is disabled for the restricted synthetic sample-user
evaluation; this configuration is not suitable for multi-user production.

**Do not run** the old full-onboarding `-Action plan` or reset/init the budget.
The native24-call gate is exhausted; EnableInference must refuse it.
Approval/clarification drivers only apply to a live native workflow, not to
an old transcript. No additional inference is authorized by this runbook.

The parent-approved12→22 and22→24 migrations already ran with identical
historical record hashes and used12 preserved at migration time. Their
historical admin commands are not general limit setters. Do not run old
`second-pass-admin`, initialization, advisory-plan or approval commands now.
Never modify the ledger directly to change its limit or usage.

## PAUSE / cloud STOP equivalent

```powershell
.\scripts\Set-MacaeCloudMode.ps1 -Mode Pause
.\scripts\Get-MacaeCloudState.ps1
```

PAUSE deploys min0/max1 and inferencefalse. Default scale cooldown is300seconds;
check again after that interval without issuing app requests. ARM state queries
do not intentionally wake the app. `cloud-final-state.json` reports actual
replica count, image digests, gate, CIDR, scale and local port listeners.
Zero replicas is the verification for no running app containers, not merely
min0. An allowed future HTTP request can still wake a min0 app, but the
persistent cap and disabled inference flag remain in force.

No resource is deleted. Search and shared platform fixed charges continue.
The old local backend/UI PID15244 and MCP PID13380 are stopped. Local
`Start-Macae.ps1` backend refuses while the cloud-budget marker exists; do not
remove that marker to run a second independent model ledger.

## Rebuild the disclosed evaluation image

**Latest advisory release:** ACR run `chs`,33seconds, produced the current
24-cap image. `Build-MacaeAdvisoryRemote.ps1` used six explicit files only.
The advisory team/request are saved under `test-data\macae`, and actual events
are in `evidence\macae\cloud-advisory-*.json`. The one-off build is complete;
do not blindly rerun or overwrite its tag.

**Latest native serializer fix:** ACR run `chn` remotely built a small patch
layer from the already verified official-backend-derived image.
`Build-MacaePatchRemote.ps1` records the six-file manifest and one corrected
retry; that one-off release/tag is complete and its retry is consumed. Use a
new reviewed release/tag for future changes, not another blind retry. Prefer
remote builds while local RAM is constrained. No `.env`, `.azure`, secrets,
internal docs or whole bundle were uploaded.

The older eval4 build recipe below describes its base image and does **not**
include the later native serializer patch. Do not replace the current pinned
digest with an unpatched eval4 build.

The three base images were built from the official Dockerfiles at
commit `8ac703a71f10b622bd3c82a9cc2b5dfe921c3025`.
Use `scripts/Build-MacaeImages.ps1` for the bounded official build procedure
and consult its parameters before running. Do not build the entire bundle.

For the thin final backend layer, the **three named contexts are required**:

```powershell
$root = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-container-source'
$data = (Resolve-Path '.\test-data\macae').Path
docker build --builder desktop-linux `
  --build-context "hrpack=$root\content_packs\hr_onboarding\agent_teams" `
  --build-context "indexscripts=$root\infra\scripts\post-provision" `
  --build-context "testdata=$data" `
  --file '.\scripts\macae-backend-eval.Dockerfile' `
  --tag acrptubundle7d804f70.azurecr.io/macae/backend:<NEW-ISOLATED-TAG> `
  '.\scripts'
```

Use a new isolated tag, authenticated Docker/Entra registry access, and pin
the resulting pushed digest in `scripts/macae-cloud.parameters.json`. Do not
overwrite the recorded historical tags/digests. The Dockerfile-specific
ignore file permits only the named metering/test files; named contexts supply
the official HR pack, official native indexer and two synthetic text files.
No credentials, `.env`, `.azure` or parent workspace are uploaded.

Then run the offline test before a **disabled** deployment:

```powershell
& 'C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\Multi-Agent-Custom-Automation-Engine-Solution-Accelerator\src\backend\.venv\Scripts\python.exe' '.\scripts\test_macae_cloud_budget.py'
.\scripts\Set-MacaeCloudMode.ps1 -Mode Pause
```

## Native ingestion and operational checks

`Invoke-MacaeCloudTest.ps1 -Action ingest` runs the official native indexer with
only its hardcoded credential constructor adapted to ManagedIdentityCredential.
It handles the two synthetic text files only; no embeddings/KB inference.
Both indexes and Blob objects already exist. Replay checks identical Blob
bytes and reuses document IDs; initial index visibility can be eventually
consistent. Do not mistake keyword retrieval for grounded agent reasoning.

Native MCP remains internal9000; backend8000; frontend3000. MCP uses
`UV_NO_SYNC=true` and TCP probes (official `/health` is404). Health routes
are not sufficient proof of dependency access or a completed workflow.

Console/system logs and durable model ledger can support manual diagnostics.
No durable alert channel, tested backup/restore or production rollback exists.
`Test-MacaeRelease.ps1` has opt-in image rollback with explicitly supplied
previous parameters, inferencefalse required;401/403 are access blockers,
not automatic rollback triggers. Never roll back models/data or weaken
ingress because a restricted client cannot reach the frontend.
