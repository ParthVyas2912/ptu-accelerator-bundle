# MACAE — native UI and container images verified; private cloud runtime pending

## Current outcome — private runtime preparation, 2026-09-12 UTC

**Search capacity is now resolved.** Approved fallback
`ptu-macae-7d804f70-srch` was successfully created in **Canada Central**, in the
same new `rg-ptu-macae-demo`. It is **Basic1×1, semantic free, Entra-only,
PNA Disabled**. Provider/name/price/ARM preflights preceded creation.
The earlier East US 2 failure below is historical; no S1 upgrade occurred.

**Current fixed Search baseline: USD0.101/hour** (~USD73.73/730h), plus
metered Cosmos/Blob and applicable governance diagnostics. Parent's future
shared networking/ACR/compute costs are separate. No PTU was purchased.

Three **official Linux images built successfully** at commit
`8ac703a71f10b622bd3c82a9cc2b5dfe921c3025`; original tracked source is unchanged.
An explicitly disclosed, fail-closed backend metering layer also built.
Offline network-disabled container checks verified frontend UI/health200,
native backend `/healthz`200, and MCP9-tool HR discovery/blueprint success.
Seven additional offline budget/CAS tests pass. None proves cloud MI access
or a complete agent workflow. **Actual live inference is still0/12.**

The proposed parent-hosted composition is **one Consumption ACA app with three
official-service containers, total1vCPU/2GiB, max1replica, min0 when idle**.
Only frontend3000 is exposed via HTTPS and a mandatory single-client CIDR;
backend8000 and MCP9000 remain internal. The prepared Bicep compiles but
**has not been deployed**. At the verified East US 2 retail rates its fully
active compute request would be USD0.108/hour, before requests, free grants
and separately billed platform/data/model services.

**Parent handoff:** `evidence/macae/container-network-handoff.md` includes
exact resource IDs, private-link groups/DNS, all environment variables,
managed-identity roles, ports, build commands, budget migration and rollback
preparation. `container-preparation.json` records image digests and tests.
Parent must supply shared environment/ACR/UAMI and working private data paths;
MACAE has created no cloud compute, ACR, VNet, PE or DNS zone.

**Additional RFP/contract blocker identified:** native KB MCP tools run on the
Foundry Responses service, not inside the ACA caller. Caller-VNet private
endpoints alone do not give Foundry hosted tools access to private Search.
Current Learn requires an appropriate Foundry private egress configuration and
warns BYO VNet injection cannot simply be added to an existing account. Search
also needs outbound private model access if Foundry becomes private. These
paths and hidden KB model-call accounting must be resolved without recreating
models/accounts, weakening policies or introducing a replacement proxy.

### Current per-feature outcome, PTU dependence and separate infrastructure

| Feature | Current verified outcome | PTU dependence | Separate Azure infrastructure |
|---|---|---|---|
| HR/IT onboarding, planning and specialist reasoning | Native API/UI/MCP built; workflow blocked pending private Cosmos/runtime path | Eligible model calls may use PTU if explicitly provisioned; **not required**; zero live calls | Foundry/project, Cosmos, backend/MCP compute |
| RFP grounding | Search now exists; actual ingestion/grounded reasoning unverified; hosted-tool egress blocker above | Specialist and KB reasoning may both be model-billed; service-side calls need separate accounting | Search Basic, Blob, Foundry connections/private egress, Cosmos |
| Contract conflicts and human decision | Three synthetic conflict inputs prepared; actual conflict detection/approval not reached | Reasoning potentially PTU-eligible; approval/wait/transport is not inference | Search/Blob, Cosmos, UI/API/WebSocket hosting |
| MCP blueprint, discovery and unavailable-tool handling | Native component tests passed; Linux HR MCP tool also verified | Tested tools use **no PTU/model calls**; surrounding agent reasoning is separate | MCP hosting; future real downstream systems |
| UI, persistence, authentication and operations | Genuine local browser and container UI verified; private cloud runtime/MI/alerts/recovery not verified | No direct PTU dependence | ACA, Entra, Cosmos, private networking/DNS, shared ACR and telemetry |

