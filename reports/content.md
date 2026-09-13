# Content Processing accelerator evaluation

## Final outcome: native missing-police case passed, with provider-filter warning

**Claim `887455af-d0bd-4a44-a9fc-8a30ab940620` completed the real native API and
full document/RAI/summary/gap workflow.** Exactly three approved documents were
submitted; the police report was intentionally absent. This is **not a
four-document happy-path pass**. No native tail was invoked manually and no
provider response or success status was replayed, rewritten or fabricated.

All three documents completed **Extract -> Map -> Evaluate -> Save**. Mapped,
evaluated and saved values match. Targeted source assertions verified:

| Document | Actual saved source fields | Native schema / entity score |
|---|---|---|
| Claim form | PTU-CONTENT-001; TEST-POLICY-001; VIN1TST23456DEMO0001; loss2026-09-01; third-party involvement; USD2500 | 0.289 /0.973 |
| Repair estimate | Same VIN/date; bumper1000; labor5 x200=1000; paint500; totalUSD2500 | 0.362 /0.951 |
| Damage diagram | 640x360; one schematic vehicle; front-left bumper damage; explicitly recognized as fictional | 0.829 /0.829 |

Native RAI returned **`{"IsNotSafe":false}`**. The persisted native summary
identifies all three filenames, consistent identifiers/amounts, and that the
police report is only referenced by number, with its contents not supplied.
The unchanged native gap output reports **one high-severity
`REQ-PR-THIRD-PARTY-006` gap, `missing_types=["police_report"]`**, with
`involves_third_party=true`; no discrepancies were reported.

**Warning preserved:** gap request45 returned HTTP200, usable native output and
usage, but also **`content_filter_error: The contents are not filtered`**.
Provider-side filtering is therefore **not verified**. Native RAI is a separate
check and does not erase this warning. The diagram is not a real photograph;
the native gap inventory counted it as one damage_photo. Scores are native
outputs, not measured extraction accuracy or photo-authenticity certification.

### Actual traffic and budget

| Native model stage | Calls | Prompt /completion tokens | Client response latency |
|---|---:|---:|---|
| Three schema/visual mappings | 3 | 22,481 /15,232 | 37.134s,52.478s,49.446s |
| RAI | 1 | 1,530 /22 | 2.396s |
| Summary | 1 | 1,697 /844 | 11.824s |
| Gaps | 1 | 46,928 /3,786 | 53.181s, provider-filter warning |
| **New total** | **6 HTTP200 responses** | **72,636 /19,884 =92,520 tokens** | No load or retries |

CU separately received **two PDF analyses and returned two
documentPagesStandard pages**. PNG routing skipped CU and used model mapping.
The native workflow reported **00:04:09.546**; control was armed05:59:21Z and
disarmed06:03:49Z.

**Budget closed at17/17 reservations:16 returned HTTP200 model responses and
one unknown outcome (reservation33).** All original33 ledger rows, including
the ten original responses and reservation33, are unchanged. Cumulative known
returned usage is **112,396 prompt /43,185 completion =155,581 tokens**;
unobserved usage for33 is not assumed zero. Cumulative CU is11 submissions,
8 successful returned pages and3 earlier rejected400 requests. The historical
Azure request metric6 versus the initial ten responses remains unresolved and
predates this run; no new metric reconciliation is claimed.

### Isolation, shutdown and Azure/PTU dependence

The earlier zero-inference isolation failure remains recorded: old revision7
made CU400 and reserved33 during the earlier rollout. For this run, **Multiple
revision mode**, idle hard-disarmed worker images, and exact native
claim/document/schema/input-hash checks prevented old work from dispatching.
Atomic stage-specific admission allowed no more than one model attempt per
logical stage and17 globally. All13 admitted messages belonged to this claim.
The **four original Map messages and one old corrupt Extract message were
explicitly deferred3600seconds without deletion**, with IDs and payload hashes
recorded. No old work consumed this run's inference budget.

**All18 retained revisions across API/Processor/Workflow/Web were inactive
with0 replicas at06:05:38Z.** Control remains disarmed; all starts are blocked
after budget exhaustion. No PaaS, networking, identity, SKU or PTU resource was
added for this attempt. Only approved remote overlay builds and owned app
revision/configuration updates were used. Base resources, four private endpoints
and shared-platform charges remain; stopping compute is not deleting them.

| Feature | Direct customer-model/PTU dependence | Required Azure infrastructure |
|---|---|---|
| Upload, schema registration, queueing | No model call; no PTU | API, Blob/Queues, Cosmos Mongo, App Configuration, Entra |
| PDF layout/table extraction | CU page charge, not a customer PTU request | CU GA AIServices EastUS2, Processor, Blob/Queues, Entra |
| Schema/visual mapping | 3 direct GPT5.1 calls; potentially PTU-eligible, not PTU-tested | Azure OpenAI, Processor, schema Cosmos/Blob, queues; Poppler |
| Confidence/evaluate/save | No new model call; depends on real mapping outputs and cached tokenizer | Processor, Blob/Queues, Cosmos Mongo |
| RAI, summary, gaps | 1 direct GPT5.1 call each; potentially PTU-eligible, not PTU-tested | Workflow, Azure OpenAI, direct Blob/Cosmos access |
| UI/hosting/authentication | No PTU requirement | Shared Consumption ACA/ACR, private network/DNS, managed identities |

This remains an **adapted private Container Apps deployment with unchanged native
processing source**, not stock Azure deployment or native-local execution.
Resources are EastUS2 with GPT5.1 GlobalStandard; no PTU purchase/utilization
test or Canadian-residency claim is made. Public browser access, the four-document
happy path and the VIN/date mismatch case remain unverified/unpassed.

**Final evidence:** `evidence/content/missing-police-native-final.json`,
raw `isolated-run-result.json`, `cloud-stop-all-all-revisions.json`, and updated
`result.json`. The raw capture includes process IDs, all saved artifacts, actual
agent text, scoped ledger and deferral logs. Eight scope checks, five hard-disarm
checks and four recorded-result regressions cover the new safeguards/acceptance;
none substitutes for the real run above.

**All sections below are earlier snapshots, not current status or authorization.**

## Historical cap17 preflight: four-document clean run not started

**The updated contract approval17 is accepted, but only6 attempts remain.**
The approval's "10 used +7" premise predates reservation33: preserved evidence
contains **11 reservations, ten returned HTTP200 responses and one unknown
provider outcome**. The original ten records remain unchanged. Reservation33
cannot be refunded simply because its response/usage was not captured.

The native four-document run requires the observed **4 mapping +RAI +summary
+gap =7 calls**. Neither rerunning claim9f9 nor creating a new claim avoids
fresh document submissions through a supported native checkpoint. A full clean
run would therefore require **total18**, one beyond approval17. The portfolio
allocation remains100 with reserve0. No extra allowance was assumed, no new
claim was created/submitted, and **no model/CU call was made for this approval**.
Zero-model recovery had already aborted; it was not an in-progress operation
that could safely continue through the failed ledger gate.

**Actual final outcome: full claim E2E remains unpassed.** Four-document success,
grounded fields and coherent native RAI/summary/gap outputs are not claimed.
All14 retained revisions across the four owned services were again verified
inactive with0 replicas at **2026-09-12T05:13:35Z**. The idle Processor image stays
hard-disarmed; the deployment interlock remains engaged. No image was rebuilt or
activated just to change its older cap12 to17.

Current details: **`evidence/content/clean-run-cap17-preflight.json`** and updated
`evidence/content/result.json`. Returned token/CU measurements below are historical
observations, not invented results from a clean run.

## Prior result: zero-model recovery aborted; all revisions stopped

The corrected scope was recovery claim **`9f9b9c98-2d6e-440f-9a67-099ffea26f51`**
only. Its bounded recovery **did not run**. The hard-disarmed idle Processor
revision8 rejected the changed live ledger before Mongo access, queue inspection
or native Evaluate/Save worker startup. Four-document recovery/field verification
and full claim E2E therefore remain **unpassed**, not fabricated successes.

