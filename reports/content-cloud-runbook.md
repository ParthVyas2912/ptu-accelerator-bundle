# Content Processing — private container fallback runbook

This is an **adapted private Container Apps deployment**, not unchanged native
execution or stock `azd up`. Repository SHA:
`659eaa1f503dd08b1e1aea1c72eab11c7c191d00`.

## Current hold — read before starting

**Evaluation closed at17/17 attempts. Do not activate or submit anything.**
The one authorized three-document missing-police claim
`887455af-d0bd-4a44-a9fc-8a30ab940620` completed all native stages with checked
saved source fields. Native RAI returnedIsNotSafe=false; the native gap output
identified the high-severity missing-police ruleREQ-PR-THIRD-PARTY-006.
This is not a four-document happy-path pass.

Six new HTTP200 model responses returned72,636 prompt /19,884 completion tokens.
CU returned2 pages from2 PDF analyses. The gap response also reported
`content_filter_error: The contents are not filtered`; provider filtering is not
verified. Cumulative budget remains17 reservations /16 returned responses /
one unknown reservation33, conservatively spent. No records were refunded.

**Control disarmed06:03:49Z; all18 owned revisions inactive/zero06:05:38Z.**
Use `.\scripts\Stop-ContentCloud.ps1 -Service all` for idempotent shutdown and
all-revision verification. It never redeploys or restores an older image.
`Start-ContentMissingPolice.ps1` now refuses activation when the recorded17-unit
budget is exhausted. The generic deploy interlock also remains enabled.

Successful isolated execution used Multiple revision mode, all old revisions
inactive, idle hard-disarmed supervisors, native queue receive filtering and
atomic model stage limits. Four old Map messages and one old Extract message
were logged/deferred3600seconds without deletion. The newclaim13 admitted
messages and all new inference records were scoped to the approved claim.
Do not revert to Single-mode warm-up or rearm the already-used control.
The earlier zero-inference rollout failure is retained in the incident evidence.

Artifacts: `evidence\content\missing-police-native-final.json`,
`isolated-run-result.json`, `cloud-stop-all-all-revisions.json`.
The raw file includes actual saved mappings/evaluations/results, native agent
text, per-call tokens/latency/status, and old-message deferrals.

Executed commands, **historical and not authorized to repeat**:
`Start-ContentMissingPolice.ps1 -Service api`, `invoke_isolated.py prepare`,
the separately scoped Processor/Workflow starts, then `invoke_isolated.py run`.
The driver used the native claim API and ordinary full workflow, never a manual
tail. It refuses duplicate submission/arming; the control Blob remains disarmed.
All credentials, including the narrow Mongo connection-string exception, stayed
runtime-only. No new Azure infrastructure/PTUs were created for this attempt.

### Earlier hold history (superseded by the closed result above)

**Latest approval is17 total, not12.** However,11 preserved reservations leave
only6 attempts; the native clean four-document +RAI/summary/gap path requires7.
Reservation33's unknown outcome is not grounds for a refund. Total18 is not
authorized and portfolio reserve is0. No clean claim was created/submitted and
no model/CU request was made under this approval. See
`evidence\content\clean-run-cap17-preflight.json`.

All14 retained revisions were reverified inactive/zero at **05:13:35Z**.
The deployment interlock is an operational safety hold for insufficient complete-run
headroom and the unresolved rollout incident, **not a claim that approval17 is
missing**. The deployed lower image cap12 remains unchanged because no rollout
was performed. Do not clear the interlock to force a six-call partial run.

**Do not deploy, activate or warm an app.** The corrected zero-model recovery
scope was claim **`9f9b9c98-2d6e-440f-9a67-099ffea26f51`**, but the rollout did not
maintain zero-inference isolation: previous regular Processor revision7 recorded
CU400 and unfinished model reservation33 before the disarmed revision8 controller
ran. Its ledger gate aborted before any native Evaluate/Save worker started.
Four-document recovery and full claim E2E remain unpassed. Exact claim/queue
effects of the prior revision are unknown; do not assert original77f4 Map retries
were untouched, copy artifacts across claims, redrive or delete messages.