Container issues found: official MCP `/health` is404, so ACA uses TCP9000
probes. Its native `uv run` attempted an online rebuild; supported
`UV_NO_SYNC=true` preserved the official image/CMD and passed offline.
Backend/ frontend200 health checks are liveness only, not dependency proof.
Cloud metering is disabled by default; the prepared Cosmos ETag ledger must
be initialized once after stopping local inference. It persists across
restarts without an Azure Files account or extra storage SKU. Rollback and
alert guidance/scripts are prepared, **not deployed or live-tested**.

## Historical checkpoint — approved continuation before private-runtime preparation

The remainder retains earlier test evidence and inspection notes. Statements
about Search being absent, awaiting a regional decision, or frontend progress
describe their dated checkpoint, not the current state above.

**As of 2026-09-11 20:18 EDT:** the native React UI, API and MCP are running.
The approved Foundry/project, both required models, Cosmos and Blob resources
were created in `rg-ptu-macae-demo`, East US 2. Full onboarding, grounded
RFP/contract analysis and human approval remain **blocked**, not passed.

Two external conditions prevent completion:

1. **Cosmos and Blob public network access is Disabled.** Azure activity logs
   contain successful policy-modification events. The native HR team upload
   reached Cosmos and failed: API **HTTP 500**, underlying Cosmos **403**,
   explicitly reporting that public source IP `52.148.138.235` is blocked by
   the account firewall. No team could be saved. No firewall setting or policy
   was bypassed or changed to restore public access.
2. **Search Basic creation failed with `InsufficientResourcesAvailable`.**
   Azure reports East US 2 lacks resources for new services. Search is absent
   from the final resource inventory. No region change or SKU escalation was
   attempted.

**Required parent decisions:** provide a policy-compliant network path for
local Cosmos/Blob access, and approve an available supported Search region
or wait for East US 2 capacity. No additional model-call allowance is needed
yet: **actual inference remains 0 / 12**.

### Resources actually created

All are in subscription `1feb53b2-854a-4ea7-b5a6-709b7d804f70`,
tenant `a600acd0-3028-4689-8402-3b471d7d924d`, new RG `rg-ptu-macae-demo`.
No pre-existing shared/protected resources were modified by MACAE.

| Resource | Actual configuration/state |
|---|---|
| `ptumacae7d804f70` | AIServices S0, local auth disabled; Entra-authenticated public endpoint |
| `ptu-macae-project` | Native Foundry project; metadata agents-list API **200**, zero agents |
| `gpt-5.4` | `2026-03-05`, GlobalStandard, capacity **10**, succeeded |
| `gpt-5.4-mini` | `2026-03-17`, GlobalStandard, capacity **10**, succeeded |
| `ptu-macae-7d804f70-cosmos` | NoSQL Serverless, one East US 2 region, Session consistency, local auth disabled |
| Cosmos database/container | `ptu-macae` / `memory`, partition `/session_id` |
| `ptumacae7d804f70st` | StorageV2 Standard_LRS Hot, shared-key/public-blob access disabled |
| Blob containers | `ptu-macae-rfp`, `ptu-macae-contract`, no anonymous access |
| Search attempt | `ptu-macae-7d804f70-srch`, Basic 1×1 semantic free: **failed/not created** |

Five approved access assignments were made **only on new resources**:
Foundry User at the new project; OpenAI User at the new account; Cosmos Data
Contributor at the new database; Blob Data Contributor separately at each
of the two new containers. Exact IDs/scopes are recorded in
`evidence/macae/continuation-infrastructure.json`. These are real access-control
changes, not “no modifications.”

### Cost baseline recorded before creation

The public retail-prices API returned **East US 2 Search Basic = USD 0.101/hour**
per unit, checked 2026-09-12 00:09 UTC. At one unit this would be about
**USD 73.73 / 730 hours**. **Search was not created**, so that proposed fixed
baseline is not an active Search resource charge.