**The zero-inference condition was not maintained across the rollout.** The
previous regular Processor revision **`0000007`** recorded a CU HTTP400 at
**04:33:42Z**, then model reservation **33 at04:33:43Z**. That reservation has
**no captured HTTP status, error or usage**; provider transmission/outcome and
claim association are unknown. It is conservatively charged to the budget.
The new disarmed revision itself did not start recovery. No baseline was reset,
no fake provider response or manual success was written, and no direct queue
deletion or cross-claim replay was performed. The prior revision may have
consumed retained work; its exact queue/claim effects are **unverified**, so
unchanged original Map retries cannot be promised.

**Current captured accounting: 11 model reservations; 10 returned HTTP200
responses.** The original ten rows remain identical (SHA256
`e8028913511c9377a114de8eb3100a5ebfe94d36d3dba4bffc73ef8840a8b272`).
Their returned usage remains **39,760 prompt /23,301 completion tokens**;
reservation33's unobserved usage must not be reported as zero, and these are not a verified
current provider-billed total. CU accounting is corrected to **9 submissions:
6 successful returned pages and3 HTTP400 rejections**. Besides the rollout
rejection, the live export revealed an earlier omitted corrupt-input retry at
02:42:56Z. No pages/chargeable usage were returned for the rejected requests.
CU charges remain separate from customer OpenAI usage.

Shutdown inspection also found **one older API revision still running**, despite
latest-revision-only checks reporting0. That older API and every active Content
revision were explicitly deactivated. **At04:46:48Z, all14 retained revisions
across API/Processor/Workflow/Web reported inactive with0 replicas.** Earlier
latest-only zero assertions were insufficient and are superseded by this check.
The stop script now deactivates/checks **every revision without redeployment**;
deployment fails closed while the inference-hold flag remains true. Two offline
lifecycle regressions passed. The five hard-disarm tests also passed in the new
image; they do not establish safety of an older image activated during rollout.

No further recovery or paid work is authorized. **Do not bypass the ledger
gate.** Native whole-claim rerun creates fresh process IDs/Extract messages and
does not reuse completed artifacts. Its observed path remains7 model calls;
with11 conservatively used, that would need a total ceiling18, not the earlier17.
This is accounting, **not a new allocation or request to run**.

Evidence: `evidence/content/zero-model-recovery-abort.json`,
`batch-zero-export-complete-recovery.json`, `batch-zero-exec-failure.json`,
`cloud-stop-all-all-revisions.json`, and updated `result.json`.
**Sections below are historical snapshots, not current counts or authorization.**

## Historical zero-model scope check — before corrected approval

The newly approved target was the **original claim
`77f4a16d-96fe-4739-b90a-9ac0b2597bb4`**, not the recovery claim. Recorded evidence
shows all four original documents failed **Map** on schema `BlobNotFound`
**before model invocation**; that run had zero Processor model responses.
Their IDs exactly match the four preserved **Map-queue** messages, not
Evaluate checkpoints. Evaluate requires a persisted `SchemaMappedData` artifact.
This original claim therefore cannot be recovered under the zero-model-only
constraint on the available evidence.

The persisted mappings discussed previously belong to **recovery claim
`9f9b9c98-2d6e-440f-9a67-099ffea26f51`**. That is a different scope and was not
substituted or replayed. No services were warmed, no queues/claims were modified,
and no new inference occurred during that read-only scope check. Guarded ARM
checks at **2026-09-12T04:19:15Z** returned zero for each **latest revision only**;
they did not establish all-revision shutdown, as corrected above.
The exact ten model records remain unchanged. Full claim E2E remains unpassed.
Evidence: **`evidence/content/zero-model-recovery-scope-check.json`**.

## Request-metric cross-check — saved parent snapshot

**Ten budget reservations produced ten client-observed HTTP200 model responses,
each with parsed response-body usage.** None of these ten is merely a reservation
without a returned response. The four mapping calls were not tokenizer failures
before provider transmission: Evaluate attempted the blocked tokenizer-asset GET
**after** the mapping response had been received and saved. That later asset GET
was blocked before transmission and was not counted as a model attempt.

| Response group | Client-observed HTTP200 + usage | Prompt tokens | Completion tokens |
|---|---:|---:|---:|
| Four Processor mappings | 4 | 28,260 | 17,825 |
| Six Workflow RAI/summary/gap calls | 6 | 11,500 | 5,476 |
| Total | **10** | **39,760** | **23,301** |

The parent's deployment-split snapshot independently reports
**AzureOpenAIRequests=6**, while both token totals match exactly. **The request
count difference remains unresolved; it has not been corrected or attributed
to lag as a proven cause.** For example, its `02:31Z` bucket reports
7,455 prompt /5,535 generated tokens, matching mapping ledger row26, but request
count0. Thus the six metric requests cannot simply be equated to the six
Workflow responses while discarding all four mappings.

Evidence boundary: the guard records `response.status_code` and parses usage
only after the underlying HTTPX send returns. Raw headers/Azure request IDs
were not retained, so unique server-ID reconciliation is unavailable. Token
bucket matches are corroboration, not per-request server-ID proof.
**That snapshot had10 reservations**, with no credit for the discrepancy.
The subsequent reservation33 is accounted separately above.
Exact rows and snapshot hashes: **`evidence/content/model-metric-reconciliation.json`**.

## Offline review during portfolio budget hold

**Model calls remain10/12. No new cloud operation, paid test or deployment was
performed during this review.** Additional allocation is pending redistribution
within the existing global100 ceiling, not an increase to that ceiling.

**Status interpretation clarified:** native code marks `Completed` when the
workflow graph yields output; document processing forwards per-file errors, and
RAI/summarization explicitly skip unsuccessful documents. The enum documentation
says "All stages finished successfully" but does not explicitly require every
child document to succeed. This is insufficient to establish an unambiguous
native-contract violation or justify changing native failure/partial semantics.
**Native source/status handling is unchanged. `Completed` is not clean-success
acceptance.** Earlier "false Completed" wording describes failed evaluation
acceptance, not a conclusively established native status-contract bug.

The host run-driver now **exits unsuccessfully unless every expected submitted
file is present exactly once and has `Completed` status**, with the claim itself
completed. It preserves raw responses before checking and never rewrites
application results. Missing-business-document rule checks remain separate:
three successfully processed uploads can still produce a valid missing-police
gap. **Eleven focused offline regressions passed**, including rejection of the
actual recorded `Completed` claim with four `Error` children and a no-mutation
assertion. This is a host-only change; no container rebuild/deployment was made.

Offline dependency checks reconfirmed canonical `Schemas` agreement and all four
schema-copy hashes. Tokenizer verification used the archived successful guarded
image-build check and the previously captured live police-report evaluation.
The public tokenizer asset was not cached locally, so no new tokenizer runtime
test or download was attempted. Ten model records retain their exact SHA256.
Compute and queues were untouched; the last verified replica counts remain zero.
Evidence: **`evidence/content/offline-verification.json`**.

## Current outcome — 2026-09-11 22:45 EDT

**Real CU and model processing executed, but full claim E2E has NOT passed.**
Both tested claim records reported `Completed` while their four document records
reported `Error`. This application status must not be treated as success.
All four Container Apps were freshly verified at **zero replicas** after testing.
The sections below this current outcome retain earlier deployment history.

