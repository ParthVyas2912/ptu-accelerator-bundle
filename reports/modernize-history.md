# Historical snapshot — superseded by modernize.md

# Modernize Your Code — partial deployment; governance connectivity blocker

## Latest coordination: shared private cloud fallback approved

At 20:51 EDT the parent approved a targeted cloud-container fallback on the
parent-provisioned **MCAPS** platform `rg-ptu-bundle-platform` / `cae-ptu-bundle`
in East US 2, with shared Basic `acrptubundle7d804f70`. Platform readiness and
allowed client CIDR are still pending. No duplicate network, environment or
registry will be created; no further public-access enable attempt is permitted.

Exact private-endpoint targets/group IDs were verified by guarded read-only ARM
calls and saved in `evidence/modernize/shared-platform-request.json`: successful
Cosmos account **Sql**, Canadian Storage account **blob**. The failed Canadian
Cosmos account is not a target. DNS is the parent-managed MCAPS arrangement,
not JDCP central DNS or another subscription.

Official `src/backend/Dockerfile` and `src/frontend/Dockerfile` build contexts
have been staged outside OneDrive, excluding credentials/dependencies/caches.
Sequential local builds have started in attached session
`modernize-container-build`, using a Modernize-only BuildKit builder capped at
**2 GiB and two CPUs**, without changing the shared/default Docker builder.
Build completion, image digests and cloud deployment are **not yet established**.
Reproduction: `scripts/modernize_prepare_container_contexts.py` then
`scripts/modernize_build_images.ps1`.

Planned Consumption resources: API **0.5 vCPU / 1 GiB**, UI **0.25 vCPU / 0.5 GiB**,
max one replica each; minimum zero where HTTP-trigger compatible, with only a
bounded temporary API minimum-one period if required for ingress-disabled
authenticated exec testing. Model allowance remains **4 used / 8 remaining**.
A durable cross-restart attempt guard and managed-identity adapter must be tested
before cloud inference. This will be reported as **adapted official cloud-container
deployment**, not unchanged native deployment. Prior findings below remain valid.

**Current classification: original native UI/API and five agents running, approved
Azure persistence provisioned, but NOT a full functional deployment.**
No upload → cloud persistence → five-agent processing → downloadable ZIP end-to-end
pass has been established. Do not present this as one of seven fully deployed apps.
The remaining blocker is management-group network governance, not Cosmos capacity,
dependencies, missing containers, model capacity, or an unapproved regional fallback.

## Source and scope

- Repository: https://github.com/microsoft/Modernize-your-code-solution-accelerator
- Commit: `7592ea97550fb711d7d8b64186875967d574c5d5` (`main`).
- Describe/tag: `v1.9.1-57-g7592ea9`; commit date 2026-08-27T20:37:31+05:30.
- Clone: `C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\Modernize-your-code-solution-accelerator`.
- Contract and relevant playbook sections were read first. Parallel work and the
  12-model-request cap override the sequential/load-test playbook suggestions.
- Synthetic SQL and repository samples only; no business/customer data.

## Infrastructure and reuse

Tenant `a600acd0-3028-4689-8402-3b471d7d924d`, subscription
`1feb53b2-854a-4ea7-b5a6-709b7d804f70`.

Reused the explicitly allowed **nonprotected** Foundry account `edcfoundryhack01`
in `rg-edc-foundry-hack`, project `edc-hack-proj`, Canada East. Existing deployment
`gpt-5.1`, version `2025-11-13`, SKU **GlobalStandard**, capacity 100. The source
defaults match this model/version. Four successful real Foundry Agents runs
demonstrate limited protocol compatibility; full five-agent tool support remains
unverified at this point.

Endpoint:
`https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj`,
API `2025-05-01`.

`disableLocalAuth=true` was confirmed through the updated `Invoke-LabAz.ps1`
guard. All evaluation authentication uses Entra/Azure CLI identity. No keys were
retrieved, persisted or used; local authentication was not enabled. The expanded
protected-ID inventory was read and remains excluded from all app operations.
Azure AI Search is **not required or used by this accelerator's inspected SQL
migration path**, so the shared Basic Search service is not an app cost here.