There is no newly deployed cloud compute, ACR or PTU fixed commitment.
Existing new Cosmos RU/storage, Blob storage/transactions, standard-model
inference if later invoked, and applicable policy-managed diagnostics remain
metered. This is a configured-resource baseline, **not a measured Azure bill**
or a claim that all deployed resources are free. Governance-created
`setByPolicy-MCAPSGovernance` diagnostic settings were observed; no separate
App Insights/Log Analytics resource was deployed by this agent.

### Genuine UI and native component results

| Check | Actual result | Scope of proof |
|---|---|---|
| Isolated frontend installation | **631 packages**, completed outside OneDrive in approximately six minutes | Dependency setup |
| Official `npm run build` | TypeScript + Vite succeeded; 2,608 modules; Vite 64 seconds | Native UI build, not agent functionality |
| UI in real headless Edge | **HTTP 200**, title “Multi-Agent - Custom Automation Engine”, zero page errors | Genuine UI rendered; empty team state |
| Native `/config` | **200**, API URL points to local backend | Runtime configuration |
| Foundry Agents metadata | **200**, zero agents; AzureCliCredential with bounded 60-second process timeout | Project SDK/auth compatibility, no inference |
| Native HR pack upload | **500**, underlying Cosmos firewall **403** | Actual app dependency failure |
| Native MCP HR blueprint/error tests | Previously passed real MCP checks; service restarted successfully | Tool/component proof only |
| Repository focused unit tests | **123 passed**, 1 warning | Unit proof only |
| Budget observer self-tests | Sync, async, chunked SSE usage capture; persistent request 13 blocked | Offline mocked guard proof, not live model tests |

The UI screenshot is `evidence/macae/macae-ui.png`; browser observations are
`ui-browser.json`; the real failed team-save response is `hr-seed.json`.
The earlier slow OneDrive frontend attempt is resolved. No tracked repository
files changed; an identical-commit sparse checkout outside OneDrive hosts the
UI dependencies/build.

### Current per-feature PTU / Azure-infrastructure assessment

No feature inherently requires PTUs. Standard/GlobalStandard compatible
inference is sufficient for evaluation; PTU is an optional capacity choice.

| Feature | Inference/PTU dependence | Separate Azure infrastructure | Current verification |
|---|---|---|---|
| Safety checks and scope classification | Model calls; PTU optional | Foundry/project; Cosmos team context | Not reached |
| Manager planning, routing and synthesis | Repeated model turns; PTU optional | Foundry, Cosmos, backend hosting | Native API available; planning blocked |
| HR/IT specialists | GPT-5.4 participants, GPT-5.4-mini manager | Cosmos, MCP, future real HR/IT connectors | HR team save blocked; deterministic blueprint verified |
| RFP grounding/review | Specialist inference plus potentially server-side retrieval reasoning | Search Basic, Blob, knowledge bases and identity connections, Cosmos | Search capacity/network blocked |
| Contract conflict reasoning | Model-backed analysis; approval is separate | Search, Blob, Foundry connections, Cosmos | Three-conflict source prepared; not analyzed |
| MCP tool discovery/errors/blueprints | No model call for tested tools | Local MCP; real downstream systems if implemented | Component verified |
| Human approval/clarification | Waiting/approval transport does not itself use PTU; subsequent reasoning can | UI/backend/WebSockets, Cosmos, audit telemetry | Native routes/helpers present; full gate unverified |
| UI, persistence, identity, operations | No direct PTU dependence | Hosting, Cosmos, Entra, diagnostics, backup/recovery | UI verified; persistence blocked; recovery unverified |

**Actual model requests: 0**, across onboarding, RFP and contract workflows.
Token/cache counts and inference latency remain **null/unmeasured**. Native
HTTP timings, unit tests, browser rendering and metadata calls are not PTU
tests. Standard capacity **10 is not 10 PTUs**. See the current
[Microsoft Learn sizing guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing);
there is no model-independent fixed-token conversion per PTU.

### Reproducible START / STOP

After `az login` to the authorized subscription, use two PowerShell terminals:

```powershell
& "$B\scripts\Start-Macae.ps1" -Component mcp
& "$B\scripts\Start-Macae.ps1" -Component backend
```

