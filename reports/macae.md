# MACAE — verified partial native cloud workflow; inference disabled

## Final outcome — native advisory run hit24/24; no successful final synthesis

**Honest budget stop, not a completed advisory workflow.** The approved
fallback ran through native new-team RAI, upload, selection, request RAI,
scope classification, facts/planning, explicit approval and specialist
execution. It returned a **native terminal `status: error`** after consuming
**24/24 total upstream attempts**. No request beyond24 was sent.
Inference was disarmed and min0/max1 restored after that terminal error.
**At03:06:27 UTC, zero replicas and no local listeners were verified** on
paused revision `ptu-macae--0000010`; see `cloud-final-state.json`.

### Exact scope and expected-versus-actual

This was a **two-specialist, read-only advisory checklist**, not enterprise
provisioning and not the original full three-domain onboarding workflow:
`HRComplianceReviewer` covered HR/policy checks and `ITReadinessReviewer`
covered device/MFA readiness. Tools, file search, KB search, coding and
clarification flags were all false. No accounts, access grants, employee
records or business transactions were changed.

Offline inspection of the exact new-team upload path found an additional
configuration RAI call. A fresh three-specialist run therefore needs at least13
new calls including upload; the authorized two-specialist fallback needs11,
leaving one retry buffer under the12 additional attempts. The new configuration
was uploaded **without `team_id`**, preserving that native RAI check rather than
taking the update-path exemption.

| Check | Actual result |
|---|---|
| Native configuration RAI/upload, selection and request | **PASS:** native routes returned200; both RAI stages retained |
| Real plan serialization | **PASS live:** structured JSON with exactly two advisory assessment steps, not a dataclass repr |
| Explicit approval | **PASS:** inspected real plan, then submitted `approved=true`; native response `approval recorded` |
| IT advisory response | Produced a substantive review identifying pending MFA and the prepared Windows11 laptop |
| HR/compliance factual fidelity | **FAIL:** claimed no evidence of handbook acknowledgement and training completion, although both were explicitly supplied as2026-09-30 |
| Specialist routing | HR/compliance was invoked twice; IT once. The additional HR response/routing consumed the available buffer |
| Final native synthesis | **NOT COMPLETED:** terminal `status: error`, generic `Connection error` at the persistent budget boundary |
| Full original onboarding / RFP grounding / cloud browser | Remain partially verified, blocked or unverified as documented below; not claimed successful by this advisory run |

The handbook/training findings conflict with the submitted completion dates at
the **application input/output level**. Exact specialist messages were not
captured, so this is not proof of model-only hallucination or deterministic
handoff loss. Effective runtime instructions are also unavailable.

**Orientation correction:** the answer says it was not scheduled **on the
required start date**, which is consistent with the supplied2026-10-02 booking
being one day late. This does not necessarily deny that a booking exists and
is not a separate established factual error. Missing manager access approval
was also a genuine supplied gap; plan approval did not change it.
No speculative context fix or additional model request was attempted.

### Bounded root-cause review - six focused lookups, no new execution

The saved approval plan's `user_request` exactly retains the request, including
handbook acknowledgement and training completion on2026-09-30 before the
2026-10-01 start. Its separate `facts` field is empty, but there is no evidence
that this field was the specialist's actual input or caused a loss. Saved
streaming events contain only agent name, output content and finality; no
actual specialist messages or manager routing instructions were captured.
The bounded source inspection did not prove a deterministic handoff bug.

The reviewed custom HR instructions require using supplied facts/policies and
distinguishing satisfied requirements. They do **not** require documentary
evidence. An unseen effective instruction cannot be conclusively excluded.
Both specialists had tool/KB/file-search flags disabled, and no conflicting
demo-tool input/output is present in this advisory evidence. Original onboarding
demo outputs are not this different session's ground truth.

**Conclusion:** an application-level handbook/training fact-utilization mismatch
is established; dropped context, conflicting tool truth, a documentary policy,
and model reasoning are not interchangeable explanations. Context loss and
model-only hallucination remain unproved. No application/framework fix,
policy change, answer rewrite or live retest was justified or performed.
Raw outputs and all24 records remain unchanged.