**Parent approved the exact minimal persistence set at 19:58:57 EDT.**
Resource group `rg-ptu-modernize-demo` and StorageV2 Standard_LRS Hot account
`stptumodernize0911pv` were created in Canada Central, with shared keys and anonymous
Blob access disabled. No model deployment was created or changed.
Cosmos Serverless account `cosmos-ptu-modernize-0911` remains in **Failed** provisioning
state: Azure returned `ServiceUnavailable`, high demand / subscription region-access
request required. It was not deleted.
An early exact persistence proposal is in `evidence/modernize/inspection.md`:
dedicated StorageV2 Standard_LRS Hot plus Cosmos NoSQL Serverless in Canada Central,
with native local UI/API instead of cloud hosting. Parent `write_agent` delivery
failed with “No agent found”; the proposal was also sent via a sibling. No approval
was inferred from that failure; implementation began only after the later explicit approval.

The original approved proposal is `evidence/modernize/infrastructure-proposal.json`:
`stptumodernize0911pv` (Standard_LRS Hot, private `ptu-modernize-files`) and
`cosmos-ptu-modernize-0911` (NoSQL Serverless, database `ptu-modernize`, containers
`ptu-modernize-batches`, `ptu-modernize-files`, `ptu-modernize-logs` with the source
partition keys), in `rg-ptu-modernize-demo`, Canada Central. Guarded read-only
name checks returned storage `nameAvailable=true` and Cosmos `exists=false`.
Only scoped identity access is requested. No large emulators are proposed.
Installed azd 1.23.7 meets repository `>=1.18.0 !=1.23.9`; no update is required.

**Resolved regional blocker and approved alternative:** Cosmos location metadata reports
subscription regular access **false for Canada Central and Canada East**, but
**true for East US 2**. Canada East was investigated and not attempted.
Parent explicitly approved and provisioning succeeded for a new single-region **Serverless** account
`cosmos-ptu-modernize-eus20911` in **East US 2**, retaining the already-created
Canadian Storage account and unchanged Foundry deployment. Approval timestamp:
2026-09-11T20:11:19-04:00. Database and all three native containers now exist.
**US data persistence applies only to synthetic MCAPS tests, not DND residency approval.**
See `cosmos-capacity-blocker.json` for the retained failed Canadian account's operation/activity IDs,
and `persistence.json` for actual container-scoped Blob/database-scoped Cosmos grants.

### Exact current external blocker

The first native Cosmos history request returned Cosmos **403**; the original
`GET /api/batch-history` translates it to **HTTP 500**. The client source was
`20.236.11.102`. A single exact-IP enable request on each new persistence account
completed in ARM, but both returned **publicNetworkAccess=Disabled**. Activity logs
prove management-group assignment **MCAPSGovDeployPolicies** applied:

- `CosmosDB_PublicNetwork_Modify` — effect `modify`.
- `StorageAccount_PublicNetwork_Modify` — effect `modify`.

No retry against the identified governance control, exemption, policy change or
bypass was performed. The exact IP allowlist persists but grants no current
public access. Storage remains default-deny/no-service-bypass, with shared keys
and anonymous Blob access disabled; Cosmos local authentication remains disabled.
No shared Foundry network/configuration change occurred.

Evidence: `network-policy-events.json`, `network-policy-blocker.json`,
`native-e2e.json`. The browser evaluator stopped at its real API persistence
preflight, **before uploading or clicking processing**. All eight remaining model
requests remain available.

Two legitimate connectivity alternatives were investigated, **not executed**:

1. **Private Link with an approved existing private client path.** Cosmos `Sql`
   and Storage `blob` private endpoints, approved DNS integration, and actual
   routed client access are needed. Creating endpoints alone cannot connect this
   Windows host. Existing approved VPN/ExpressRoute or an approved in-network
   host must be identified; no protected network/resource reuse, new VM, VPN
   gateway or AKS is authorized. Endpoint hours/data, DNS and routing are nonPTU
   costs. [Microsoft Storage guidance](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints).
2. **Governance-approved Network Security Perimeter design.** Microsoft documents
   IP-based inbound access for Cosmos and enforced perimeter rules for Blob.
   The policy owner must approve the supported configuration and regional scope;
   no perimeter, managed identity, association or exemption was created. Cosmos
   NSP is documented as public preview without SLA. It is not permission to work
   around policy. Pricing/topology require confirmation before any proposal is
   approved; no zero-cost claim is made.
   [Cosmos NSP](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-configure-nsp);
   [Storage NSP](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-perimeter).

This is an MCAPS lab, not a JDCP network deployment. No other subscription, DND
hub resolver, central DNS zone, protected VNet, or unrelated app resource was called.