**Budget: 11 reservations /17 allocation; 10 returned HTTP200 responses unchanged,
one unknown transmission/outcome with no captured usage.** Count reservation33
conservatively; never reset it or waive the recovery gate. Returned known usage
is39,760 prompt +23,301 completion, excluding any unobserved usage for33.
CU cumulative9 submissions returned6 successful pages and3 HTTP400 rejections.
The older Azure request metric6 versus ten returned responses remains separately
unresolved; its snapshot predates reservation33.

**All14 retained revisions of the four apps were inactive/zero at04:46:48Z.**
Earlier latest-only zero checks missed a running older API revision, now stopped.
Use `.\scripts\Stop-ContentCloud.ps1 -Service all` for repeatable shutdown:
it deactivates and checks every revision and never redeploys an image. If it
reports a still-running revision, recheck without deploying. Evidence is written
to `evidence\content\cloud-stop-all-all-revisions.json`.

`Deploy-ContentCloud.ps1` now rejects every deployment while
`evidence\content\result.json` has `modelCallsOnHold=true`. Do not clear that flag
without coordinator authorization and rollout-wide isolation. Image-local
`CONTENT_INFERENCE_DISARMED=1` does not constrain an older image that is activated
during rollout. The commands below are **historical/held**, not permission to run.

Native whole-claim rerun does not reuse finished artifacts and still follows
the observed7-call path. Eleven conservatively used plus7 would require ceiling18,
one beyond the now-approved17. No increase beyond17 is authorized. Resolve the
headroom and incident before further recovery. See
`evidence\content\zero-model-recovery-abort.json` and `content.md`.

The AI PE is now complete: all three AI hosts resolve privately to
10.246.2.21/22/23; original Processor CU metadata helper returned200 with MI.
Canonical `APP_COSMOS_CONTAINER_SCHEMA=Schemas` is required: the Processor
hardcodes this blob prefix. Existing schemas were copied/verified without
deleting old data; Mongo shared manual400RU remains unchanged.

## Ownership and safety

- Subscription: `1feb53b2-854a-4ea7-b5a6-709b7d804f70`.
- Own RG: `rg-ptu-content-demo`.
- Parent platform: `rg-ptu-bundle-platform`, `cae-ptu-bundle`, Basic
  `acrptubundle7d804f70`; do not recreate or reconfigure its network/registry.
- Storage/Cosmos PNA stays **Disabled**. No public API/Web ingress. No new Entra
  registrations/admin consent. Only synthetic claim data.
- Four app identities, each scoped to required own resources; shared ACR pull
  only. Mongo custom role grants read/listConnectionStrings at the owned account,
  not listKeys or account/network/throughput writes.
- Mongo URI is fetched by assigned managed identity and injected into process
  memory only. Never use ACA secrets, AppConfig, files or logs for that value.

## Current image set

Registry prefix: `acrptubundle7d804f70.azurecr.io/content/`.

| Service | Current image | Digest |
|---|---|---|
| API (hard-disarmed) | `eval-api:659eaa1-scope-r1` | `sha256:7d5c97ad6a055fb806e6113fde10aa91af9ee73778d008f46126bf7ef90974e9` |
| Processor (idle, hard-disarmed) | `eval-processor:659eaa1-scope-r2` | `sha256:93a1cc122f4c32dc4286012c2ed20b3810f425991c17565cb9d0ef324db88799` |
| Workflow (idle, hard-disarmed) | `eval-workflow:659eaa1-scope-r1` | `sha256:5f071948ec4baf8c5ae18a0c816fa7f7b09cae3f58959934b39a5d48ebd25194` |
| Web | `official-web:659eaa1` | `sha256:dfba6efd9fbbaa284d514b8abef752569f5bea24f265707b10c0f3e7da3762eb` |

Official Dockerfiles were retained in base images. The tiny Python overlay adds
runtime-only Mongo retrieval, redacted stdout and the shared request guard.
API uses one Uvicorn worker. Adapter r2 fixes upstream construction of
`ManagedIdentityCredential(client_id=None)` for UAI-only apps.