| Measured result | Actual observation |
|---|---|
| Private AI connectivity | All three hostnames resolved privately: Cognitive Services **10.246.2.21**, OpenAI **10.246.2.22**, Foundry services **10.246.2.23**. Original Processor CU helper fetched GA2025-11-01 `prebuilt-layout` metadata **HTTP200** using its UAI. |
| Direct customer model usage | **10/12 attempts**, all HTTP200, `gpt-5.1`; **39,760 prompt + 23,301 completion = 63,061 total tokens** returned. Completion tokens already include **16,330 reasoning tokens**; do not add these twice. |
| CU usage, separately | **7 analysis submissions**: six successful one-page PDF analyses with returned `documentPagesStandard=1`, plus one rejected corrupt PDF **HTTP400**. **Six returned billable-category pages**, not model tokens. No page-usage count was returned for the rejected request. |
| Real application HTTP evidence | **68 recorded requests**, including schema/claim/file operations, status polling and result retrieval. Health/ARM success is not counted as inference success. |
| Corrupt-content flow | Real `/contentprocessor/submit` accepted truncated PDF **202**; real CU rejected it **400**; app status became **500/failed**. **Zero additional model calls.** Original unsupported/bad-magic uploads returned415. DLQ movement was not observed. |
| Full complete-claim result | **Failed acceptance**: stale/false `Completed`, document errors, and downstream summary/gap calls with no successfully completed documents. No valid complete-claim summary or discrepancy result is claimed. |

### Failures found and dependency repairs

1. **Schema prefix mismatch.** Our isolated configuration used
   `APP_COSMOS_CONTAINER_SCHEMA=ptu-content-schemas`; the API wrote schema blobs
   under that prefix, but upstream Map hardcodes case-sensitive **`Schemas`**.
   The first claim (`77f4a16d-96fe-4739-b90a-9ac0b2597bb4`) therefore extracted
   three PDFs but failed all four maps with `BlobNotFound`. Its three downstream
   model calls operated without successful document results. Four real schema
   documents/blobs were copied and verified at canonical `Schemas`, preserving
   IDs and old data. AppConfig and `content-native.bicep` now use `Schemas`;
   services were reloaded. Shared Mongo throughput remains **400 RU/s**, no autoscale.

2. **Missing tokenizer cache.** A clearly identified recovery claim
   (`9f9b9c98-2d6e-440f-9a67-099ffea26f51`) made four successful structured
   mapping calls, but Evaluate attempted tiktoken's public Blob asset download.
   The runtime endpoint guard blocked that request **before transmission**.
   Processor **r4**, remote build **chq**, precaches the official hash-verified
   `o200k_base` asset during a credential-free build. The original confidence
   evaluator passed in-image with the runtime guard enabled. A live police-report
   extract/map/evaluate result subsequently became available. Three other
   exported document-step records still held earlier errors at the last read;
   a clean full-claim rerun has not yet happened.

The second run also spent three tail calls without successful document results.
Thus the ten observed calls are **four mappings and six RAI/summary/gap calls**,
not ten successful business outcomes. No runtime endpoint allowlist, public
access restriction or authentication control was weakened; upstream application
source is unchanged. The false-`Completed` behavior remains an application risk.

### Next authorization needed — exact bounded plan

**Two model attempts remain. Request five additional attempts, raising the
lifetime cap from12 to17**, for **one clean four-document claim** after both
dependency repairs: four map + one RAI + one summary + one gap call, matching
the observed seven-call sequence. The increase is **not yet authorized or used**.
No new infrastructure is requested. Missing-police and VIN/date-mismatch variants
remain unexecuted; do not label the empty-input gap outputs as those tests.

Four original failed map messages were preserved and deferred until
**2026-09-12T04:26:20Z**. The corrupt input and unfinished retry work were not
purged. **Do not blindly warm Processor**: retained work can consume the remaining
allowance. Worker activation rules are removed and revisions deactivated.

### Current per-feature PTU and infrastructure dependence

| Feature | Required Azure components | PTU dependence and observed state |
|---|---|---|
| Schemas, claims, uploads, status | Private Blob/Queue, Mongo7 shared400RU, Entra AppConfig, local/private container services | **No PTU.** Real HTTP/data path verified; canonical schema-name dependency documented above. |
| PDF layout/text/table extraction | CU GA `prebuilt-layout`, EastUS2 AIServices S0 and private endpoint | **No customer AOAI PTU.** Six returned document pages; CU extraction charges are separate. Full table acceptance remains unverified. |
| Schema/vision mapping | Customer Azure OpenAI `gpt-5.1` GlobalStandard, model deployment and MI | **No PTU required.** Four real mapping calls succeeded; compatible provisioned deployments are a possible separate deployment choice, not tested here. |
| Confidence evaluation / save | Cached tokenizer, CPU, Blob and Mongo | **No new model call or PTU.** Build-time cache repair passed; one live evaluated output recovered. |
| RAI, summary, gaps/discrepancies | Customer Azure OpenAI plus successfully processed documents | **No PTU required.** Six calls returned tokens but lacked successful document inputs; business outcomes are not validated. |
| Browser experience | Internal API/Web Container Apps; external access needs an approved auth/ingress path | **No PTU for hosting.** Internal Web previously200; public browser walkthrough remains unverified. |

This remains an **adapted private container deployment**, not unchanged native
execution or stock Azure deployment. No PTUs were purchased or tested and no
tokens-per-PTU conversion is inferred. Known dependency baseline **$0.082/hour**
continues while compute is paused, **plus four PE endpoint/data charges**,
storage and shared-platform charges; no measured bill is available.

Authoritative current evidence: **`evidence/content/inference-result.json`** and
**`evidence/content/result.json`**. They retain request order, model, HTTP status,
elapsed time, raw returned usage, errors, claim IDs, image digests and fresh stop
state. **`reports/content-cloud-runbook.md`** has current images and restart holds.

## Pre-inference snapshot — historical

**Status: FOUR PRIVATE CONTAINER SERVICES DEPLOYED; real schema/claim-upload/negative HTTP tests passed. Full inference E2E remains blocked on the fourth AI private endpoint. All four services have now been verified at ZERO replicas after testing. Model calls0; CU analyses0.**

## Latest real execution results — supersedes earlier preparation status

The actual app now runs as an **adapted private Container Apps deployment** in
the approved shared Consumption environment. All four official source images
were built; Python runtime guards are deployed with API **`659eaa1-r3`** and
Processor/Workflow `659eaa1-r2`. API/Web ingress is **internal only**; workers have no ingress.
No public-access policy was relaxed, no app registration/admin consent was used,
and no protected endpoint was called.

### Verified service/data path

- API `/health` returned **200** with `{"message":"I'm alive!"}` through authenticated exec and through internal app-name discovery.
- Internal Web returned **200**, `nginx/1.28.3`, `text/html`. This is not a public-browser walkthrough.
- Both API and Processor identities successfully listed own Blob/Queues/AppConfig and executed real Cosmos Mongo ping (`ok:1.0`).
- Actual private DNS: **Blob10.246.2.16, Queue10.246.2.17, Mongo10.246.2.14**. All three PEs are Succeeded/Approved.
- Real Processor initialized all four pipeline queue handlers; real Workflow started its single queue worker.
- Initial API r1 failed because the upstream helper selected a nonexistent system identity. Adapter r2 explicitly binds the app's own UAI for sync/async credentials. Its runtime-only Mongo retrieval succeeded; no URI is stored in ACA secrets, AppConfig, source or logs.

### Actual application HTTP tests

| Test | Actual result | What remains unverified |
|---|---|---|
| Register four upstream schemas and Auto Claim set | **12 actual API requests, all200**; schema-set `0669038a-dcc4-46c7-b53c-1209263c070b` | Schema-driven extraction not yet invoked |
| Complete synthetic claim creation + four uploads | **PUT200 + four POST200**; claim `77f4a16d-96fe-4739-b90a-9ac0b2597bb4` | Not submitted; no CU, map, RAI, summary or gap output |
| Corrupt-input claim | PUT200; bad-magic.pdf **415**, unsupported.txt **415**, truncated.pdf **200** | Truncated file passed only the header gate; no downstream/DLQ test |
| Missing police / VIN-date mismatch / visual-table extraction | Fixtures prepared, no inference submission | All semantic outcomes remain unmeasured |

