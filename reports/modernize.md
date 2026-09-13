# Modernize Your Code — deployed; real API/worker batch passed; paused

**Result:** the adapted official cloud application completed real two-file upload
→ private Blob/Cosmos persistence → original SQL-agent processing → original ZIP
download. This is **not component-only**, but it is also **not unchanged native
deployment or a verified cloud browser journey**.

The API revision is deactivated for cost control; UI is min-zero. At
`2026-09-11T21:31:33.0134656-04:00`, **both actual app replica counts were zero**.
**Budget custody update, September 11 at 22:42 EDT:** Modernize's allocation is
closed at **10 total / 10 used / 0 remaining**. The parent reassigned its two
unused attempts to **MACAE**; the portfolio allocated ceiling remains **100**.
Verified outcomes and token usage are unchanged. Inference remains disarmed and
apps remain paused; no compute was started and no model call was made for this update.

The private Blob's historical cap of12 was **not rewritten**: it cannot be reached
from the local evaluator without reactivating in-VNet compute, which is prohibited
for this custody-only update. Its last observed guard is disarmed. Local start/eval
helpers and future runtime sources now fail closed pending **explicit new parent
budget authorization and guard reconciliation**. Existing images were not rebuilt
or redeployed. See `evidence/modernize/budget-allocation.json`.
No Azure resources were deleted. Do not reset the ledger or rerun the completed batch.

## Actual results

Batch: `8f9c942d-c1fc-42ec-a07f-00478401de98`. Authenticated Azure exec invoked the **original HTTP
routes**, worker, Azure clients and SQL agents—not a generic model script or mock
persistence. Processing took **39.060 seconds**, total API evaluation **44.148 seconds**.

| Test | Expected | Actual | Result |
|---|---|---|---|
| Two-file upload | Persist both files in one batch | Both `/api/upload` requests200; real batch/file/log records and Blob objects | PASS |
| Malformed Informix | Reject without publishing an invented target | `ptu-malformed.sql`: completed/error, one diagnostic, empty translated path; omitted from ZIP | PASS |
| Informix correlated NVL query | Translate through original orchestration | Three candidates; picker selected ISNULL variant; syntax checker and semantic verifier completed | PASS for tested normal path |
| Native syntax agent tool | Execute parser, not merely claim validation | Service run step records `SyntaxCheckerPlugin-check_syntax`, output `[]` | PASS |
| Original ZIP download | Return only successful target | HTTP200; member `rslt_ptu-nvl.sql` | PASS, API client—not browser download |
| Independent target syntax | Parse downloaded SQL | Bundled Linux T-SQL parser returned `[]` | PASS, syntax only |
| Synthetic results | Same duplicate/null/no-match row multiset | All five rows match in SQLite3.46.1 with NVL/ISNULL→COALESCE rewrites | PASS with engine limitation |
| Failure-placeholder fix | Reject empty/whitespace/`No migration`; discard partial results on communication error | Three production-line changes; complete conversion-module suite:11 passed | FIXED locally |
| Durable spending guard | Count errors/continuations and survive concurrent processes | Nine offline and Linux tests passed; real private-Blob ETag state records4+6 attempts | PASS |
| Cloud browser journey | Use approved ingress, not relax controls | Both public URLs return403 from evaluator; single-client allowlist retained | NOT VERIFIED |
| Fixer / WebSocket progress | Exercise optional branch / live UI progress | Fixer initialized but not needed; no cloud WebSocket client | NOT RUN |
| Earlier streaming procedure component | Warn about changed FOREACH/RETURN WITH RESUME interfaces | Procedure/TVF/cursor variants claimed equivalent without adequate incompatibility warning | FAIL; production gate |
| Earlier demographic schema component | Preserve harmless gender/age_group fields without inappropriate refusal | Three candidates preserved fields/filter | Narrow PASS, not a fairness audit |

The semantic verifier's equivalence judgement is **not proof**. No Informix or
SQL Server execution engine was available. SQLite does not establish dialect
equivalence, type/precision/collation compatibility, stored-procedure calling
contracts, or cross-file dependency correctness. The batch contained two
independent files, one malformed—not a complete multi-file application migration.