**Published driver-only update (remote run chb):** `exercise_app.py` now restores previous test
state from Blob after a revision restart and supports `submit` of an existing
claim with duplicate-submission protection. API r3 was built remotely from the
verified r2 digest using a two-file, 3.184-KiB source context; upstream application
source and original-Dockerfile base are unchanged. Processor/Workflow remain r2.
Do not overwrite existing tags or reset the durable budget.

API r6 retains the r3 duplicate-safe driver and adds batched orchestration,
schema-data repair and a real corrupt-file test. Processor r4 precaches the
official tiktoken asset; the runtime guard is still enabled. The build-only
download had no credentials, prompts or model requests. Original application
source remains unchanged.

## Start, readiness, stop — only after resolving the hold

Run from the bundle directory using the supplied scripts:

```powershell
.\scripts\Deploy-ContentCloud.ps1 -Service all -WarmForTest
.\scripts\Test-ContentCloudReadiness.ps1 -Service api
```

Warm mode is for bounded authenticated-exec tests only. Maximum per-service
replicas is one. Resource allocations: API0.25vCPU/0.5GiB,
Processor1vCPU/2GiB, Workflow0.5vCPU/1GiB, Web0.25vCPU/0.5GiB.

`Test-ContentCloudReadiness.ps1` alerts on bounded readiness failure. Supplying
`-PreviousKnownGoodImage <verified same-service image>` enables automatic
rollback to that image at min0/max1. No first-deployment rollback was claimed
without a known-good image. Readiness is **not** claim-processing success.

Stop after tests:

```powershell
.\scripts\Stop-ContentCloud.ps1
# If only the API was warmed for evidence export:
.\scripts\Stop-ContentCloud.ps1 -Service api
```

This preserves all resources/data/images and the durable request ledger, sets
min0/max1, removes worker queue activation rules and uses a30-second cooldown.
Actual ingress-less workers retained one replica after min0/no-rules, so the
script also **deactivates their current revisions explicitly**. Restart using
the warm deployment above, which creates an active revision; never reset budget.
Do not leave warmed workers running while waiting for networking.
Also do not leave them running while awaiting additional model allowance.
Verify actual replicas with guarded `az containerapp replica list` for each app;
min0 alone is not proof of shutdown. One pause invocation exited1 without
diagnostics; an isolated retry succeeded and fresh replica queries all returned0.

## Batched real execution and evidence

The small host wrapper uses one authenticated exec per bounded action:

```powershell
$python = "$env:LOCALAPPDATA\ptu-content-eval\api\Scripts\python.exe"
& $python .\scripts\content-runtime\invoke_cloud_batch.py preflight
& $python .\scripts\content-runtime\invoke_cloud_batch.py export
```

`run --case <case> --submit` is a paid-work submission and requires adequate
remaining authorization. Without `--submit`, `run` only polls/reads an already
submitted claim. Never bypass its persistent submission intent. The original
complete and recovery claims are already submitted.

`negative` executed the actual `/contentprocessor/submit` flow: truncated PDF
202 -> CU400 -> application500, with zero extra model requests. Its persistent
intent prevents duplicate execution. A future new clean claim needs a new,
explicitly tracked case name; do not overwrite the failed case records.

Use `capture_inference_result.py` for the current inference/stop snapshot.
Earlier preparation/native/pre-inference capture scripts are historical and
must not overwrite the current results.

### Offline acceptance checks

Native `Completed` denotes graph output in the implementation, not a proven
all-child-success guarantee. Native semantics were left unchanged because the
documentation does not resolve that distinction sufficiently. The host wrapper
now applies `claim_acceptance.assert_clean_claim` **after writing the unmodified
response**. A `run` exits nonzero for missing, duplicated, failed, nonterminal or
malformed per-document outcomes, even if the native claim says `Completed`.
Use `export` for a read-only snapshot when clean-success acceptance is not the
purpose. Per-file processing acceptance does not replace gap-rule assertions.