Open **http://127.0.0.1:8111/**. The MCP endpoint is
**http://127.0.0.1:5111/hr/mcp**. The second command belongs in the second
terminal; each runs in the foreground.

```powershell
& "$B\scripts\Stop-Macae.ps1" -Component all
```

The STOP script checks recorded PID command lines and stops only the matching
MACAE processes. It deletes no Azure resources/data. MCP stop/restart was
actually verified. Current backend/UI PID **15244**, session
`macae-backend-approved`; MCP PID **13380**, session `macae-mcp-restarted`.
Processes remain session-attached and will not survive CLI shutdown.

An external ASGI runner mounts the unchanged native frontend server after the
unchanged backend routes, allowing UI/API to share 8111 while MCP uses 5111.
This port-consolidation adaptation is disclosed; no replacement business logic
or fake database was introduced.

Runtime credentials come only from Azure identity. START creates no `.env`,
keys, tokens or connection-string files. PID/budget state is outside OneDrive
under `%LOCALAPPDATA%\ptu-eval\macae-state`. The persistent request cap is not
reset by restarting. Actual model usage, when returned, is recorded without
prompts, response text or headers. Remote Search knowledge-base reasoning is
blocked by this evaluation guard until its hidden server-side model requests
can be metered/coordinated; a local HTTP call counter alone cannot prove the
aggregate twelve-call limit for that feature.

**Production verdict:** reference implementation worth further investigation,
but not production-ready evidence. Human approvals, grounded conclusions,
repeatability, isolation, external HR transactions, backup/restore and rollback
remain unverified. No active application alerting or automated cloud rollback
was added. Network and capacity blockers must be resolved through authorized
operations, not policy bypass.

## Historical first-pass checkpoint — superseded where current results differ

The following preserves the original inspection and pre-approval outcomes.
Statements below about missing resources, pending approval or frontend
installation refer to that earlier checkpoint, not the current inventory.

**Recommendation: Investigate.** The real backend and MCP services run locally,
but onboarding, RFP and contract workflows cannot proceed without native
Cosmos DB and compatible Foundry deployments. No substitute generic chat app
was built. No Azure infrastructure was created and no model inference occurred.

## Infrastructure decision sent early

### Immediate approval request — MACAE Phase A only

Source inspection is complete. Request authorization for this bounded native
**HR onboarding** evaluation, not the full default deployment:

| Exact proposed resource | Configuration |
|---|---|
| Resource group `rg-ptu-macae-demo` | Authorized subscription/tenant below; `eastus2`; required evaluation tags |
| Foundry account `ptumacae7d804f70` | AIServices, S0, `disableLocalAuth=true`; Entra credentials only |
| Foundry project `ptu-macae-project` | Under the new account; project identity and narrowly scoped permissions |
| Deployment `gpt-5.4` | Version `2026-03-05`; GlobalStandard; capacity **10** |
| Deployment `gpt-5.4-mini` | Version `2026-03-17`; GlobalStandard; capacity **10** |
| Cosmos account `ptu-macae-7d804f70-cosmos` | NoSQL Serverless; one East US 2 region; Session consistency; local authentication disabled |
| Cosmos database/container | Database `ptu-macae`; container `memory`; partition key `/session_id`; no provisioned RU/s |

Names remain subject to Azure availability; report a collision instead of silently
changing scope. Add only required identity roles on these new resources.
No shared Foundry/Search resources will be modified.

**Explicit exclusions:** Azure compute, ACR, Search, Blob Storage, image models,
new PTUs, reservations, quota increases and blanket `azd up`. Native backend/MCP
remain local. Before any inference, enforce the existing **12-request aggregate
ceiling**, including safety checks, tool follow-ups and retries; stop at the
ceiling rather than assume an entire agent workflow fits.

This phase does **not** unlock RFP/contract grounding. A separately approved
Phase B would add Search Basic (one replica, one partition), Standard_LRS Blob
Storage, and native knowledge-base/source/identity connections.