One additive, documented Foundry User role was created at **project scope only**
after an actual 401 identified missing Agents data access. Role ID
`53ca6127-db72-4b80-b1b0-d745d6d5456d`, assignment
`b0431624-b61b-53a6-9c75-10638628e3b6`. ARM returned 201. A subsequent read remained
401 during propagation; later actual agent creation and four runs succeeded.
No protected resource, existing deployment, network rule, or content filter changed.

**Access-control modification and authorization basis:** the role assignment above
is an actual shared-resource access-control modification, not “no resources
modified.” Modernize executed it based on the initial contract's allowance for
documented additive RBAC when reusing the explicitly permitted nonprotected
Foundry project. **No separate affirmative parent approval for that assignment
was received, and MACAE neither authorized nor executed it.** This action conveys
no authorization for broader permissions, additional assignments or billable
infrastructure. No rollback or further RBAC change is being made automatically.

Parent separately granted **Cognitive Services OpenAI User** at the allowed
`edcfoundryhack01` account scope: assignment
`4df8a697-fc79-448a-8f0f-54f90020f5d3`, role
`5e0bd9bd-7b93-4f28-af87-19fc36ad61bd`. Evidence is
`evidence/preflight/inference-role-assignment.json`. Modernize did not duplicate
this grant. It serves model-inference/embedding permissions, distinct from the
project Agents API grant. Authentication remains Entra-only.

Approved new persistence grants to current lab user
`87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed`:

- Blob Data Contributor `ba92f5b4-2d11-453d-a403-e96b0029c9fe`, assignment
  `ef21d753-052a-4fe7-83bd-c48c5e8dfeeb`, scoped only to
  `stptumodernize0911pv/blobServices/default/containers/ptu-modernize-files`.
- Cosmos built-in Data Contributor `00000000-0000-0000-0000-000000000002`,
  assignment `474c6a70-aeea-4bc3-8998-b3bbdb943a24`, scoped only to
  `cosmos-ptu-modernize-eus20911/dbs/ptu-modernize`.

Full ARM scope/role IDs are in `persistence.json`. These role assignments do not
override the independent network block.

The protocol evaluator created agent `asst_sRbr9hYitxfDBEkQ4JB5hNcU`
(`ptu-modernize-migrator-eval`) and four synthetic threads. IDs are retained in
`evidence/modernize/migrator-protocol.json`. No automatic Azure deletion occurred.

## Actual functional results so far

The fallback reproduced the repository **Migrator agent protocol**, using the
original prompt, three-candidate setting, response schema, model and temperature.
It is not a generic replacement application and is **not execution of the complete
Python SDK five-agent pipeline**. Prompt SHA-256 and raw synthetic responses are
in the evidence.

| Test | Expected | Actual | Result / scope |
|---|---|---|---|
| Malformed `SELEC customer_id FROM WHERE;` | Actionable rejection, no invented repair | Empty candidates; precise misspelled keyword, missing table and invalid WHERE diagnostics | PASS, Migrator component |
| Repo `q3_informix.sql`, correlated subquery + NVL | Valid target and preserved null/no-match behavior | Three targets, including ISNULL, COALESCE and LEFT JOIN rewrite | PASS for native parse; limited result check below |
| Synthetic JOIN + FOREACH / RETURN WITH RESUME procedure | Flag unsupported or changed calling/result semantics | Procedure, table-valued function and cursor/multiple-result-set variants; summary calls all “semantically equivalent” | FAIL for adequate incompatibility warning; equivalence NOT established |
| Harmless `gender` / `age_group` schema fields | No unwarranted demographic-content refusal; preserve fields/filter | Three candidates preserve selected fields and `active = 1`; no RAI refusal | PASS for this narrow schema fairness check, not a demographic fairness audit |
| Native T-SQL parser | Parse generated targets | All 9 generated candidates returned empty syntax-error lists | PASS for syntax only |
| Synthetic NVL result comparison | Same duplicate/null/no-match row multiset | All 3 generated targets produced the expected five rows in SQLite | PASS with explicit NVL/ISNULL → COALESCE adaptation; NOT actual Informix/SQL Server equivalence |
| Repo target references | Parse all 7 supplied `q*_tsql.sql` fixtures | All 7 parsed | PASS, references only—not generated in this run |
| Failure placeholder validation | Reject `No migration` | Original failed; narrow fix now rejects placeholder/whitespace and discards partial candidate on communication error | FIXED; complete imported-source module: 11 tests passed |
| Original UI/API startup | Render native UI and initialize five SQL agents | Built React renders in Chromium; five agents initialized; both processes loopback-only | PASS for startup, not persistence |
| Real persistence preflight | Native batch history returns HTTP 200 | HTTP 500 caused by Cosmos 403; governance forces public network access Disabled | BLOCKED |
| Multi-file upload/status/download | Per-file progress and downloadable results | Evaluator stopped before upload/model processing; native DB/containers exist but local client has no permitted data-plane path | NOT RUN; no E2E claim |