There are **21 confirmed real application HTTP requests** across these schema
and upload flows. Actual responses and elapsedMs were persisted by the driver
to owned Blob `ptu-content-configuration/evaluation/functional-results.json`.
The complete Blob evidence was **successfully recovered** through one authenticated
exec during the capture starting `2026-09-12T01:48:28Z`. All **21 actual responses**
are now local: **19 HTTP200 and two expected HTTP415**. Observed API elapsed time:
minimum **3.415 ms**, median **102.300 ms**, maximum **1,593.644 ms**; this tiny
CRUD/validation sample is not inference latency or a performance benchmark.
The earlier **429/Retry-After600** at `01:27:10Z` is retained as historical
evidence, not a current export blocker. The model-budget Blob is absent, as
expected before any guarded CU/model request; no usage has been fabricated.

### Current inference blocker and stop state

The owned AI endpoints still resolve to **public20.62.58.5**. The approved PE
helper has no `account` group/multi-zone support, so Content's fourth PE still
requires the parent to extend the helper or create it centrally. A fresh
guarded ARM check confirmed `pe-content-ai` is still **ResourceNotFound**. Target and
three exact zones are in `shared-platform-request.json`. No inference was
submitted merely to reproduce a known firewall failure.

The API hardcodes **`claim-process-queue`**. Before any submission, the Workflow
AppConfig value and KEDA plan were aligned to that exact name, confined to the
new owned account. Processor-created stage DLQs likewise remain isolated.

**All four replica counts are verified0.** Initially min0/no-rules left each
ingress-less worker with one replica; their current revisions were then
explicitly deactivated, without deleting resources or data.
`Stop-ContentCloud.ps1` now includes that step. Full startup/stop, readiness
alerting/optional automatic rollback and resume instructions are preserved in
**`reports/content-cloud-runbook.md`**.

The standing **$0.082/hour dependency estimate is not an all-in total**: the
three new private endpoints add endpoint-hour/data-processing charges, and the
parent's shared platform has its own costs. Private Link rates were not
successfully retrieved in this run and are not fabricated. All-four-active
compute scenario remains $0.216/hour before grants/request charges; actual
post-test replica count is zero.

Exact resource/image/revision configuration and ACR run digests:
**`evidence/content/cloud-application-evidence.json`**. API **r3 is published**:
remote ACR run **chb**, about **17 seconds**, a **3.184-KiB two-file context** on
the verified r2 digest. It adds durable-state recovery and duplicate-protected
existing-claim submission; no upstream application code or original-Dockerfile
base was changed. Its revision became ready and exported the stored evidence.
Only API was briefly warmed; it returned to **zero actual replicas** after its
cooldown. The three other services stayed paused. No local Docker/npm/install
workload was started. `Stop-ContentCloud.ps1 -Service api` now supports a
targeted pause without reconfiguring the already-paused workers.

## Shared private-platform handoff — 2026-09-11 20:56 EDT

**Readiness update:** parent has now confirmed the shared platform ready. Content Blob/Queue/Mongo PE creation was submitted through the approved helper and validated successfully (deployment still running at last read). First official API image build **succeeded**, ACR run **ch1**, tag `content/official-api:659eaa1`, digest `sha256:0f638fcb7e12cde55c41ea231b8d73d51c98dd18cf5f5a5b7b2e9f38e3a6e920`; 3.588-MiB isolated context uploaded. This is a base image, not yet a running/guarded app. Exact evidence: `evidence/content/cloud-build-progress.json`.

**Parent helper extension required:** the helper currently rejects groupId `account` and accepts only one `zoneName`; the verified AI endpoint needs **one account PE with three DNS zones** (`privatelink.cognitiveservices.azure.com`, `privatelink.openai.azure.com`, `privatelink.services.ai.azure.com`). This is Content's **fourth** PE, within the approved cap. No helper modification/bypass or other network write was attempted.

- Parent owns `rg-ptu-bundle-platform/eastus2`, `vnet-ptu-bundle`, `cae-ptu-bundle` and Basic `acrptubundle7d804f70`. **No Content VNet, environment, registry, DNS zone or PE has been created.** This is MCAPS, **not JDCP**; no JDCP hub/subscription is involved.
- Exact target IDs, case-sensitive group IDs and service-returned DNS requirements are in **`evidence/content/shared-platform-request.json`**. Required: Storage **blob + queue** (two PEs), Cosmos **MongoDB**, owned AI **account** (three DNS zones). AppConfig **configurationStores** is optional for a fully private path; it is currently Entra-only/public Enabled and reachable.
- All **40 nonsecret AppConfig settings now wrote successfully through Entra** after propagation. The earlier Forbidden result is historical, not a remaining configuration-write blocker. Mongo connection string remains absent.
- Four official Dockerfile/source build contexts are staged **outside OneDrive**, with source/tree/Dockerfile hashes in **`evidence/content/container-contexts.json`**. The API base image is now built/pushed as noted above; remaining builds and guarded runtime overlays are pending. `Build-ContentSharedImage.ps1` selects one service at a time and refuses action without explicit `-PlatformReady`.
- Do **not** run stock `acr_build_push.ps1`: its WAF branch relaxes ACR public networking/export restrictions and its cleanup deletes staging files. The prepared replacement does neither, uses only the parent registry, immutable SHA tags, and excludes secret environment files.
- Planned cap: API **0.25 vCPU / 0.5 GiB**, Processor **1 / 2**, Workflow **0.5 / 1**, Web **0.25 / 0.5**; max **one replica per service**, total **2 vCPU / 4 GiB** when all active. HTTP/event-compatible services min0; queue workers need managed-identity Queue scalers. API uses one Uvicorn worker instead of the stock four. Ingress remains internal/disabled until parent CIDR/auth is configured.
- All-active compute scenario is **$0.216/hour before grants/request charges**, in addition to existing dependency baseline $0.082/hour. Scale-to-zero means this is not a fixed monthly compute bill.
- Remaining runtime work before Python images may process claims: container-compatible runtime-only Mongo retrieval and **durable, atomic shared 12-call budget** across Processor/Workflow/restarts. Separate container-local SQLite counters would be unsafe and will not be used. No Mongo value may appear in ACA secrets/config, images or files.
- Per-app managed identities will get only required own-resource roles and shared-ACR pull. The built-in **Cosmos DB Account Reader Role does not grant listConnectionStrings**; runtime retrieval needs a narrowly scoped `databaseAccounts/read` + `databaseAccounts/listConnectionStrings/action` custom role assigned only at this owned Mongo account, or parent-provided equivalent.
- This fallback will be reported as an **adapted, container-hosted private deployment**, not unchanged native execution. Real E2E and usage remain pending shared platform readiness.

## Current implementation result — supersedes pre-approval notes below

The parent approved `content-native-eastus2` at **2026-09-11 20:19:24 EDT**. Deployment used the reviewed `scripts/content-native.bicep`, not stock `azd up`.

| Approved dependency | Actual deployed state / verification |
|---|---|
| Storage `stptuvcontent260911` | StorageV2 Standard_LRS Hot; three containers and six queues created; shared-key/anonymous access disabled. **Governance changed publicNetworkAccess to Disabled**, despite the requested current-client-IP restriction. Actual Blob/Queue SDK reads returned AuthorizationFailure. |
| Cosmos `cosmos-ptuv-content-260911` | Creation completed. Mongo 7.0, East US 2 only, account total-throughput limit **400**; `ptu-content-db` shared **manual 400 RU/s**, autoscale null. No application collections populated. |
| AppConfig `appcs-ptuv-content-260911` | Standard, Entra-only. Initial ARM key creation failed because data-plane proxy defaulted to local authentication. A **config-only** repair enabled Pass-through and added Data Owner at this new store only; immediate writes returned Forbidden during propagation. Later Entra SDK retry **successfully wrote all 40 nonsecret settings**. No local-auth enabling or secret settings were used. |
| Foundry `aif-ptuv-content-260911` / `ptu-content-project` | AIServices S0, Entra-only; `gpt-5.1` **2025-11-13 / GlobalStandard / capacity 50** created. Current-client-IP firewall rule retained. CU GA `prebuilt-layout` metadata GET returned **403: Access denied due to Virtual Network/Firewall rules**. No analysis/model request was attempted. |