**Minimum future plan, not current authorization:** first capture or locally
mock exact synthetic specialist messages and effective instructions with zero
model calls. With an unchanged, previously RAI-checked team selected natively,
the first HR response has a **six-call structural floor** (seven if fresh
configuration upload is needed), retaining request RAI, scope/facts/planning,
explicit approval and routing. That is only a partial diagnostic. A complete
two-specialist run has a **ten/eleven-call floor**, not a guarantee: the prior
twelve-call continuation exhausted its budget after repeated HR routing.
Any live diagnostic/retest needs a newly authorized allowance and restart;
the current ledger remains exhausted and inference disarmed.

Detailed evidence: `evidence\macae\advisory-root-cause-review.json`.

The same healthy replica was retained from planning through the terminal event:
revision `ptu-macae--0000009`,
replica `ptu-macae--0000009-6bc957fc4d-gvxw6`.
Session `ptu-macae-advisory-cae0694a`;
team `4ee7ecb7-8c4e-49b6-a6ac-9d033de2eb26`;
plan `3692c5c0-3107-4c1e-ae57-1b72c9c0f110`;
approval ID `8311b6b0-ed92-46a3-98f1-427ceb2f372d`.

### Final usage and independent Azure cross-check

| Scope | Actual requests / requested models | Captured usage |
|---|---|---|
| New advisory attempt | **12**: GPT-5.4 ×2, GPT-5.4-mini ×10; all HTTP200 | **16,200 input /2,417 output /1,280 cached-input tokens**, returned fields captured for all12 |
| Cumulative SDK evidence | **24**: GPT-5.4 ×9, GPT-5.4-mini ×15; all HTTP200 | Partial subtotal across19 responses: **27,923 input /2,918 output /9,088 cached-input**; five historical mini responses remain uncaptured |
| Independent dedicated-account Azure metrics | **AzureOpenAIRequests24** | **ProcessedPromptTokens36,352 /GeneratedTokens3,997**; complete cached-input total unavailable |

The Azure increase from its previous12-request snapshot is exactly12 requests,
16,200 processed prompt tokens and2,417 generated tokens, matching the new SDK
subtotals. **Do not sum SDK and Azure totals.** Cache is a subset of input,
and the partial historical cache total must not be presented as complete.
The corrected observer now has **real mini usage evidence**, obtained only
while executing the native workflow, not by a telemetry-only model test.
New observer latencies were **954.47–7,091ms**, including wrapper/ledger overhead.

The original twelve records were unchanged through both authorized limit
migrations. The new allowance used two explicitly reclaimed Modernize attempts;
no portfolio cap increase or unauthorized ceiling change occurred.

New cloud image:
`sha256:edb14961ca638605bc54a1f456e1f15ddf6b08eaabf977266b9f3df193b44ad9`.
Remote ACR run **`chs` succeeded in33seconds**, uploading only a9.311KiB
six-file archive. No local build or new network/model/resource architecture
was introduced. **Ten offline budget/observer tests passed**, plus the exact
native team-parser validation and driver parsing checks. The native serializer
fix retains its39 targeted passing regressions and is now verified on a real
approval event.

Evidence: `cloud-advisory-upload.json`, `cloud-advisory-request.json`,
`cloud-advisory-plan.json`, `cloud-advisory-approval.json`,
`cloud-advisory-final.json`, `cloud-model-ledger.json`,
`azure-metrics-advisory-final.json`, `advisory-offline.json`.
The report/result do not treat the Python driver's failed completion assertion,
HTTP200 responses, or intermediate agent text as final success.

**Production/PTU assessment:** semantic correctness and bounded orchestration
remain failed acceptance criteria; adding PTUs would not fix either issue.
All inference remained GlobalStandard, with no PTU purchase/test or capacity
increase. Search Basic still costs approximatelyUSD0.101/hour while compute
pauses; shared platform/data charges and short ACR build usage remain separate.
RFP/contract service-side private egress remains **unconfigured; supported
enablement for the exact existing-account/API path is unverified**. The earlier
blanket claim that account recreation is mandatory is withdrawn. No grounding
test was performed.

### Networking classification correction - read-only, 2026-09-12

MACAE runs **local Microsoft Agent Framework orchestration in ordinary ACA**,
using `FoundryChatClient` and the project Responses API. It registers/reads
`PromptAgentDefinition` objects (`kind: prompt`), not Foundry custom-container
Hosted Agent deployments. Installed and pinned versions agree:
`agent-framework`/`agent-framework-foundry`1.6.0,
`azure-ai-projects`2.1.0 and `openai`2.34.0. Actual requests used
`/api/projects/ptu-macae-project/openai/v1/responses`.
The source constructs a local `Agent` with instructions/tools rather than
`FoundryAgent`; portal registration alone does not prove server-managed
agent-reference invocation or Data Proxy compatibility for these calls.