## Source and images

- Repo: https://github.com/microsoft/Modernize-your-code-solution-accelerator
- Commit: `7592ea97550fb711d7d8b64186875967d574c5d5`; describe `v1.9.1-57-g7592ea9`.
- Clone: `C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\Modernize-your-code-solution-accelerator`.
- Authorized uncommitted changes: three production lines in `convert_script.py`
  plus regression tests. No broad upstream refactor.
- Backend: `acrptubundle7d804f70.azurecr.io/modernize/backend:7592ea9-eval1`
  — digest `sha256:cecb00b9dc0cfeb4c1d9ccbb14c6ecb0a9ce28011ed09e824f0e2a4cdaccfe00`.
- UI: `acrptubundle7d804f70.azurecr.io/modernize/frontend:7592ea9`
  — digest `sha256:5a838547934e62d13c054560ad3c9f719a9d676f1266880c074dbe55c2dc60ef`.

The backend uses the official source/dependency/runtime steps plus async managed
identity, durable accounting, disabled automatic deletion, and executable mode
for the bundled Linux parser. Direct PyPI TLS failed; the Microsoft package mirror
worked **without disabling certificate verification**.

The official frontend container's npm install failed (“Exit handler never called”),
then Vite was missing. The working alternative packages the **already successful
original native React production build** with the original Python runtime stage.
No replacement UI was written. Asset hashes and image provenance are in
`cloud-images.json`. Build contexts excluded credentials/caches and were isolated
outside OneDrive; only Modernize tags were pushed. Local builder was capped at
2GiB/two CPUs and is stopped. Both former loopback servers are stopped.

## Endpoints, private connectivity and access

- API: https://ca-ptu-modernize-api.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io
- UI: https://ca-ptu-modernize-ui.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io
- Both were created atomically with HTTPS and **174.112.74.34/32 only**.
- Actual external probes from this evaluator returned **403 “RBAC: access denied”**.
  No allowlist expansion, policy weakening or anonymous public inference was used.
- End-user app authentication is not enabled for this IP-restricted synthetic
  demo. Runtime data/model authentication is Entra managed identity. Evaluation
  control used authenticated Azure exec.
- In-container DNS: Cosmos **10.246.2.7**, Blob **10.246.2.9**; real read/write
  and download succeeded. Both PaaS public endpoints remain **Disabled**.
- Empty initial history returned HTTP200 with a serialized404 “No batch history”
  body, an upstream response-shape quirk; after upload, actual batch history and
  detailed records were retrieved.

## Actual Azure footprint

Only subscription `1feb53b2-854a-4ea7-b5a6-709b7d804f70`, tenant
`a600acd0-3028-4689-8402-3b471d7d924d`. No SpecSuite/Planetary reuse, calls or changes.

| Resource | Configuration / region | Ownership and state |
|---|---|---|
| `rg-ptu-modernize-demo` | Canada Central RG metadata | Modernize-approved group |
| `stptumodernize0911pv` | StorageV2 Standard_LRS Hot, Canada Central | Private `ptu-modernize-files`; keys/anonymous Blob/PNA disabled |
| `cosmos-ptu-modernize-eus20911` | NoSQL Serverless, single-region East US2 | DB `ptu-modernize`; batches/files/logs containers with `/batch_id`, `/file_id`, `/log_id` |
| `cosmos-ptu-modernize-0911` | Canada Central failed regional-capacity attempt | Retained; not deleted; not used for cloud data |
| `ca-ptu-modernize-api` | Consumption0.5vCPU/1GiB, East US2 | min0/max1; latest revision deactivated; zero replicas |
| `ca-ptu-modernize-ui` | Consumption0.25vCPU/0.5GiB, East US2 | min0/max1; zero replicas |
| `id-ptu-modernize` | Backend user-assigned MI | Scoped data/model/image-pull roles |
| `id-ptu-modernize-ui` | Separate UI user-assigned MI | AcrPull only; no data/model roles |
| `pe-modernize-cosmos`, `pe-modernize-blob` | Sql and blob private endpoints | Only own new PaaS targets; parent helper/shared PE subnet |
| `cae-ptu-bundle`, `acrptubundle7d804f70` | Shared Consumption environment / Basic ACR, East US2 | Parent-created; no duplicates; registry admin disabled |
| `edcfoundryhack01` / `edc-hack-proj` | Existing Canada East Foundry | Existing GPT-5.1 `2025-11-13`, GlobalStandard capacity100 unchanged |