**Exact external blocker:** management-group assignment `MCAPSGovDeployPolicies`, definition **`StorageAccount_PublicNetwork_Modify`**, display name **“SFI - Disable public network access on Storage accounts (excluding NSP configured resources)”**, performed `AddOrReplace` on `Microsoft.Storage/storageAccounts/publicNetworkAccess` at creation. Activity-log evidence is in `evidence/content/native-deployment.json`. The account now reports `Disabled`; localhost native workers cannot access Blob/Queues through the approved public-IP allowlist. No policy exemption, network bypass, private endpoint, NSP or additional compute was created. A policy-owner-approved connectivity path is needed before the real workflow can run.

**Independent host blocker:** measured available RAM fell to **0.62 GiB** (later 0.87 GiB). `Start-ContentNative.ps1` was actually invoked and **refused admission before launching services or retrieving the Mongo credential**, because it requires 5 GiB free before starting the 4-GiB-bounded stack. Other accelerators' processes were not stopped. API `127.0.0.1:8113` and Web `127.0.0.1:5113` are not live.

Implementation preserved:

- `scripts/Start-ContentNative.ps1` and `scripts/Stop-ContentNative.ps1`: attached runtime, specific owned-PID shutdown, sequential service startup; no secret-bearing `.env` or command-line credential.
- Hard **4-GiB Windows job committed-memory limit**, including descendants, plus aggregate-RSS/free-memory watchdog. Hard-job creation passed a real Windows test. No separate 1.5-GiB per-process limit is claimed.
- Persistent cross-process SQLite **12-model-request guard**, counting reservations/retries across restarts and restricting endpoints/model to the new approved account and GPT-5.1. Local MockTransport guard tests passed; these are explicitly **not** live model tests.
- Raw CU usage/page and model-token metadata capture at HTTP boundaries, without logging credentials/prompts. The only CU ledger record so far is the nonbillable analyzer-metadata GET (403).
- Actual locked Processor/Workflow model SDK imports passed. Poppler **26.07.0** installed outside OneDrive; verified archive SHA256 `a711b0563b06edc488583d28198b6734c5a494afbbd1b9d87d3d2866062fb7e2`; real `pdfinfo` reports one page for the synthetic claim PDF.
- React rebuilt successfully for `http://127.0.0.1:8113` with auth disabled **only for localhost**: gzip JS **427.76 kB**, CSS **5.42 kB**. No unusable standalone UI is represented as a completed app.
- `scripts/content-runtime/exercise_app.py` implements the actual schema-vault → schema-set → PUT claim → file uploads → POST submit → status/details API workflow. It has **not** been executed against a running app.
- Azure CLI startup measured **13.57 seconds**, exceeding the SDK default 10-second credential subprocess timeout; the runtime raises that bounded timeout to 120 seconds while preserving Entra authentication.

**Cost continuing while blocked:** approved fixed baseline **$0.082/hour** (Cosmos $0.032 + AppConfig $0.050), approximately $1.968/day, plus storage/Cosmos storage/transactions and any future model/CU usage. This is a retail estimate, **not a measured bill**. No hosting, ACR, AKS, PTUs or larger SKUs were created; no resources were deleted.

**Resume decision needed:** coordinate safe host memory and an approved, policy-compliant storage/CU connectivity path. Do not blindly redeploy the template to fight the governance policy. AppConfig writer-role propagation/settings can be rechecked within the already-approved resource envelope. Complete/missing-police/VIN-date/visual/corrupt E2E cases remain blocked; previous local validator/unit-test results below remain valid but are not E2E evidence.

## Scope and provenance

- Repository: https://github.com/microsoft/content-processing-solution-accelerator
- Clone: `C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\content-processing-solution-accelerator`
- Branch: `main`; SHA: `659eaa1f503dd08b1e1aea1c72eab11c7c191d00`
- Commit time: `2026-08-25T16:52:54+05:30`; nearest tag: `v2.1.2-123-g659eaa1`; highest fetched version tag: `v2.1.2` (not asserted to be latest GitHub release).
- Authorized subscription: `1feb53b2-854a-4ea7-b5a6-709b7d804f70`; tenant observed: `a600acd0-3028-4689-8402-3b471d7d924d`.
- Only the approved isolated resources/data-plane prerequisites and their RBAC/configuration described above were created/modified. No Azure resources were deleted. No SpecSuite or Planetary endpoints were used.
- No live inference requests were initiated. The 12-request first-pass allowance remains unused.
- Entra tokens were obtained in process memory only. The approved Mongo credential exception has not yet been exercised; no Foundry, Storage or AppConfig keys were retrieved. No secret-bearing `.env` files were created. Python environments and compiled ARM templates are outside OneDrive in `%LOCALAPPDATA%\ptu-content-eval`.
- A bounded, value-suppressing credential-pattern scan considered 701 tracked files and found no private-key/JWT/storage-key/GitHub-token patterns. This is not a comprehensive credential audit. The tracked application source remains unchanged.

### Shared safety update — 2026-09-11 20:09 EDT

- **Content Processing / accelerator=content:** all later infrastructure proposals must retain this explicit app identifier. No new infrastructure approval is implied by this report update.
- Shared account `edcfoundryhack01` has **`disableLocalAuth=true`**, as reported by the coordinator. Any later authorized access must use **Entra ID**, through `DefaultAzureCredential`/`AzureCliCredential` locally or managed identity in Azure. Do not retrieve keys or enable local authentication. Its CU regional incompatibility remains unchanged.
- The authoritative protected-resource inventory is `B\evidence\protected-resources.json`, read locally for this update: **100 records across 9 resource groups**, SHA-256 `9B151198EB9CF14CC8AACE86ADA69375240EB87823118790404662F6D67592E3`. Protection includes `specsmith-builders-rg`, `specsuite-demo-rg`, `rg-specsuite-aks-mcaps` and managed groups, in addition to the contract's protected groups. Preserve the **union** of contract protections, inventoried IDs/groups and known application associations; the inventory does not remove a contract protection.
- Use `B\Invoke-LabAz.ps1 -AzArguments <string[]>` for supported later Azure CLI actions. The guard is an additional safety check, **not billing approval**, permission to use protected endpoints, or a substitute for inspecting commands/payloads.
- Shared `edc-hack-search` is reported as **Basic, 1 partition / 1 replica**. Azure AI Search and embeddings are **not required by the inspected Content Processing claim workflow**, and that resource was not reused.

## Infrastructure decision and two deployment paths investigated

### Path 1 — documented existing Foundry reuse: rejected

`docs/re-use-foundry-project.md` documents `AZURE_EXISTING_AIPROJECT_RESOURCE_ID`, but requires the existing project region to support **both** GPT-5.1 GlobalStandard and Content Understanding GA.

Read-only ARM checks confirmed nonprotected `rg-edc-foundry-hack/edcfoundryhack01` is an `AIServices` S0 resource in **Canada East**. Its existing `gpt-5.1` is version `2025-11-13`, **GlobalStandard**, capacity 100; `gpt-4.1-mini` is also GlobalStandard; embeddings are Standard. None are PTUs. These resources were inspected only, not used.

Canada East and Canada Central are absent from both the accelerator's allowed CU regions and the current Microsoft Learn CU region list. Therefore neither setting the reuse variable nor pointing CU at that account is a supported deployment. No compatibility model call was made.

Supported CU regions verified from Microsoft Learn: Australia East, East US, East US 2, Japan East, South Central US, Southeast Asia, Sweden Central, UK South, West Europe, West US and West US 3.

### Path 2 — documented native four-service execution: real bootstrap blocked

`docs/LocalDevelopmentSetup.md` is not an offline mode: it first requires deployed Azure resources and loads settings from Azure App Configuration. It still needs Blob/Queue Storage, Cosmos Mongo, CU and Azure OpenAI.