The native HR/IT `MCPStreamableHTTPTool` runs client-side in ACA. RFP/KB
`azure.ai.projects.models.MCPTool` definitions remain **server-side Responses
tools**, using `project_connection_id` and Search KB API2025-11-01-preview.
Calling these "hosted tools" did not make the app a Hosted Agent.

The detailed [virtual-networks how-to](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/virtual-networks)
explicitly scopes its creation-time restriction to **Hosted agents**.
The [networking deep dive](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agents-networking-deep-dive)
distinguishes prompt-agent Tools Service/Data Proxy routing from the Hosted
Agent Micro VM `/invoke` path. Broader overview wording does not establish
mandatory recreation for MACAE, nor does this distinction alone prove retrofit
support.

Three read-only ARM GETs found `networkInjections: null`, no account capability
hosts and no project capability hosts. Foundry remained PNA Enabled with
`disableLocalAuth: true`; Cosmos/Blob/Search remain PNA Disabled. These are
**missing-configuration observations, not proof of immutability**.

**Documented existing-account candidate, not a verified fix:** the official
[standard-setup sample](https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep/15-private-network-standard-agent-setup)
has a BYO account capability-host module using `capabilityHostKind: Agents`
and `customerSubnet`, and an in-place `add-existing-project.bicep` flow.
However, the latter requires prior account-level injection; the existing-account
identity module does not add it. The sample alone does not prove this precise
Responses/managed Search MCP path works.

The bounded proposal is to **reuse this account, project, models and own data
services**, first confirming support for the existing-account capability-host
route, exact Responses/KB API, Serverless Cosmos, Basic Search, cross-region
connectivity, project identity permissions and Data Proxy costs. Only with
separate approval would it add one dedicated delegated agent subnet
(minimum/27 evaluation; not the ACA subnet), one absent account capability host,
three AAD backing-service connections, one project capability host, required
scoped roles, and up to two matching native KB MCP connections. Existing data
PEs/DNS would be reused. This is **not yet a complete costed deployment**.

No new account/project/model is presumed necessary. Do not execute the full
sample's defaults, enable local auth, weaken PNA, use trusted-service bypass,
or substitute a client-side/proxy grounding implementation. An inbound Foundry
PE alone is not an outbound tool path. Current Foundry IQ tutorials use a newer
KB API and their Search-to-Blob/Foundry direction must not be confused with
Foundry-to-Search.

Evidence and source SHAs: `evidence\macae\network-agent-type-correction.json`.
This correction made **zero model calls, zero Azure mutations and no runtime
restart**. It supersedes earlier networking inferences, not historical workflow
results or the24/24 ledger. The last runtime observation remains03:06:27 UTC;
it was not refreshed by this documentation review.

## Historical continuation outcome — approved total22 before reclaimed allowance

**Native serializer fixed and deployed; no additional model calls spent.**
The22-total ceiling was applied atomically to the existing Cosmos ledger:
used12 stayed12, and all twelve historical records have identical before/after
SHA256 `447797ea758dfa959bab5264f339a1a66ea386bf689fd251eca7e346cea81dc5`.
**Ten attempts remain allocated, not exhausted.** Inference remains disabled
and min0/max1 is configured; the final actual replica observation is in
`cloud-final-state.json` and the current `result.json`. **At02:34:17 UTC,
revision `ptu-macae--0000007` had zero replicas and no local port listeners.**

### Why a successful new three-specialist run was not launched

The original workflow cannot be resumed through the current native deployment.
`orchestration_manager.py` constructs **InMemoryCheckpointStorage**; workflow
objects, pending approvals and running tasks are process-local dictionaries.
Its resume loop supplies responses to that same living workflow object.
The original replica was replaced. Cosmos plans/conversation records are not
serialized framework checkpoints, and the native router has no persisted
checkpoint restore path. Rebuilding a checkpoint from transcripts would invent
unverified state and was not attempted.

The smallest selected fallback is a **read-only HR/IT/compliance onboarding
readiness review**, with three distinct native configured agents, complete
synthetic inputs, no MCP actions and no clarification. Even that path needs
**at least12 new model attempts**:

| Native operation | Minimum attempts |
|---|---:|
| API RAI check and native team-scope classifier | 2 |
| StandardMagenticManager facts and plan generation | 2 |
| Routing each of the three specialists | 3 |
| One substantive response from each specialist | 3 |
| Terminal progress/completion check | 1 |
| Native final synthesis | 1 |
| **Total before any retries, replans or tool loops** | **12** |

This follows the installed framework's `plan`, `create_progress_ledger`,
`_run_inner_loop_helper`, and `prepare_final_answer` implementation. A round
limit yields a **termination message**, not a successful synthesized result;
it is not a valid shortcut. RAI/scope gates, specialist execution, and native
final-result handling were not bypassed. No fake workflow events were emitted.

Thus the requested three-specialist completion cannot fit the remaining10.
The outstanding decision is **at least two explicitly reclaimed attempts from
another completed app**, or an explicitly reduced two-specialist scope. Twelve
is a lower bound, not a promise that retries will fit. **No unapproved increase
to24 was made**, and no allowance was wasted on a known-incomplete run.

### Delivered fix, observer verification and cloud release

`ConnectionConfig.send_status_update_async` now uses FastAPI's existing
`jsonable_encoder`, preserving nested dataclasses/Pydantic plans, enums and
dates as proper JSON. Blanket `str` fallbacks were removed; encoding failures
surface rather than becoming successful-looking events. **39 targeted native
tests passed**, including original connection behavior and new plan/replan,
clarification, datetime and error regressions.

**Nine offline observer/budget tests passed.** They verify GPT-5.4-mini returned
model/input/output/cache fields from pretty JSON and SSE, fragmented streams,
bounded capture, the22-call gate and an idempotent12→22 migration. This is
offline observer verification—not an additional live mini request.

ACR remote run **`chn` succeeded in39seconds** using an8.503KiB archive with
only six manifest-verified files. It layered the requested native source fix
and existing evaluation guard on the already verified official-backend-derived
image; original Dockerfiles/dependencies were not rebuilt or replaced.
One initial CLI pre-upload failure (`Dockerfile` resolved against the wrong
directory) was corrected with an absolute path; no further retry occurred.
**No local Docker/npm/.NET build was started.**

New backend digest:
`sha256:dc067468acd805293835c42c27969d46c301d88799ee297239eebf4140222781`.
One authenticated exec batched private MI readiness, budget migration/readback
and deployed source verification. The native serializer SHA256 matched the
locally tested source:
`ddc723d803886a9a7d9b28d99022f424ba3f7a64065a1bcaf4e9ef31b12b7721`.
Base commit remains `8ac703a71f10b622bd3c82a9cc2b5dfe921c3025`, now with two
tracked source/test changes; exact diff is `native-serialization.patch`.

### Independent account-level usage recovery

Parent Azure metrics and the final direct cross-check both report:
**AzureOpenAIRequests12; ProcessedPromptTokens20,152; GeneratedTokens1,580**.
See `azure-metrics-final.json` for the actual interval and raw values.
These account-level aggregates are independent of the SDK's partial subtotal
below. **Do not add the two sources**, assign aggregates to individual calls,
or infer a complete cached-input total. The metrics response's `cost` property
is query metadata, not an Azure currency charge.

### RFP/contract architecture inference - corrected after this checkpoint

RFP/contract agent grounding remains **blocked and unverified**. Keyword search
was an ingestion check, not a replacement native grounded workflow.
The earlier inference that a new Foundry account was mandatory is withdrawn:
MACAE uses local MAF/project Responses and prompt definitions, not a Foundry
Hosted Agent deployment. See the current networking correction above.

Official existing-account capability-host/customerSubnet and existing-project
modules provide a conditional reuse candidate, but the current account lacks
explicit injection and account/project capability hosts. The exact API/tool
compatibility, storage prerequisites and cost implications are not yet proved.
A new project or inbound AIServices PE alone is not a demonstrated fix.

No account/model recreation, PNA bypass, subnet change or additional PE was
performed for this investigation. Any implementation needs separate approval;
service-side KB model accounting also remains required before grounded testing.

Search's fixed reference remains **USD0.101/hour**, plus separately billed
shared platform/data services. The short remote build is additional metered
ACR task usage; exact invoiced cost was not measured. No PTUs or capacity
increases occurred.

## First-pass outcome — historical workflow details, superseded limits/fix status