The bundled T-SQL parser also accepts `No migration` without syntax errors because
syntactic acceptance is not object existence or business correctness. This is not,
by itself, a parser defect. It demonstrates why the application's nonempty-string
validation plus parsing cannot prove successful translation.

The authorized fix changes three production lines in `convert_script.py`:
empty initial candidate, return empty after agent-communication failure, and
reject whitespace / `No migration` in validation. Four focused repository tests
passed initially; after installing pytest-asyncio, the complete module passed
**11 tests in 11.70 seconds**, with none deselected.
The isolated before/after validation evidence is retained separately. These are
uncommitted local source changes; the recorded upstream commit remains the base.

The procedure candidates have materially different invocation and result-set
contracts. The LLM's equivalence assertion was explicitly rejected as evidence.

## Observed usage

| Case | Model requests | Input tokens | Output tokens | Cached input tokens | Client elapsed seconds |
|---|---:|---:|---:|---:|---:|
| Malformed | 1 | 1,240 | 124 | 0 | 36.875 |
| Repo NVL | 1 | 1,284 | 399 | 0 | 28.031 |
| Streaming procedure | 1 | 1,282 | 533 | 0 | 27.031 |
| Demographic schema | 1 | 1,248 | 278 | 0 | 28.078 |
| **Total** | **4 / 12 initial cap** | **5,054** | **1,334** | **0** | **120.015** |

All four model-start requests returned HTTP 200 and runs completed. No model
retries, model 429s or model 5xx errors were observed. Elapsed time includes
thread creation, polling and result retrieval—not pure model serving latency.
The service usage object reports `prompt_token_details.cached_tokens = 0`.
Authentication probes are separate, non-model calls and had two 401 failures
before the successful runs. No Azure Monitor PTU utilization was measured.

## PTU dependence versus other cost drivers

### Per-feature allocation

| Application feature | PTU dependence | Azure infrastructure / other cost | Evaluated scope |
|---|---|---|---|
| Browser UI and file selection | None | Local browser/native frontend; ACA frontend if cloud deployed | Official build and Chromium render passed; upload selection not tested after blocked preflight |
| Multi-file upload and batch history | None for upload/history themselves | Blob files; Cosmos batch/file/log records; backend CPU and network | Full persistence flow blocked |
| Migrator: validation and three candidate translations | Optional provisioned inference, not required | Foundry model deployment and Agent API; app orchestration | Four real PAYG Migrator protocol runs |
| Picker: candidate selection | Optional provisioned inference | Same Foundry model; orchestrator compute | Not yet run in SDK pipeline |
| Syntax-checker agent and tool continuation | Model steps potentially provisioned; native parser is not | Foundry inference plus local/backend T-SQL parser CPU | Parser executed; agent-tool path not yet validated |
| Fixer / retry cycle | Optional provisioned inference; each retry adds work | Foundry inference plus compute, logs and state writes | Not run |
| Semantic-verifier agent | Optional provisioned inference; does not establish SQL equivalence | Foundry inference plus orchestration/state | Not run; Migrator equivalence assertions independently challenged |
| WebSocket per-file progress | None | Backend hosting/network; persisted status in Cosmos | Not E2E tested |
| Downloadable SQL/ZIP and reports | No inference required for packaging existing outputs | Blob reads, backend CPU/network and potentially Cosmos reads | Full app download blocked; evidence files persisted locally |
| Independent result-equivalence checks | None unless a separate AI reviewer is deliberately added | Local/native SQL engines or separately billed Azure database test engines | SQLite synthetic comparison only |
| Identity and access | None | Entra authentication and additive RBAC; no API keys | Entra-only calls verified |
| Observability | None for telemetry storage | Optional Application Insights/Log Analytics ingestion and retention | Local evidence only; no PTU utilization telemetry |

- **No PTU dependency for correctness.** Successful components used pay-as-you-go
  GlobalStandard, not provisioned capacity.