No new model deployment, PTUs, GPU, VM, AKS or premium tier was purchased.
Parent-managed MCAPS DNS/networking is **not JDCP**; no other-subscription hub or
protected network was used. **US compute/persistence is approved only for
synthetic MCAPS testing, not DND residency.** GlobalStandard is not a Canada-only
inference-routing guarantee.

### Access-control changes — explicitly recorded

- Earlier CLI-user Foundry User project assignment:
  `b0431624-b61b-53a6-9c75-10638628e3b6`, role
  `53ca6127-db72-4b80-b1b0-d745d6d5456d`. This was an actual shared-resource
  permission change based on the initial contract's documented additive-RBAC
  allowance. **No separate affirmative parent approval existed at that time;
  MACAE neither authorized nor executed it.** No broader authorization was inferred.
- Parent separately granted CLI-user account OpenAI User:
  `4df8a697-fc79-448a-8f0f-54f90020f5d3`; Modernize did not duplicate it.
- New backend MI client `c61fbd63-e98b-4ea2-83ff-628afbe2cfae`,
  principal `ca046adc-801d-4813-a1fe-518ce527ac4b`: own-container Blob Data
  Contributor, own-database Cosmos Data Contributor, approved-project Foundry
  User, approved-account OpenAI User and shared-registry AcrPull.
- UI MI principal `90fa0bc5-1a22-482d-b2e9-99a8d60d7299`: shared-registry
  AcrPull only. Full assignment IDs/scopes in `cloud-identities.json`;
  earlier user persistence grants in `persistence.json`.

The original network blocker is preserved in `network-policy-events.json`:
`MCAPSGovDeployPolicies` modified Cosmos/Storage public access to Disabled.
After identifying enforcement, no bypass or repeated public-enable request was
made. Parent-approved private endpoints and in-VNet compute resolved it.

## Observed inference and latency

| Phase / agent | Model HTTP actions | Service runs | Input tokens | Output tokens | Cached input |
|---|---:|---:|---:|---:|---:|
| Earlier four Migrator protocol cases | 4 | 4 | 5,054 | 1,334 | 0 |
| Cloud malformed Migrator | 1 | 1 | 1,348 | 113 | 0 |
| Cloud valid Migrator | 1 | 1 | 1,386 | 393 | 0 |
| Cloud Picker | 1 | 1 | 1,276 | 202 | 0 |
| Cloud SyntaxChecker + tool continuation | 2 | 1 | 2,678 | 152 | 0 |
| Cloud SemanticVerifier | 1 | 1 | 1,461 | 70 | 0 |
| **Total** | **10/10 current allocation** | **9** | **13,203** | **2,264** | **0** |

Total tokens **15,467**. All ten model HTTP actions returned200; no model retry,
429,5xx or failed model run was observed. Cloud five-run service durations were
4,6,4,8,3 seconds chronologically; the syntax duration includes tool waiting.
Cloud HTTP-to-response-header observations were
1.431,0.721,0.691,0.772,0.787,0.551 seconds—not pure inference latency.
The earlier protocol client elapsed times were36.875,28.031,27.031,28.078 seconds
including setup/polling. These different scopes are not a controlled performance comparison.

The durable private Blob counter reserves **before** each run/continuation send,
counts failures, uses ETag compare-and-swap, survives processes/restarts and fails
closed without Blob access. Its baseline retains the earlier four calls.
Current allocation: ten used, zero remaining, disarmed, completed batch claim retained.
The original cap12 in historical snapshots/images is not permission to use the
two attempts now assigned to MACAE.
No counter reset. Old local/component launchers refuse obsolete separate-ledger
startup after cloud evaluation. No load or provisioned-throughput test occurred.