**Partial functional success, not a completed end-to-end onboarding deployment.**
The genuine application ran on the approved MCAPS private-network platform.
Native team persistence, planning, explicit human approval, HR clarification,
and HR demonstration-tool execution worked. The persistent **12/12 live-call
cap** then prevented further inference; IT provisioning and final orchestration
did not complete. No PTUs, capacity increases, policy weakening, protected
resources, replacement generic chatbot, or duplicate cloud platform were used.

Current authoritative machine-readable result: `evidence/macae/result.json`.
Raw final settings/replicas: `evidence/macae/cloud-final-state.json`.
**Inference is disabled; scale is min0/max1.** Scale-to-zero has a 300-second
cooldown; use the timestamped replica observation rather than assuming min0
means a replica stopped immediately. **At 01:57:55 UTC, zero cloud replicas
were verified.** Local backend/UI PID15244 and MCP PID13380
were stopped; ports8111/5111 have no listeners at the final-state check.

### Functional expected-versus-actual and feature-level PTU/infra matrix

| Feature | Expected | Actual evidence / assessment | PTU dependence | Separately billed infrastructure |
|---|---|---|---|---|
| Native HR team persistence | Save/select official team | **PASS:** upload200, selection200, two official specialists | None for save/select | Cosmos Serverless, API/frontend compute |
| Planning | Produce an actionable approval-gated plan | **PARTIAL PASS:** native request200, approval event, HR/IT/manager steps; event `data` is a Python dataclass repr string, not a structured object | Model inference only; current Standard deployment worked without PTUs | Foundry/project, Cosmos, ACA |
| Human approval | Pause until tester decision | **PASS via native API:** explicit inspected-plan approval200; continuation then asked HR clarification. Cloud browser approval not verified | Approval/wait itself has no PTU use; continuation reasoning does | API/WebSocket, Cosmos, frontend |
| HR onboarding | Clarify missing inputs and execute actions | **PARTIAL PASS:** clarification200; agent reported background check, orientation, handbook, benefits, payroll, mentor and ID-card actions; MCP logs corroborated seven action requests | GPT-5.4 reasoning used Standard inference; tool execution itself is not PTU inference | Internal MCP, ACA, Cosmos; real enterprise HR integrations absent |
| IT onboarding / final consolidation | Finish IT tasks and a successful overall result | **BLOCKED:** final error after the twelve-call gate. No verified IT provisioning or final successful workflow | Further model calls require new allowance | Same compute/data services; future real IT systems |
| RFP/contract ingestion | Store and index two tiny synthetic documents | **PASS with disclosed MI adaptation:** native `index_datasets.py`, one695-byte RFP and one651-byte contract; each index has one document and matches keyword `Canada`; replay did not duplicate IDs | **Zero model calls**, no embeddings in this native text-ingestion path | Blob Standard_LRS, Search Basic, bootstrap compute, private endpoints |
| RFP grounding / contract conflicts | Ground claims, identify three seeded conflicts, require decision | **NOT VERIFIED:** ingestion/search is not agent grounding. Hosted Foundry KB-tool private egress and service-side call accounting remain unresolved; allowance exhausted | Agent and potential KB reasoning are inference; PTU support/sizing for exact models unverified | Search, Blob, Foundry connections/private egress, Cosmos, UI/API |
| Unavailable tool / repeatability | Deterministic blueprint and explicit unknown-tool error | **PASS at native MCP component level:** identical repeated blueprint, real ToolError for unknown tool; not a full repeated onboarding | Zero calls for these direct native tool checks | Internal MCP compute |
| Genuine UI | Build/render frontend and use cloud browser flow | **LOCAL PASS / CLOUD BLOCKED:** genuine frontend built and rendered locally; cloud frontend proxy/config verified inside container. External Python and Edge requests returned403 `RBAC: access denied` | Rendering/auth/transport are not PTU inference | ACA ingress, Entra if production auth is enabled |

The seven HR actions are the repository's **demonstration tools**, not actual
payments, employee records, hardware orders, or identity provisioning. Individual
action parameters were not separately instrumented. Nothing here is a claim
that static UI, unit tests, ARM success, or a standalone model call proves the
complete application.

### Actual model accounting

Authoritative ledger: `evidence/macae/cloud-model-ledger.json`, persisted in
Cosmos as `__ptu_macae_model_budget_v1`, partition
`__ptu_macae_evaluation__`. **Never reset or delete it.**