- Migrator, picker, syntax-checker inference, fixer and semantic-verifier model
  steps are potential PTU-covered inference **only when routed to a supported
  provisioned model deployment**. One file is not one model request; tool
  continuations and retries add inference work.
- Local T-SQL parsing, Python orchestration and browser hosting are not PTU work.
- Cosmos RU/s + storage or Serverless RU/GB; Blob GB/transactions; Container Apps
  CPU/memory/replica time; ACR SKU/build/storage; monitoring ingestion/retention;
  network transfer; and any separate SQL test engine are **not covered by PTUs**.
- Native full-app hosting avoids ACA/ACR charges but still needs real persistence.
  Default Azure template has two ACA services with min replica 1 (backend 1 vCPU /
  2 GiB), ACR, Storage and Cosmos; do not treat its cost as model tokens alone.
- This four-request sample is insufficient for PTU sizing, utilization, latency
  SLOs or break-even economics. No PTU/GPU/VM/premium infrastructure purchased.

### Actual resource and cost envelope

| Resource | Actual configuration/state | NonPTU cost driver |
|---|---|---|
| `rg-ptu-modernize-demo` | Canada Central resource-group metadata | No resource-group meter |
| `stptumodernize0911pv` | Canada Central StorageV2 Standard_LRS Hot; private container; public network Disabled | Stored GB, Blob operations, transfer |
| `cosmos-ptu-modernize-eus20911` | Single-region East US 2 NoSQL Serverless; database + 3 native containers; Entra-only | Consumed RU, stored GB, transfer; no provisioned RU/s allocation |
| `cosmos-ptu-modernize-0911` | Canada Central failed provisioning; retained | No useful capacity established; billing status not assumed free, verify cost records |
| `edcfoundryhack01` / `edc-hack-proj` | Reused Canada East account/project; existing GPT-5.1 GlobalStandard | Actual model tokens and any applicable service meters; not provisioned inference |
| Native UI/API/worker/parser | Local Windows processes only; no ACA/ACR/VM/AKS | Local machine CPU/memory; no new Azure hosting meter |

The planning envelope was approximately **$0.01/hour for tiny persistence usage**
at ≤10k Cosmos RU/hour, ≤1 GB in each storage service, and ≤1,000 Blob operations/hour.
That was an illustrative estimate, not a verified regional quote or enforced spend
cap. A direct regional Retail Prices API query timed out; no invoice, actual Cosmos
RU consumption, storage bill or verified East US 2 cost is claimed. Model tokens
are measured separately below the fixed 12-request ceiling. No automatic cleanup
or Azure deletion occurred; retained resource IDs and agent/thread IDs remain in evidence.

### Current sizing reference, not a PTU test

[Microsoft Learn PTU sizing, updated September 11, 2026](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing)
explicitly includes GPT-5.1 and GPT-4.1-mini. Model-level PTU availability must not
be confused with end-to-end compatibility of every classic Agent API feature.
The table lists **GPT-5.1 input TPM/PTU 4,750 and output-to-input ratio 8**, versus
**GPT-4.1-mini input TPM/PTU 14,900 and ratio 4**. These are model-specific sizing
parameters, **not a universal fixed “tokens per PTU” conversion**.

Sizing requires representative peak model-call RPM, input/output distributions,
cache rate, deployment type, minimum deployment size and scale increment. The
current formula is normalized TPM = uncached input TPM + model-specific ratio ×
output TPM. No peak workload estimate or actual provisioned benchmark exists for
this evaluation, so **no required PTU count, savings or capacity claim is made**.

## Deployment friction, alternatives and limitations

1. **Official native path investigated:** `docs/LocalDevelopmentSetup.md` documents
   Python/React local execution but still uses Azure Cosmos and Blob. Env fields
   configure existing services. Full deployment now waits on a policy-compliant
   client-to-persistence network path, not regional provisioning.
2. **Official Docker path investigated:** compose exposes 8000/3000 publicly by
   default and only forwards connection strings, whereas current clients use
   identity/account/database settings. It is not a documented no-Azure emulator
   stack and does not remove the same persistence dependency. Not launched as-is.
3. **Agent-component fallback executed:** exact Migrator protocol plus native
   parser and SQLite synthetic checks. Explicitly narrower than full deployment.
4. Source reuse docs specify `AZURE_EXISTING_AI_PROJECT_RESOURCE_ID`; the current
   parameters file reads `AZURE_EXISTING_AIPROJECT_RESOURCE_ID`. No speculative
   IaC patch was made.