Billing in Phase A is standard model inference and Cosmos consumed RU/storage;
there is no new fixed App Service/ACR/Search footprint. The supplied Canada
Central retail rates are not an East US 2 quote and have not been used as one.
No PTU sizing or purchase is justified by a small token test.

Installed `azd 1.23.7` satisfies this repository's `>=1.18.0` requirement and
is not the excluded `1.23.9`; no azd update is required. No emulators or Docker
builds are running for MACAE, and the stalled npm/typecheck tasks were stopped.
An explicit Phase-A `write_agent` request again failed to resolve the parent
owner ID; this proposal is therefore also returned directly to the caller.
**Approval remains pending; no creation performed.**

Repository: https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator  
Commit: `8ac703a71f10b622bd3c82a9cc2b5dfe921c3025`  
Subscription: `1feb53b2-854a-4ea7-b5a6-709b7d804f70`  
Tenant: `a600acd0-3028-4689-8402-3b471d7d924d`

No Azure resources have been created, changed or reused for inference.
Protected applications have not been touched. Live model calls: **0 / 12**.

The current content packs require **GPT-5.4** (HR) and **GPT-5.4-mini**
(RFP, contracts and orchestration). Existing Canada East Foundry inventory
contains GPT-5.1, GPT-4.1-mini and text-embedding-3-small; it does not contain
the native required models. Reuse is therefore **not approved/proven compatible**.
The current reuse environment variable is `AZURE_EXISTING_AIPROJECT_RESOURCE_ID`,
not the spelling in the supplied playbook.

### Do not run the default deployment

The vanilla Bicep route creates:

| Resource | Actual template setting | Billing |
|---|---|---|
| Foundry account/project | S0; GPT-5.4-mini 2026-03-17 capacity 100, GPT-5.4 2026-03-05 capacity 150, gpt-image-1.5 capacity 5 | Model inference, not PTU |
| Azure AI Search | Basic, 1 replica, 1 partition, semantic tier free | Fixed Search units plus applicable retrieval features |
| Cosmos DB NoSQL | Serverless, `macae` database, `memory` container partition `/session_id` | RU consumption and storage |
| Blob Storage | Standard_LRS | Storage and transactions |
| ACR | Basic | Fixed registry charge |
| Container Apps | Consumption; backend and MCP each 2 CPU / 4 GiB, min=max=1 | Persistent minimum-replica compute |
| Frontend App Service | **B3**, one instance | Fixed compute |
| Log Analytics / App Insights | PerGB2018 | Telemetry ingestion and retention |
| Managed identity and RBAC | Additive access required | No separate base identity charge |

The template provisions model deployments **even when an existing project is
selected**, so setting the reuse flag alone does not preserve shared model
deployments. The post-deploy script also temporarily changes public network
access in its WAF path. Neither behavior is allowed by the evaluation contract.
The non-WAF MCP template enables external ingress with `ENABLE_AUTH=false`;
it must not be exposed as-is. No such hooks have been executed.

The router's allowed app regions exclude Canada Central and Canada East.
**East US 2** is a documented overlap for the app and AI region parameters;
actual required-model availability and quota are being checked read-only.

### Minimum proposed native local-backed evaluation, not deployed

Target a dedicated `rg-ptu-macae-demo`, not a protected resource group.
Host the repository's real backend, frontend and MCP server locally on loopback.
Obtain a compatible isolated Foundry S0/project with the exact two text models,
using existing quota only and the smallest service-supported GlobalStandard
capacity; no image model is needed for the requested three text workflows.
Provide Cosmos DB Serverless and a dedicated Standard_LRS storage account.
RFP/contract native knowledge bases additionally need compatible Azure AI Search
Basic, indexes, Foundry connections and their identity roles. Shared Search reuse
has not been proven or authorized. HR does not require Search-based grounding.

Read-only catalog and quota checks succeeded for **East US 2**:
GPT-5.4 `2026-03-05` and GPT-5.4-mini `2026-03-17` are listed with
GlobalStandard default capacity **10** each. Both quota entries report
current **0**, limit **1000**. The proposed model allocations are therefore
**10 each**, using existing quota, without requesting an increase. The catalog
returns no minimum, so these are its documented defaults, not a claim of an
absolute service minimum. Parent coordination is still required.
**No capacity increase, PTU purchase, or new billable deployment is authorized
by this report.**

