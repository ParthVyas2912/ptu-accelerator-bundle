# Modernize cloud fallback — start, inspect, evaluate, pause

This is an **adapted official-source cloud-container deployment**, not an
unchanged local/native deployment. Use only the approved lab subscription
`1feb53b2-854a-4ea7-b5a6-709b7d804f70`.

## Budget custody — closed

Parent update at **2026-09-11 22:42 EDT** reduced Modernize to **10 total, 10 used,
zero remaining**. Its two unused attempts were reallocated to **MACAE**; the
portfolio allocated ceiling remains100. Prior verified outcomes remain valid.

**No start, reactivation, rearm or evaluation is authorized by this runbook.**
Obtain an explicit new parent budget and reconcile both durable/runtime guards
before any future start/evaluation. `Assert-ModernizeBudgetOpen.ps1` currently
blocks start/deployment/evaluation helpers. The source runtime also rejects arm,
batch claims and model reservations under the closed allocation.

No compute was reactivated to update the private Blob. Its historical cap12 and
the existing image's implementation are unchanged; its last observed state is
disarmed with10 used. **Those two historical spare slots are not authorization.**
The local custody record is `evidence/modernize/budget-allocation.json`. No image
rebuild, infrastructure/role change or model call is required for this closure.
Use saved results for inspection; the commands below are historical procedures,
gated until a new explicit budget is recorded and deployed guards are reconciled.

## Scope and credentials

- Own application RG: `rg-ptu-modernize-demo`.
- Shared parent environment: `rg-ptu-bundle-platform/cae-ptu-bundle`, East US 2,
  Consumption only. Do not recreate the environment/network/registry.
- API: `ca-ptu-modernize-api`, 0.5 vCPU / 1 GiB, maximum one replica.
- UI: `ca-ptu-modernize-ui`, 0.25 vCPU / 0.5 GiB, minimum zero / maximum one.
- Backend UAMI: `id-ptu-modernize`; UI UAMI: `id-ptu-modernize-ui` (AcrPull only).
- No keys, secrets, `.env`, `.azure` directories, or local Azure login cache go
  into build contexts, images, manifests or reports.
- Cosmos and Blob public access must remain **Disabled**. Parent-approved private
  endpoints provide data access. Public app ingress is created atomically with
  the single-client `174.112.74.34/32` allow rule; never remove that restriction
  to make a probe work.

## Build and deployment

Commands below are from the bundle directory. Existing build contexts are
deliberately not overwritten automatically.

```powershell
.\scripts\Assert-ModernizeBudgetOpen.ps1
python .\scripts\modernize_prepare_container_contexts.py
.\scripts\modernize_build_images.ps1 -BackendOnly
.\scripts\modernize_publish_cloud.ps1 -BackendOnly
.\scripts\modernize_frontend_runtime.ps1
.\scripts\modernize_deploy_cloud.ps1 -Deploy
```

The original direct PyPI download failed TLS negotiation. The isolated Docker
contexts use `https://packagefeedproxy.microsoft.io/pypi/simple/`, the same
Microsoft feed used for the successful native dependency installation. TLS
verification remains enabled. Requirements and original application source are
unchanged except the documented three-line false-success fix.

The original frontend Docker build's `npm install` reported **Exit handler never
called**, then `npm run build` failed because Vite was missing. The working
alternative packages the already-successful original native `src/frontend/dist`
with the original Python runtime stage. For a fresh clone, complete the documented
native `npm ci` / `npm run build` first; the runtime script deliberately does not
substitute HTML or rebuild a different UI. Asset SHA-256 hashes are retained.

The cloud overlay adds async managed identity, a durable attempt guard, disabled
automatic remote deletions, diagnostic routes, and the executable mode required
by the bundled Linux parser. Linux unit/parser/import checks run without network
before image push. See `cloud-images.json` for actual tags/digests **after** push.
Do not treat this runbook as evidence that deployment or evaluation completed.

## Start/wake for bounded inspection

**Currently prohibited pending an explicit new budget.** If newly authorized,
use a minimum-one API replica only for the bounded exec/evaluation window.
The completed evaluation left the API revision **deactivated**, not deleted, to
stop its remaining idle replica immediately. Reactivate the latest revision first.