The real API was started using its documented import path, with binding changed to `127.0.0.1:8113`. It exited with a Pydantic `ValidationError`: **APP_CONFIG_ENDPOINT is required**. No placeholder service outputs or replacement extraction workflow were introduced. An HTTP health page would not establish claim processing even if it were independently reachable.

This was the initial, pre-approval outcome. The parent subsequently approved East US 2 and GlobalStandard processing; the dedicated dependency accounts/model are now created, with external blockers detailed above.

Early proposals preceded billable creation. Parent clarified that ending a turn delivers the proposal; session UUIDs are not messageable agent IDs. Approval was subsequently received before this deployment. The initial rough stock cost floor was superseded by exact template sizing.

### Exact recommended approval request — Content Processing / accelerator=content

**Approved and implemented as dependency infrastructure; native application startup/E2E remains blocked.** The following table preserves the exact approved envelope, not an unapproved expansion.

Target tenant/subscription are the confirmed IDs above. Use new `rg-ptu-content-demo`, **East US 2**, with contract tags. Proposed globally unique names must pass availability checks; stop rather than silently change the approved plan.

| Proposed resource | Exact requested configuration | Fixed baseline |
|---|---|---:|
| `stptuvcontent260911` | StorageV2, **Standard_LRS**, Hot; blob/queues; no anonymous blobs, shared-key access disabled; Entra; restrict to current client egress where supported | Usage-based storage/transactions |
| `cosmos-ptuv-content-260911` | Cosmos Mongo **7.0**, single region; one `ptu-content-db` with shared **manual 400 RU/s**; account total-throughput ceiling **400 RU/s**; no autoscale | **$0.032/hour**, $23.36/730h |
| `appcs-ptuv-content-260911` | App Configuration **Standard**, Entra-only; **nonsecret settings only** | **$1.20/day**, $36.50/730h |
| `aif-ptuv-content-260911` | AIServices **S0**, Entra-only `disableLocalAuth=true`; project `ptu-content-project`; CU GA; deployment `gpt-5.1`, version `2025-11-13`, **GlobalStandard**, initial capacity **50** (approximately 50k TPM allocation) | Token/CU usage; no PTU reservation |

Known recurring baseline: **$59.86/730 hours**, approximately **$1.968/day**, plus storage, transactions, Cosmos storage, CU pages and model tokens; taxes/grants/discounts excluded. This is not a total-spend cap. No ACR, ACA, Search, App Service, VM, AKS, Redis, emulators or additional paid monitoring services are proposed.

Read-only preflight through the guard confirms GPT-5.1 GlobalStandard is offered in East US 2. The model metadata returns capacity default 10, but no minimum/step; initial capacity 50 remains subject to service validation. Current quota snapshot: **570/1,000** units allocated, **430** remaining. No existing deployment is resized; the proposed new allocation is 50. No model/PTU call was made.

Required explicit deviations/conditions:

- This is a reviewed **native-dependency-only provisioning adaptation**, not an unchanged `azd up`. Existing documented native application entry points and actual claim pipeline remain intact.
- Use LRS rather than stock AVM's GRS and a shared-throughput Cosmos database with an account ceiling. Microsoft documents shared Mongo throughput, but cautions against it for many production workloads; it is proposed only for these tiny sequential synthetic tests. Stop if collections cannot inherit the shared throughput; do not add dedicated collection RU/s.
- Use `ptu-content-` names for configurable data objects. Any remaining repo-hardcoded queue/collection names, notably `claimprocesses`, would be confined to the new dedicated accounts/database and require approval of that narrow prefix exception before creation; no existing resource/data reuse.
- The repo requires a **Cosmos Mongo connection string**. Obtain/inject it in process memory only; never store it in App Configuration, `.env`, source, OneDrive or logs. This is a Cosmos-specific credential requirement, **not permission to retrieve Foundry/Storage/App Configuration keys**. Stop if the coordinator requires Entra-only authentication for Cosmos Mongo as well.
- Native API binds `127.0.0.1:8113`, Web `127.0.0.1:5113`. Start services one at a time; no new image builds/emulators. Enforce a proposed 4-GiB aggregate native-process memory budget, 1.5-GiB per-process guard and free-memory admission checks before launch; do not rely on unrestricted Docker memory.
- Capture per-stage status/latency, raw CU usage and AOAI token responses locally without credentials; alert/stop on budget, memory, repeated failure or DLQ conditions. Recovery is stopping/restarting only owned PIDs with the unchanged source revision, not deleting cloud resources.
- First run: complete four-document claim, default RAI enabled. Source-derived **nominal** sequence is four map calls + RAI + summary + gap (7 model calls) and three CU PDF analyses; this is a plan, not measured traffic. Enforce **12 model calls including retries**, and stop before further variants exceed it. No PTU purchase or load test is proposed.

The local azd **1.23.7** satisfies this repository's `>=1.18.0 !=1.23.9` requirement; no update is needed. Existing builds/dependency installation are already complete. No additional large build/emulator work is needed.

## Required infrastructure versus actually provisioned

| Component | Exact inspected sandbox behavior | Provisioned by this evaluation |
|---|---|---|
| Four application services | API, Web, ContentProcessor, ContentProcessorWorkflow | None in Azure; native API attempted and exited |
| Container Apps environment | Consumption workload profile | None |
| Four Container Apps | **Each 4 vCPU / 8 GiB**, minimum 1, maximum 2 replicas by default; total minimum 16 vCPU / 32 GiB | None |
| ACR | Standard in root template | None |
| App Configuration | Standard; holds service settings including Cosmos connection configuration | None |
| Storage | Root template omits SKU; compiled AVM default is **Standard_GRS**, StorageV2, Hot, not LRS | None |
| Blob containers | `cps-configuration`, `cps-processes`, `process-batch`; created/used by app initialization | None |
| Queues | Per-step extract/map/evaluate/save queues plus claim queue and claim dead-letter queue | None |
| Cosmos DB | Mongo API 7.0, Standard RU account, `EnableMongo`; not serverless. Template database `default`; application uses `ContentProcess` and several collections | None |
| Foundry/CU | AIServices S0 with project; CU GA `2025-11-01` | None |
| Azure OpenAI | Default GPT-5.1 GlobalStandard capacity 300; **not approved**. Parameter accepts 1, but service minimum/quota remains unverified | None |
| Identities / RBAC | Application system identities, managed identities and additive service roles | None |
| Monitoring | `enableMonitoring=false` by default; Log Analytics/App Insights are conditional | None |
| WAF/private-network variant | Also creates VM/Bastion/private networking; excluded by contract | None |

This is a sample accelerator, not a preconfigured low-cost deployment. There is no documented root-template switch to omit the four hosted apps while retaining only native dependencies. A smaller persistence-only deployment, smaller containers, LRS storage, Cosmos serverless or App Configuration Free would require a separately approved, reviewed adaptation, not an assertion of faithful stock deployment.

### Fixed/recurring cost exposure

Official Azure Retail Prices API checked for East US 2, USD:

- ACR Standard registry: **$0.6666/day**.
- App Configuration Standard: **$1.20/day**.
- ACA: active vCPU **$0.000024/second**, idle vCPU **$0.000003/second**, active/idle memory **$0.000003/GiB-second**.
- At exact minimum template allocation, illustrative **730-hour** ACA compute scenarios are **$378.43 if all replicas meet idle criteria**, or **$1,261.44 if all remain active**. These are arithmetic scenarios, not measured cost, quotations, caps, or a guarantee workers qualify for idle pricing. Scaling to two replicas raises exposure.
- Cosmos provisioned-throughput collections, GRS storage/transactions, model tokens, CU pages, optional monitoring, registry storage overage and applicable environment features are additional. Cosmos throughput is not set explicitly by the app's collection creation; a reliable total requires a concrete approved resource plan.
- Free grants, negotiated discounts, taxes, exchange rates and any newly applicable environment meters are not included.

**Do not deploy the stock template under an unqualified “modest spend” assumption.** No billable infrastructure was created in this evaluation.