The parent-directed `write_agent` failed because the parent owner ID was not
resolvable by the messaging tool; an early sibling relay was requested.
Dependency installation and local validation continued independently; final
outcomes follow.

## Actual startup and local setup

| Component | Actual endpoint | Process/session | Result |
|---|---|---|---|
| Native backend | `http://127.0.0.1:8111`; API `/api/v4` | PID **25496**, session `macae-backend-native` | Running, attached to session |
| Native MCP | `http://127.0.0.1:5111/hr/mcp` | PID **35232**, session `macae-mcp-native` | Running; actual protocol/tool tests pass |
| Frontend | None | Install session `55` stopped | Not started or verified |

Backend launch from `src/backend`:
`.venv/Scripts/python.exe -m uvicorn app:app --host 127.0.0.1 --port 8111 --no-access-log`.
MCP launch from `src/mcp_server`:
`%LOCALAPPDATA%/ptu-eval/macae-mcp/Scripts/python.exe -m uvicorn mcp_server:app --host 127.0.0.1 --port 5111 --no-access-log`.
Nonsecret endpoint configuration is runtime environment only. No keys or
connection strings were generated or saved. Backend uses the documented
`APP_ENV=dev` Azure identity path. The existing Foundry endpoint was configured
for startup, but was not invoked for inference.

Backend `uv sync --frozen` succeeded with Python 3.11 and repository-pinned
dependencies in isolated `src/backend/.venv`. MCP `uv sync --frozen --extra dev`
succeeded in `%LOCALAPPDATA%/ptu-eval/macae-mcp`. The local guide suggests Python
3.12, but pyproject and official Dockerfiles permit/use 3.11.

Native imports were exceptionally slow. A bounded diagnostic timed out while
reading imported FastMCP/beartype modules; no security settings were changed.
Services eventually started successfully. The full backend test attempt was
stopped during those imports, then focused repository tests were run:
**123 passed, 1 warning, 16.17 seconds** (date utilities, message models, health
middleware and plan-review helpers). These are unit/component results, not
evidence of working multi-agent workflows.

`npm ci --no-fund --ignore-scripts` remained in progress for more than 30 minutes;
it and an inconclusive TypeScript check were stopped. Frontend build, UI,
browser-to-backend integration and UI human approval are **unverified**.
No tracked repository files were changed. Source lockfiles were not rewritten.

## Functional expected versus actual

| Test | Expected | Observed | Verdict |
|---|---|---|---|
| Native API discovery | Real accelerator routes available | `/openapi.json`: **200**, 95.27 ms; plan, approval, clarification and team APIs present | Component pass only |
| Team listing | Seeded team configurations | `/api/v4/team_configs`: **500**, 272.46 ms | Blocked by absent Cosmos |
| Synthetic onboarding | HR/IT routing and coherent approved plan | Native `process_request`: **400**, 9.24 ms at team lookup | End-to-end blocked |
| Synthetic RFP | Missing audit evidence, specialist outputs, consolidated recommendation | **400**, 4.37 ms at team lookup | End-to-end blocked |
| Three-conflict synthetic contract | Canada-only/30-day/human-payment-approval policies versus US/365-day/automatic payment; detect all three and require approval | **400**, 4.51 ms at team lookup | End-to-end blocked; approval unverified |
| Unavailable MCP tool | Explicit failure, no fabricated success | Native MCP HTTP **200** envelope with **isError=true**, `Unknown tool`, 20.79 ms | MCP layer pass; agent recovery unverified |
| Repeat native HR blueprint 3 times | Deterministic same blueprint | **200**, `isError=false`; 4.28/5.38/5.44 ms; same 1,136-character response/hash | Tool-level pass only; LLM plan repeatability/isolation unverified |