```powershell
.\scripts\modernize_start_cloud.ps1
```

After an authorized start reaches readiness, use
`.\scripts\modernize_exec_capture.ps1 -Action Preflight`. Preflight must show
private DNS for both persistence endpoints, HTTP 200 for the
actual Cosmos-backed history route, initialized original agents, and a readable
durable Blob budget. Model processing starts disarmed. No model is called by
preflight, agent metadata creation, or usage retrieval.

## One-shot real API/worker batch

Historical command only; the completed allocation cannot be reused.

```powershell
.\scripts\modernize_exec_capture.ps1 -Action Evaluate
```

The script uploads two synthetic SQL files through the original API, sends one
processing request, invokes the original SQL-agent orchestration and persistence,
retrieves ZIP/records/usage, parses downloaded SQL with the bundled Linux parser,
and performs a limited read-only SQLite comparison. It **does not claim browser
upload/download or Informix-to-SQL Server execution-equivalence**.

It refuses to repeat after a prior cloud batch/model attempt. Never delete or reset
the durable guard to obtain more calls. The initial four protocol calls remain in
the immutable baseline; cloud reservations are persisted before sending each
model HTTP request, including tool continuations and failed requests, up to
the original **12 total**. ETag compare-and-swap preserved that historical ceiling
across overlapping revisions and restarts. The current allocation is **closed at
10/10**; the old ceiling does not grant further attempts. Lack of Blob access
fails closed.

Results and request reservations persist in the OWN private Blob
`ptu-modernize-files/evaluation/modernize-global-budget-v1.json`.
Obtain a read-only snapshot through authenticated exec:

```powershell
.\Invoke-LabAz.ps1 -AzArguments @(
  'containerapp','exec','-g','rg-ptu-modernize-demo','-n','ca-ptu-modernize-api',
  '--command','python /app/control.py snapshot',
  '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70'
)
```

## Pause after testing — no deletion

First disarm inference, then restore scale-to-zero. UI remains max one/min zero.
Minimum zero is a scaling configuration, not proof that an active request or
cooldown replica has already stopped; verify replica state separately.
For immediate pause, deactivate only this app's latest revision after the
scale update. This is reversible and does not delete the application or data.

```powershell
.\Invoke-LabAz.ps1 -AzArguments @(
  'containerapp','exec','-g','rg-ptu-modernize-demo','-n','ca-ptu-modernize-api',
  '--command','python /app/control.py disarm',
  '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70'
)
.\Invoke-LabAz.ps1 -AzArguments @(
  'containerapp','update','-g','rg-ptu-modernize-demo','-n','ca-ptu-modernize-api',
  '--min-replicas','0','--max-replicas','1',
  '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70','-o','none'
)
$revision = .\Invoke-LabAz.ps1 -AzArguments @(
  'containerapp','show','-g','rg-ptu-modernize-demo','-n','ca-ptu-modernize-api',
  '--query','properties.latestRevisionName','-o','tsv',
  '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70'
)
.\Invoke-LabAz.ps1 -AzArguments @(
  'containerapp','revision','deactivate','-g','rg-ptu-modernize-demo','-n','ca-ptu-modernize-api',
  '--revision',$revision.Trim(),
  '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70','-o','none'
)
```

**Completed run:** batch `8f9c942d-c1fc-42ec-a07f-00478401de98` passed the real
API/worker/upload/download test. **10/10 allocated requests used; zero remain;
inference is disarmed and the single-batch claim is retained.** The two unused
attempts under the original cap belong to MACAE. Do not rerun the evaluation or
reset its ledger. Any future start/evaluation requires an explicit new parent
budget and reconciliation of the durable guard and runtime image.

Do not delete Azure resources, agents, threads, failed Canadian Cosmos, private
endpoints or shared platform objects automatically. Private endpoint hours/data,
shared Basic ACR/monitoring, Blob GB/operations and Cosmos RU/GB remain nonPTU
costs even with app replicas scaled to zero. US compute/persistence remains
synthetic MCAPS-only, not DND residency approval.