## Authentication, deployment hooks and operational controls

- `azure.yaml` contains a preprovision informational hook; it does not build/deploy all four application images automatically.
- Documented image path: `infra/scripts/acr_build_push.ps1` / `ACRBuildAndPushGuide.md`; then `infra/scripts/post_deployment.ps1` registers schemas and creates the schema set.
- Template first deploys hello-world images. API and Web have external ingress; Processor and Workflow are internal. Paid-operation application images must not be deployed to unrestricted external ingress.
- `docs/ConfigureAppAuthentication.md` requires Entra authentication for Web/API and corresponding registration/consent settings. Postdeployment schema registration expects API access, so ingress/auth and authenticated automation must be coordinated before paid operations.
- Proposed subsequent run: restrict API/Web ingress before replacing placeholders; use identity and Azure secret stores; enforce a shared hard request counter including SDK/queue retries; capture errors and DLQ events; add failure alerts and bounded deployment health gates. Retain the prior image/revision for non-destructive rollback. None of these hosted controls is claimed active here.
- Default monitoring is off. Claim queue retries and dead-letter implementation exist, but its live failure behavior has **not** been validated.
- Tags for any later resources must include `workload=accelerator-eval owner=parth environment=mcaps-nonprod accelerator=content protected=false`. Some nested template tag dictionaries do not automatically propagate the entire requested set.

## Actual application workflow and PTU fit

The tested codebase is the **real accelerator**, not a generic extraction substitute:

1. Register four document schemas and Auto Claim schema set.
2. **PUT** `/claimprocessor/claims` creates the claim container (the Golden Path prose incorrectly says POST; API.md/source distinguish PUT creation from POST submission).
3. POST files to `/claimprocessor/claims/{id}/files`, assigning their schemas.
4. POST `/claimprocessor/claims` submits the claim to `claim-process-queue`.
5. Workflow invokes the document processor. Each document passes **Extract → Map → Evaluate → Save**, then optional RAI, summary and gap-analysis stages run at claim level.
6. GET claim status and full results. Extracted fields, extraction/schema scores, summary and rule findings must be compared with input evidence.

Important billing distinction:

- PDFs call CU **`prebuilt-layout`**, GA API `2025-11-01`, through `:analyzeBinary` and operation polling. This content-extraction analyzer incurs **CU extraction/page charges**, not contextualization or generative LLM charges for this analyzer.
- PNG/JPEG bypass the CU extract stage in the current production handler and proceed to model mapping.
- The mapping stage invokes Azure OpenAI vision; RAI when enabled, summarization and gap analysis also invoke the configured model. These are customer deployment inference calls. Evaluate combines existing results; it is not described as another measured model call.
- CU generative analyzers in general can use customer-supplied Foundry model deployments and generate separate deployment token charges. That general GA capability does **not** establish that this accelerator's layout calls consume customer PTUs.
- CU response is parsed into a model that does not retain a `usage` member; measurement should capture the **raw response before Pydantic conversion**. Map output persists usage fields from the model response. Claim agent response usage should be captured separately at its request boundary.
- First-pass cap is **12 live model requests including retries**, not 12 claims. Multiple multi-document variants could exceed it; no load or uncapped queue retry run is authorized.

**PTU fit: potentially strong for repeated schema mapping and claim-wide reasoning, unmeasured here.** CU extraction and persistence remain separate dependencies/costs. No PTU deployment or utilization was observed. GlobalStandard is not Canadian processing residency. This is MCAPS synthetic evaluation, not a DND/JDCP deployment or accreditation.

### Per-feature PTU dependence and Azure infrastructure

**No feature requires a PTU SKU to function.** The accelerator can use non-provisioned model deployments. “Potential PTU consumer” below means that a model operation could use a compatible, explicitly configured provisioned deployment; it does not mean this evaluation used PTUs or proved accelerator PTU compatibility. All live model/CU stages remain unexecuted.

| Feature | Model / PTU dependence | Azure infrastructure and other dependencies |
|---|---|---|
| Web UI, authentication, schema/schema-set registration | **No direct PTU use.** UI/schema management does not itself invoke inference | Web/API compute (Container Apps in stock deployment); Entra registrations/authentication for public apps; App Configuration; Blob Storage and Cosmos for schema/claim state |
| Claim creation, file upload, MIME/size validation, queue submission | **No direct PTU use.** Header validation is deterministic | API compute, Blob Storage, Cosmos Mongo, Azure Queue Storage; local validator can run without Azure but is not a complete upload workflow |
| PDF text/layout/table extraction | **No customer PTU dependence in this configured path.** CU `prebuilt-layout` is an extraction-only analyzer; separate CU page charges | CU-enabled AIServices resource in supported region; Processor compute; Blob/Queue Storage; Entra access |
| PNG/JPEG extract routing | **No model call in the extract stage.** Images bypass CU; this is routing, not image understanding | Processor compute and Blob/Queue Storage; the following map stage supplies actual image interpretation |
| Schema mapping and visual field extraction | **Azure OpenAI inference required; PTU optional/potential consumer.** Default GPT-5.1 vision maps source/image content to schema | Compatible AOAI deployment and endpoint, Processor compute, source images/markdown/schema, Blob/Queues; Poppler/pdf2image for PDF rasterization |
| Evaluate/merge confidence scores | **No new model request in inspected evaluate stage.** Indirect dependency on prior CU/model outputs; no separate PTU consumption | Processor compute and saved extraction/map outputs; Blob/Queues and configuration |
| Save document results and retrieve/review/comment | **No direct PTU use.** Persistence and human review are not inference | Processor/API/Web compute, Blob Storage, Cosmos Mongo |
| Responsible-AI claim analysis, when enabled | **Azure OpenAI inference required when enabled; PTU optional/potential consumer** | Workflow compute, compatible AOAI deployment, extracted claim documents, Cosmos state; configured RAI stage |
| Cross-document summarization | **Azure OpenAI inference required; PTU optional/potential consumer** | Workflow compute, AOAI deployment, API access to processed documents, Cosmos persistence |
| Gap analysis / VIN-date discrepancy reasoning | **Azure OpenAI inference required; PTU optional/potential consumer.** YAML rules are inserted into the agent prompt, not a model-free substitute for claim reasoning | Workflow compute, AOAI deployment, processed-document API, bundled YAML/prompt rules, Cosmos persistence |
| Status polling, retries and dead-letter handling | **No inherent PTU use.** A retry that repeats an inference request can consume model capacity and counts toward the call cap | Workflow/Processor compute, Storage Queues including DLQ, API/Cosmos status; bounded retry settings |
| Monitoring, deployment and image registry | **No direct PTU use.** Observability/hosting charges remain separate | ACR, Container Apps environment, managed identities/RBAC; optional Application Insights/Log Analytics and alerts |

The stock root Bicep restricts `deploymentType` to `Standard` or `GlobalStandard`; it is not a PTU-provisioning path. Model-level PTU availability must not be confused with validation of a compatible existing-resource configuration for this accelerator.

### Model PTU availability versus actual sizing evidence

Microsoft Learn's **Determine PTU sizing for a workload**, updated September 11, 2026 and checked for this update, lists provisioned support for **GPT-5.1 `2025-11-13`** and **GPT-4.1-mini `2025-04-14`**. This confirms model-level support, **not capacity availability in this subscription/region**, suitability as a drop-in model replacement, or measured application throughput. The current accelerator defaults to GPT-5.1; no GPT-4.1-mini substitution was tested.

For these two model/version rows, the published sizing parameters are:

| Model | Input TPM/PTU parameter | Output:input normalization ratio | Global/Data Zone minimum / increment | Regional minimum / increment |
|---|---:|---:|---:|---:|
| GPT-5.1 | 4,750 | 8 | 15 / 5 PTUs | 50 / 50 PTUs |
| GPT-4.1-mini | 14,900 | 4 | 15 / 5 PTUs | 25 / 25 PTUs |