All three actual workflow attempts failed with the native error:
`Error retrieving team configuration: Invalid URL scheme or hostname`
because `COSMOSDB_ENDPOINT` is unset. The real DatabaseFactory supports Cosmos,
not a documented SQLite/in-memory fallback. No database behavior was mocked or
replaced. Requests stopped **before** RAI/model inference.

The MCP HR endpoint negotiated protocol `2025-03-26`, reported server
`MACAE-hr` / FastMCP `3.2.0`, and exposed **9 tools**. Ten JSON-RPC requests
included seven tool calls: three successful blueprints, one unavailable tool,
and three rejected calls from an initial test-harness parameter typo
(`workflow_name` instead of `workflow`). The correction was in the test call,
not in application source. The invalid calls visibly returned validation
errors and are not counted as successes.

The identical blueprint SHA-256 was
`68d26951a659e8a249777d1be25ecbb5b4725d6aec5ef6d8c9e02e126cf119c1`.
This is deterministic tool repeatability, **not** proof that three generated
plans agree or that users cannot see another session's data.

## Distinct approaches investigated and stop condition

1. **Native documented local service path:** dependencies installed; backend
   and MCP started; real app requests and native MCP calls executed. Mandatory
   Cosmos/team persistence blocks the workflows, with required models also
   absent from the shared project.
2. **Native azd/Bicep and existing-project deployment path:** templates,
   Windows hooks, image build and seeding scripts inspected. Foundry reuse does
   not suppress model deployment. Region, ingress, network-change and fixed
   compute defaults conflict with this low-cost contract. Exact alternative
   resource proposal and read-only model quota evidence are above.
3. **Documented Docker route:** official backend/MCP Dockerfiles inspected and
   local images inventoried without using protected images. Containers retain
   the same mandatory Foundry/Cosmos requirements and do not remove the blocker.

No new infrastructure was approved through parent coordination; parent
messaging returned “No agent found.” Stop at this specific cloud dependency
boundary rather than fabricate a database or rename incompatible shared
deployments. The native loopback services remain attached for inspection.

## PTU and inference accounting

**Actual live model calls: 0 / 12**, including retries. Actual per-workflow calls:
onboarding **0**, RFP **0**, contract **0**. No inference HTTP status, input,
output or cached tokens, inference latency or PTU utilization was returned.
Those fields are **null/unmeasured**, not estimates. The timings above measure
local HTTP/tool responses only.

Current shared deployments are Standard/GlobalStandard, not provisioned.
Native code uses FoundryChatClient, with separate RAI checks, scope evaluation,
manager planning/progress, specialist turns, tool follow-ups and synthesis.
Actual inference counts are dynamic and **not measured**. `max_rounds=30` and
`max_stall_count=5` are not a twelve-request budget. Before any live workflow,
instrument the SDK transport and enforce an aggregate request limit including
retries, safety checks and any knowledge-retrieval model calls; request a larger
allowance if needed rather than claiming all test cases fit into twelve calls.

PTU could be relevant to steady, repeated production orchestration workloads,
but no utilization or savings is demonstrated here. Cosmos RU/storage, Blob
storage/transactions, Search capacity and knowledge-retrieval features,
hosted tools where applicable, cloud compute, ACR, telemetry and network
transfer remain **separately billed**; PTU does not cover the whole application.

### Per-feature PTU dependence and Azure infrastructure

**No MACAE feature inherently requires PTU.** Model-backed features need compatible
inference deployments; Standard/GlobalStandard is the proposed evaluation
configuration. PTU is an optional production capacity/billing choice for eligible
model calls, not a replacement for the application's other services.