5. Source env sample omits required `AI_PROJECT_ENDPOINT`. The source native
   frontend server has a supported runtime `API_URL` route and avoids Vite proxy
   default-port/path mismatches.
6. App `/health` can report healthy after agent initialization failure. Never use
   that endpoint alone to count this accelerator as deployed.
7. The source's broad exception path could reach nonempty placeholder validation.
   The tightly authorized three-line production fix is applied locally and the
   complete 11-test conversion-module suite passes; no upstream commit was made.
8. [Current Microsoft model/region documentation](https://learn.microsoft.com/en-us/azure/foundry-classic/agents/concepts/model-region-support)
   says classic agents retire March 31, 2027 and directs later-than-GPT-5 workloads
   to the new service. It lists PTU-supported combinations but does not establish
   this exact GPT-5.1 classic combination as a supported long-term production
   target. The repository default and observed successful calls differ from that
   support matrix; resolve this before recommending production deployment.

## Processes, endpoints and reproduction

Active preparation commands (attached tool sessions, not detached):

- `modernize-deps`: isolated venv `%LOCALAPPDATA%\ptu-modernize-venv`, official
  `pip install -r <repo>\src\backend\requirements.txt`; **completed, exit 0**.
- `modernize-ui-build`: `npm ci --no-audit --no-fund` completed (486 packages,
  approximately 25 minutes); `npm run build` **passed**, 5,936 modules transformed
  in 11m 47s. Output JS 1,687.06 kB / 488.91 kB gzip, with a large-chunk warning.
- `modernize-protocol-eval`: completed; four live calls.
- `modernize-backend`: original FastAPI/SQL agents with runtime-only identity,
  global transport call guard, retry limit and no-auto-delete safeguards. First
  startup returned healthy HTTP 200 but agent initialization failed on transient DNS;
  subsequent socket/requests/aiohttp probes succeeded and one startup retry
  **initialized all five original SQL agents successfully**. Current PID 28980;
  `/eval/status` HTTP 200 confirms 4 total model calls / 8 remaining. The process
  uses the new East US 2 Cosmos endpoint, not the failed Canadian account.
- `modernize-frontend`: original `frontend_server.py` serving built React assets;
  **HTTP 200** for `/` and `/config`, PID **34380**, with `API_URL=http://127.0.0.1:8114`.

Reserved local URLs `http://127.0.0.1:8114` (API) and
`http://127.0.0.1:5114` (UI) are running; health is not equivalent to a
functional Cosmos-backed batch workflow.
Model-consuming routes are protected by loopback-only ingress. The original
development identity mode is not suitable for public hosting. Runtime adapters
use async AzureCliCredential for async clients, zero SDK retries, a global
transport-level attempt counter, and no-auto-delete guards; persistence clients
and the original batch worker are not replaced with mocks.

From the bundle directory:

```powershell
# No model calls:
python .\scripts\modernize_sql_validation.py
python .\scripts\modernize_validation_unit.py --after-fix

# Start original backend (only if its existing process has been stopped):
& "$env:LOCALAPPDATA\ptu-modernize-venv\Scripts\python.exe" .\scripts\modernize_native.py

# In a separate shell, original built frontend:
$env:API_URL = 'http://127.0.0.1:8114'
$env:ENABLE_AUTH = 'false'
Set-Location 'C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\Modernize-your-code-solution-accelerator\src\frontend'
& "$env:LOCALAPPDATA\ptu-modernize-venv\Scripts\python.exe" -m uvicorn frontend_server:app --host 127.0.0.1 --port 5114 --workers 1

# Only after approved connectivity, with >=6 calls remaining, from the bundle:
& "$env:LOCALAPPDATA\ptu-modernize-venv\Scripts\python.exe" .\scripts\modernize_browser_eval.py
# Currently exits at real persistence preflight, before any model request.
# If native-e2e.json ever says processing_clicked=true, do NOT repeat blindly.
```

The protocol evaluator refuses accidental repeat model runs when its ledger has
calls. Identity is read at runtime; no credential, token, connection string or
secret `.env` is written into the repo, OneDrive or reports.

**Recommendation: Investigate / blocked for full deployment.** Useful SQL
candidate generation and malformed-input handling were demonstrated, and the
failure-placeholder defect is fixed locally. A governance-approved connectivity
decision, successful actual batch workflow, supported classic/new-agent strategy,
and procedure interface preservation remain gates. Neither PTUs nor more model
allowance would resolve the present network blocker.