| Phase | Wire attempts | Requested deployments | Result |
|---|---:|---|---|
| Initial request/planning | 4 | GPT-5.4 ×1; GPT-5.4-mini ×3 | HTTP200; reached approval |
| Explicit approval continuation | 3 | GPT-5.4-mini ×1; GPT-5.4 ×2 | HTTP200; HR blueprint and clarification |
| Clarification continuation | 5 | GPT-5.4 ×4; GPT-5.4-mini ×1 | HTTP200; HR tools, then cap prevented further upstream inference |
| RFP/contract ingestion, MCP checks, readiness | 0 | None | No model inference |
| **Observed onboarding segment total** | **12** | **GPT-5.4 ×7; GPT-5.4-mini ×5** | **All twelve returned HTTP200; full workflow incomplete** |

Captured usage from the **seven GPT-5.4 responses only**: **11,723 input,
501 output, 7,808 cached input tokens**. Cached input is a subset of input, not
additional tokens. Five mini responses have **unknown/uncaptured usage**, not
zero. The evaluation observer discarded pretty-printed nonstream JSON lines;
that defect was reproduced offline and fixed in the final image. The missing
historical values cannot be reconstructed and must not be described as
service-omitted usage. No complete workload token total or model invoice is claimed.

Captured observer latencies range **1,153.69–5,049.59ms**; they include wrapper/
ledger work and are not pure model-serving latency. Raw per-call status,
deployment, token fields, timestamps, latency and error fields remain in the
ledger. The first uppercase inference-flag failure sent **zero** upstream
requests and is preserved separately as `cloud-initial-guard-failure.json`.
The final native generic “Connection error” occurred at the local budget
boundary; it is not evidence of a thirteenth upstream HTTP failure.

### Actual deployment, identity and private connectivity

- Repository unchanged at **`8ac703a71f10b622bd3c82a9cc2b5dfe921c3025`**.
- App: **`ptu-macae`**, own RG **`rg-ptu-macae-demo`**, EastUS2.
- URL: `https://ptu-macae.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`.
- Tested workflow revision: `ptu-macae--0000002`; final disabled release:
  `ptu-macae--0000005`. See final-state JSON for its replica observation.
- One Consumption app, three sidecars: frontend3000 **0.25CPU/0.5GiB**,
  backend8000 **0.5CPU/1GiB**, MCP9000 **0.25CPU/0.5GiB**.
- Sole public ingress is frontend HTTPS, restricted to parent-approved
  **174.112.74.34/32**. No public backend/MCP port. Native sample-user auth is
  disabled behind that restriction: **not production user-auth validation**.
  Shared environment PNA was read as Enabled/internal=false; the403 remains an
  unresolved evaluator-ingress issue. Its cause was not assumed or bypassed.
- Reused only parent-approved shared `cae-ptu-bundle`, Basic ACR
  `acrptubundle7d804f70`, VNet and MCAPS-local private DNS. These are **not JDCP
  hub resources** and not the earlier shared Foundry account.
- Own runtime UAMI **`id-ptu-macae`**: eight runtime/bootstrap assignments on own
  project/account, Cosmos DB, two Blob containers, own Search, and shared ACR
  pull. Exact IDs/scopes in `runtime-identity.json`; five earlier lab-user grants
  remain documented in the historical infrastructure evidence.
- Cosmos→**10.246.2.4**, Blob→**10.246.2.6**, Search→**10.246.2.20** from the
  actual cloud container; managed identity successfully accessed all three.
  Cosmos/Blob/Search PNA stays **Disabled** and local/key auth stays disabled.
- Foundry was separately verified **PNA Enabled, disableLocalAuth=true**;
  inference requires Entra identity. MACAE did not re-enable policy-disabled
  data access or create a Foundry PE. Exact final settings are in
  `cloud-service-state.json`.
- Parent created Cosmos `Sql` and Blob `blob` PEs. MACAE added only
  `pe-macae-search`, group **`searchService`**, via the approved helper.
  All PaaS client traffic uses canonical endpoints over TCP443.