| Feature | Inference/PTU relationship | Azure infrastructure outside model throughput | Verified state |
|---|---|---|---|
| RAI safety checks and request scope evaluation | Model-backed; eligible calls could consume provisioned model capacity if explicitly routed there | Foundry account/project and native team/context persistence in Cosmos | Not reached; 0 live model calls |
| Plan generation, manager routing, progress checks and final synthesis | Repeated model turns; potential PTU demand depends on measured input/output/cache tokens and call rate | Foundry project, Cosmos; backend compute if cloud-hosted | API exists; actual planning blocked |
| HR/IT specialist reasoning | Native HR pack uses GPT-5.4; manager uses GPT-5.4-mini. PTU optional for inference only | Cosmos; MCP/backend hosting; future real HR/IT systems and connectors | Workflow blocked; HR blueprint tool independently verified |
| RFP review and grounded recommendations | Specialist/retrieval-related inference may be model-billed; separately trace retrieval model calls before attributing them to any PTU deployment | Search Basic, Blob Storage, knowledge bases/sources, Foundry connections and identity permissions, Cosmos | Blocked; grounding unverified |
| Contract conflict identification and consolidated recommendation | Same separation as RFP; model reasoning could use eligible provisioned deployments, but approval is not inference | Search, Blob Storage, Foundry connections and Cosmos | Three synthetic conflicts submitted; analysis blocked |
| MCP discovery, blueprint lookup and unavailable-tool error | Tested tools make no model calls and have no PTU dependence. Agent reasoning before/after a tool may make separate calls | Local MCP hosting now; cloud compute and real downstream APIs if later deployed | Native component behavior verified |
| Human approval, clarification transport and audit persistence | Approval/wait/transport does not itself consume PTU; generating questions or resuming agents may call models | Frontend/backend, WebSockets, Cosmos and audit telemetry | Routes/unit helpers verified only; human approval flow unverified |
| UI, session/team storage, authentication, monitoring and recovery | No direct PTU dependence | Frontend/backend compute, Cosmos, Entra identity, App Insights/Log Analytics, backups and deployment tooling | Backend running; frontend, cloud monitoring and recovery unverified |

Sizing reference checked on **2026-09-11**:
[Microsoft Learn — Determine PTU sizing for a workload](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing).
Its current model table includes GPT-5.1, GPT-4.1-mini, GPT-5.4 and GPT-5.4-mini.
That does **not** establish shared-model compatibility with the native MACAE
packs, a provisioned deployment in this subscription, or available reserved
capacity in a particular region.

Sizing must use model/version/deployment-specific parameters, measured peak
request rate, input/output token mix and cache rate, plus the applicable
deployment minimum and increment. There is **no universal fixed-token value
per PTU**. No sizing calculation is warranted from these non-inference smoke
tests. The proposed **GlobalStandard capacity 10** allocations above are
standard deployment capacity settings, **not 10 PTUs**.

### Shared governance update

The coordinator reports `edcfoundryhack01.disableLocalAuth=true`; preserve it
and use Entra credentials only. No account keys will be retrieved, persisted
or enabled. Shared Search is Basic, one partition and one replica; inventory
does not establish permission or compatibility for reuse.

The updated `evidence/protected-resources.json` exists and contains 100
inventory entries. It is the current protection inventory, including the
additional SpecSuite/Specsmith and managed resource groups; this evaluation
has not touched those resources. Future supported Azure CLI actions must use
`Invoke-LabAz.ps1 -AzArguments <string[]>`; the guard does not confer billing
approval. The infrastructure proposal is explicitly for **MACAE only** and
still requires parent coordination.

## Production fit and operational readiness

The reference implementation offers meaningful routing, MCP and native
plan-review structures, but is not production-verified here. Inspected HR
tools format demonstration success responses rather than call real HR
systems; integrate and independently verify real business transactions.
RFP/contract grounding, three-conflict detection, approval enforcement,
cross-session isolation, restart recovery and durable checkpoint behavior
remain unverified. In-memory orchestration checkpoints require reliability
assessment before scaling.

For production, require authenticated/restricted ingress for every paid
operation, per-user authorization, hard call/token budgets, observed request
and tool-error metrics, approval audit trails, alerts, Cosmos backup/restore
validation and versioned deployment rollback. Application Insights is
currently **disabled**, not an active monitoring deployment. No automated
cloud rollback or alerting was deployed because no cloud deployment occurred.
This is an MCAPS synthetic evaluation, **not DND/JDCP accreditation**.

Machine-readable evidence, synthetic inputs, process IDs, command outcomes,
model inventory, proposed SKUs and failures: `evidence/macae/result.json`.