These parameters are **not** a universal “one PTU equals a fixed number of total tokens” conversion. For these models the published estimate uses uncached input TPM plus model-weighted output TPM, then divides by the model-specific input TPM/PTU parameter and rounds to the deployment's minimum/increment. Workload rate, input/output mix, cache behavior, model/version, deployment type and service availability must be accounted for. For vision input, use the model's actual image-token accounting rather than counting images as text words.

No PTU count is recommended or purchased here: returned token measurements and representative peak traffic are unavailable. **Smoke tests are not PTU tests; mocked unit tests and a successful frontend build are not PTU tests either.** An approved representative benchmark and actual provisioned-deployment telemetry would be needed for sizing/utilization conclusions. No such benchmark was run.

## Functional tests: expected versus actual

Inputs generated locally under `B\test-data\content`; 17 files including manifest. No outputs were fabricated. The vehicle image is explicitly a fictional diagram, not an authentic damage photograph.

| Test | Expected | Actual |
|---|---|---|
| Complete claim | Four schemas, source-aligned fields/summary/confidence values | **Blocked**: no configured cloud persistence/CU/model workflow |
| Missing police report | `REQ-PR-THIRD-PARTY-006` for a collision explicitly involving another party | **Blocked**. Input deliberately triggers the rule; missing police is not a universal requirement for every claim |
| VIN/date mismatch | `DISC-VEHICLE-VIN-001`, `DISC-DATE-OF-LOSS-001` | **Blocked**; mismatching source inputs prepared |
| Image/table extraction | Damage location and estimate rows/total USD 2,500 extracted accurately | **Blocked**; PDF estimate and labeled synthetic diagram prepared |
| Unsupported/corrupt | Controlled error and no false completion; malformed valid-header PDF should fail downstream or dead-letter | **Partial local validation only**: real upload function returns 415 for unsupported text and invalid PDF magic; truncated valid-header PDF is accepted by header gate. Downstream parsing/DLQ remains **unverified**, not passed |

Real production upload-validator function measurements (not HTTP or model latency):

| Input | Actual returned status | Function latency |
|---|---|---|
| unsupported.txt | 415 | 251.526 ms |
| bad-magic.pdf | 415 | 38.812 ms |
| truncated.pdf | Accepted for downstream processing; no HTTP response status | 123.425 ms |

## Local build/test evidence

- Python 3.12.10; isolated uv 0.12.10; `uv sync --locked` succeeded for API, Processor and Workflow.
- First API/Processor concurrent installations encountered 300-second shared-cache lock timeouts. API recovered with its own cache; Processor recovered after the Workflow installer released the shared cache. Dependency versions were not rewritten.
- System Node 24 is outside package engines; frontend tooling explicitly selects Node **22.22.0** and pnpm **10.28.2**.
- Initial frozen frontend install encountered Microsoft mirror socket timeouts; it was stopped and retried against public npm with bounded network retries. The retry **completed successfully, 1,527 packages installed**, preserving the lockfile.
- Real React production build **compiled successfully** using Node 22.22.0, pnpm 10.28.2, `CI=true`, `GENERATE_SOURCEMAP=false`; gzip JS 428.02 kB, CSS 5.42 kB. This does not establish backend connectivity.
- React tests: **107 test cases passed; 9 suites passed and 3 suites failed to load**, 106.917 seconds, exit 1. `useHeaderHooks`, `usePanelHooks` and `DialogComponent` suites hit the untransformed `react-router` ESM import (`Cannot use import statement outside a module`). No source/lockfile patch was applied to hide these failures.
- Bicep **0.44.1** compiled exact stock `infra/main.bicep` successfully outside OneDrive. Warnings include nullable accesses and `tag` versus `tags` on the Mongo database object. Compilation is not Azure validation or successful deployment.
- API full unit collection: **213 collected, 1 collection error**, missing `APP_CONFIG_ENDPOINT` in `app/tests/test_main.py`; exit 2.
- API retry excluding only that bootstrap test: **175 passed, 5 failed**, stopped at `--maxfail=5`, 342.38 seconds. Failures: delete-helper expectation, mocked delete route returning 500, and three fake-context `get_service` errors. These are local mocked tests, not cloud deletion operations.
- Processor full unit collection: **209 collected, 2 collection errors**, `agent_framework.openai` unavailable because the test stub makes `agent_framework` a non-package; exit 2. Isolated pipeline/CU response-model retry: **129 passed, 7 warnings in 264.02 seconds**.
- Workflow full unit suite: Windows fatal exception **0xc000070a**, exit **-1073740022**, while importing the Cosmos dependency during collection. This is recorded as a local execution failure, not proof of a cloud product failure.
- Workflow bounded utility retry: **13 passed in 33.42 seconds**.
- All **338 tracked Python files** passed AST syntax parsing without execution/imports.
- Unit commands set outbound HTTP/HTTPS proxy to loopback port 9; no Azure application configuration or model endpoint was injected. Existing repository mocks remain unit-test-only and are not represented as service responses.

## Measured traffic

- Live Azure OpenAI requests initiated: **0**.
- Live Content Understanding analyses initiated: **0**.
- Returned input/output/cached tokens: **not available** (no live response).
- Live request sequence: **empty**.
- Model/CU latency, p50/p95, throughput, 429/5xx rate, accuracy, groundedness and PTU utilization: **not measured**.
- Control-plane reads and public dependency/document retrieval are not model inference traffic.

## Reproduction and process ownership

Define:

```powershell
$R = 'C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\content-processing-solution-accelerator'
$B = 'C:\Users\partvyas\OneDrive - Microsoft\Desktop\projects\PTU accelerator Bundle'
$V = "$env:LOCALAPPDATA\ptu-content-eval"
```

For each service, set `UV_PROJECT_ENVIRONMENT` to `$V\api`, `$V\processor`, or `$V\workflow` and run:

```powershell
& "$V\tools\Scripts\uv.exe" sync --locked --python 3.12 --project "$R\src\<service>"
```

Tests: run `python -m pytest` from the corresponding service using its isolated Python and the scopes above. For the real local input validator and fixture generation:

```powershell
& "$V\processor\Scripts\python.exe" "$B\scripts\content-synthetic-samples.py"
& "$V\api\Scripts\python.exe" "$B\scripts\content-local-upload-validation.py"
```

Real API startup attempted (requires approved Azure App Configuration in runtime environment to progress):

```powershell
Set-Location "$R\src\ContentProcessorAPI"
$env:APP_ENV = 'dev'
& "$V\api\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8113 --no-access-log
```

UI intended command after dependencies/configuration: `HOST=127.0.0.1 PORT=5113 BROWSER=none pnpm start` (set those as PowerShell environment variables, not shell assignment syntax). Never use production auth-disabled public ingress.

Native API shell session **153** (launch PowerShell PID 13748) exited with code 1; it is not a running server. No cloud app URL exists. No active API/Web application PID is claimed; no listeners on 8113 or 5113 were verified. Frontend was built, not started as an unusable standalone workflow. Build/install/test command session IDs and final statuses are recorded in `result.json`; all commands completed or were stopped, and no process was detached.

## Recommendation

**Investigate / retain as a strong candidate, not deployment-ready evidence.** Approve a supported region and a concrete reduced-cost deployment plan, or explicitly approve the stock recurring exposure; then configure restricted/authenticated ingress, run one capped complete claim first, capture raw CU and AOAI usage, and request additional call allowance before more variants. Do not call this a successful deployment, a PTU utilization proof, or a Canada-resident solution.

### Authoritative references

- Repository documents at the recorded SHA: README, DeploymentGuide, LocalDevelopmentSetup, re-use-foundry-project, GoldenPathWorkflows, ProcessingPipelineApproach, API, ACRBuildAndPushGuide, ConfigureAppAuthentication, SECURITY, SUPPORT and TRANSPARENCY_FAQ.
- https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/language-region-support
- https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/pricing-explainer
- https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing
- https://prices.azure.com/api/retail/prices (East US 2 queries for Azure Container Apps, Container Registry and App Configuration).