## Per-feature PTU dependence versus other infrastructure

| Feature | PTU dependence | NonPTU infrastructure | Evidence |
|---|---|---|---|
| UI / file selection | None | Browser,0.25vCPU/0.5GiB frontend, image registry | Original assets built/rendered locally; cloud UI deployed, browser path unverified |
| Multi-file upload/history | None for storage/query operations | Blob, Cosmos RU/GB, API CPU/network, Private Link | Real two-file batch and history passed |
| Migrator candidates/input rejection | Optional provisioned inference; not required | Foundry Agent API orchestration and state | Four protocol + two cloud runs |
| Picker | Optional provisioned inference | API orchestration, state/log writes | One real cloud run |
| Syntax agent/tool continuation | Model steps optionally provisioned; parser is not | Native parser CPU plus state/network | Actual tool step and independent downloaded-target parse |
| Fixer/retries | Optional provisioned inference | CPU, repeated state writes | Initialized, not exercised |
| Semantic verifier | Optional provisioned inference; no equivalence guarantee | Orchestration/state | One real cloud run |
| WebSocket progress | None | API/network/Cosmos status | Not cloud-tested |
| SQL/ZIP download | No inference needed for packaging | Blob reads, API CPU/network | Real original ZIP API passed |
| Independent result checks | None | Native/SQLite/test-engine compute | Five-row SQLite comparison; no real target engine |
| Identity/access | None | Entra, scoped RBAC, ingress rules | Real managed-identity data/model calls |
| Observability | None | Logs/retention and local evidence storage | Service token/run-step evidence; no PTU utilization metrics |

**No functional PTU requirement:** successful runs used existing GlobalStandard
PAYG. Only model inference may be PTU-covered when routed to a supported provisioned
deployment. Cosmos RU/storage, Blob operations/GB, ACA CPU/GiB-seconds, shared ACR,
private endpoint hours/data, DNS, monitoring and transfer are **not covered by PTUs**.
Zero app replicas do not stop those retained infrastructure/storage meters.

No actual invoice, regional token-price quote or RU/GB bill was measured. The
earlier ~$0.01/hour tiny-persistence planning estimate was illustrative only,
excluding later cloud/network costs; a direct regional Retail Prices query timed
out. Do not treat it as the full deployed hourly price or a spend cap.

[Microsoft PTU sizing](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing)
includes GPT-5.1 and GPT-4.1-mini. Reference parameters: GPT-5.1 inputTPM/PTU4,750,
output/input ratio8; GPT-4.1-mini14,900 and ratio4. They are model-specific sizing
inputs, **not a universal tokens-per-PTU conversion**. This smoke sample establishes
no PTU count, utilization, break-even saving, peak capacity or latency SLO.

## Restart, evidence and recommendation

Use [modernize-cloud-runbook.md](modernize-cloud-runbook.md) for build/push,
historical reactivation, read-only inspection and pause commands. API is intentionally
paused. **Do not start it or evaluate again without an explicit new parent budget**
and reconciled guards; use the saved evidence for inspection now.

Primary evidence: `cloud-e2e.json`, `cloud-budget-snapshot.json`,
`cloud-run-audit.json`, `cloud-paused-state.json`, `cloud-images.json`,
`cloud-identities.json`, `private-endpoints-result.json`, `result.json`.
Extracted actual target: `downloaded-rslt_ptu-nvl.sql`.
Earlier four cases, nine candidate parses and three SQLite comparisons remain in
`migrator-protocol.json` / `sql-validation.json`. Historical deployment friction
is retained in `modernize-history.md`.

**Recommendation:** useful bounded MCAPS demo with real API/worker outcomes.
Before production, resolve procedure-interface preservation, actual Informix/
SQL Server engine tests, browser/user access, optional error/fixer paths, broader
fairness/performance coverage and supported agent-service lifecycle.
[Classic-agent model documentation](https://learn.microsoft.com/en-us/azure/foundry-classic/agents/concepts/model-region-support)
states retirement March31,2027 and has a GPT-5.1 support-matrix caveat despite this
repository default and observed successful calls. Observed compatibility is not
a long-term support commitment.