| App-owned billable service | Actual SKU / region | Cost / PTU distinction |
|---|---|---|
| Foundry `ptumacae7d804f70` / `ptu-macae-project` | AIServices S0, EastUS2; Entra-only | Token inference; no PTUs bought |
| `gpt-5.4` / `gpt-5.4-mini` | GlobalStandard, capacity10 each; versions2026-03-05 /2026-03-17 | Capacity10 is **not ten PTUs**; no capacity increase |
| `ptu-macae-7d804f70-cosmos` | NoSQL Serverless, one EastUS2 region; `ptu-macae/memory` | Metered RU/storage, not included in model/PTU cost |
| `ptumacae7d804f70st` | Standard_LRS Hot, EastUS2; two private containers | Metered capacity/operations, not included in PTUs |
| `ptu-macae-7d804f70-srch` | Basic1partition/1replica, semantic free, **Canada Central** | Verified public retail reference **USD0.101/hour** (~USD73.73/730h), continues while app pauses |
| `ptu-macae` ACA | Consumption, aggregate1vCPU/2GiB when running, max1 | Fully active reference **USD0.108/hour** plus requests; no active-replica compute when actually scaled to zero |

Search EastUS2 creation failed `InsufficientResourcesAvailable`; the explicitly
approved Canada Central Basic fallback succeeded, without S1 escalation.
Cross-region Search traffic, shared Basic ACR, private endpoints/DNS,
Cosmos/Blob, model tokens, requests and any diagnostics are **separate costs**.
Prices are public retail references, not a bill or binding quote; free grants
and an exact private-endpoint/platform allocation were not assumed.

### Reproducibility, operations and limitations

`reports/macae-cloud-runbook.md` contains persistent START/PAUSE/status/build
commands. They use runtime managed identity; no secrets or connection strings
are required in OneDrive or source. Final images are digest-pinned in
`scripts/macae-cloud.parameters.json`.

The official containers are retained, with a disclosed evaluation entrypoint,
durable fail-closed ledger, and native HTTP test driver. MCP uses supported
`UV_NO_SYNC=true` and TCP9000 probes because its official `/health` is404.
Native Blob→Search bootstrap changes **only** the script's hardcoded
AzureCliCredential constructor to the supplied runtime ManagedIdentityCredential.
This is **not an unchanged stock azd deployment**.

**123 focused repository unit tests passed** earlier. **Seven additional
offline budget/observer tests passed**, including CAS/concurrency, restart
preservation, twelve-request enforcement, KB gate, pretty JSON, fragmented SSE
and bounded JSON capture. No live request was made to validate the corrected
observer after the exhausted allowance. Final image private-readiness probe
passed with inference disabled.

Health/TCP probes, console/system log access and the durable metering ledger
exist. Native `/healthz` is liveness, not dependency health. App Insights and
durable environment logging were not configured (destination read as null);
**alerts, automated production rollback, backups/restore and disaster recovery
were not deployed or validated**. `Test-MacaeRelease.ps1` offers an opt-in
previous-image rollback path and refuses to treat401/403 as a release rollback
trigger; this is prepared automation, not proven recovery.

**Production fit:** promising native multi-agent/HITL prototype, not
production-ready evidence. Resolve structured plan-event serialization,
user authentication, genuine enterprise tool integrations/idempotency,
hosted-tool private egress, complete usage capture, monitoring/recovery and
end-to-end acceptance before production. Human approval introduces idle time;
this tiny, incomplete workload is insufficient for PTU sizing or utilization
claims. Exact GPT-5.4/mini Provisioned SKU/region eligibility is unverified.
No fixed “one PTU equals N tokens” assumption is used.

**Remaining decisions:** (1) no more inference until an explicit new allowance;
a possible next bounded request is **up to12 additional attempts, total24**,
only after checking supported persisted-session resumption—not a guarantee of
completion or permission to restart/reset accounting; (2) supported
Foundry-hosted-tool private egress and service-side model accounting for
RFP/contracts; (3) verify access from the approved client without broadening
ingress or disabling policy.

References:
[PTU sizing](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing),
[Foundry networking](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/networking-options),
[Search private outbound access](https://learn.microsoft.com/en-us/azure/search/search-indexer-howto-access-private).

---

## Archived checkpoints — NOT current status or restart instructions

Everything below predates the completed private-runtime work above. Old zero-call,
running-local-process, awaiting-platform and deployment-proposal statements are
historical only. Full pre-cloud copies also exist as
`evidence/macae/report-before-private-runtime.md` and
`evidence/macae/result-before-private-runtime.json`.

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
An appropriate Foundry private egress configuration is still required.
**Correction:** the earlier blanket creation-time inference is superseded by
the current prompt/Hosted-agent classification above; existing-account
enablement is not ruled out, but this exact path is unverified. Search
also needs a supported outbound model path if Foundry becomes private. These
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