```powershell
& $python -m unittest discover -s .\scripts\content-runtime -p test_claim_acceptance.py -v
& $python .\scripts\content-runtime\verify_content_offline.py
```

These checks do not call Azure or models. The local tokenizer asset was absent;
cache verification therefore relies on archived build/runtime evidence rather
than a new offline encoding run. Current images and native source are unchanged.

## Earlier authenticated validation — historical

Use `Invoke-LabAz.ps1 -AzArguments <string[]>` with the authorized subscription.
Examples of the `--command` value for `az containerapp exec`:

```text
curl --silent --show-error --max-time 60 http://127.0.0.1:80/health
/app/.venv/bin/python /opt/content_eval/cloud_probe.py
/app/.venv/bin/python /opt/content_eval/exercise_app.py register
/app/.venv/bin/python /opt/content_eval/cloud_export.py
```

Do not use nested `python -c` quoting. Respect exec429 Retry-After. On
2026-09-12T01:27:10Z, the shared exec endpoint returned **429/Retry-After600**;
full evidence export was deferred rather than immediately retried.
It subsequently **succeeded** in the capture starting `2026-09-12T01:48:28Z`,
using one authenticated exec after the Retry-After interval. This is no longer
a blocker. The API r3 revision became ready; after targeted pause its observed
replica count fell from one to zero during cooldown.

Actual successful checks:

- API health and internal service-discovery health returned200.
- Internal Nginx React response returned200.
- API and Processor identities listed own Blob/Queues/AppConfig and Mongo ping
  returned `{"ok":1.0}`.
- Blob10.246.2.16, Queue10.246.2.17, Mongo10.246.2.14.
- AI endpoints still public20.62.58.5: **do not submit inference yet**.

## Resume the real claim, not a duplicate

The real API already registered four schemas and the Auto Claim schema set
`0669038a-dcc4-46c7-b53c-1209263c070b`.

- Complete claim: `77f4a16d-96fe-4739-b90a-9ac0b2597bb4`, four uploads200,
  **not submitted**.
- Corrupt-input claim: `4ca130f8-2f91-4d3b-8276-e14297e3ef91`,
  bad-magic415, truncated200(header gate), unsupported415; **not submitted**.

Before submission:

1. Parent completes fourth AI `account` PE with all three verified DNS zones.
2. Verify private AI DNS and authenticated CU metadata inside Processor.
3. Verify Workflow uses **`claim-process-queue`**, matching the API's hardcoded
   queue; this narrow naming exception remains inside the owned new account.
   AppConfig and planned KEDA rule have been aligned. Stage-specific dead-letter
   queues are also created by the real Processor automatically.
4. Use the published r3 API test-driver overlay described above, preserving
   existing claims and evidence.
5. Submit the existing complete claim once; poll within one bounded baked script
   rather than repeatedly opening exec sessions.

## Usage and durable evidence

All model requests, including retries, are admitted through an atomic Blob ETag
compare-and-swap ledger, shared across processes/replicas/restarts:

```text
stptuvcontent260911 / ptu-content-configuration /
  evaluation/content-call-budget.json
  evaluation/functional-results.json
```

The initial cap remains **12 total model requests**, not per service. Native and
cloud inference have consumed **0** so far. CU analysis count is also0. No token
counts, CU pages, accuracy or PTU utilization are inferred from health/CRUD.
CU `prebuilt-layout` page charges are separate from direct customer model tokens.

The functional Blob contains actual API responses and elapsedMs. Full contents
have now been recovered into `cloud-application-evidence.json`: 21 requests,
19 HTTP200 and two expected HTTP415. API elapsedMs min/median/max:
3.415/102.300/1593.644. These are CRUD/validation timings, not model performance.
`capture_cloud_application.py --export-only` skips repeated private-network
probes and uses a single authenticated exec for export. Do not run historical
capture modes that would replace recovered application evidence with a
deferred-export placeholder.

Standing dependency estimate: **$0.082/hour plus usage**. All four active compute
scenario: **$0.216/hour before grants/request charges**. Neither is a measured bill.
