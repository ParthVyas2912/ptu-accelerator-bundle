# CKM cloud restart and evidence runbook

## Current boundary

The approved private dependencies now exist and the original native persistent
workflow was exercised. **This is not full hosted Explore/browser deployment.**
The serving API now has durable native SQL/Blob/Search/MI configuration and the
direct model endpoint. Its guarded entrypoint **cannot arm inference**: budget9/9
is closed, automatic processing and queue workers are off, and all model/mutation
routes fail explicitly503. Original native read/reload handlers were verified
over real HTTP to the Uvicorn process, not TestClient.
Native KPI/narrative quality failures are preserved in
`reports\conversation.md` and `evidence\conversation\data-workflow-review.json`.

**Budget closed12 ->9:9/9 model requests used,0 reserved;3 original unused attempts
released to Content through the coordinator, not an additional release.
CKM has0 remaining allocation. Never rerun the completed passes.**
Both apps are paused, all14 retained revisions inactive/replicas0, min0/max1.
SQL is serverless min0.5/max2 with auto-pause60; final readback was Online, not
Paused. Search and four PEs continue accruing charges while app replicas stop.
No cleanup or resource deletion is authorized automatically.

- Subscription: `1feb53b2-854a-4ea7-b5a6-709b7d804f70`.
- Own RG: `rg-ptu-conversation-demo`.
- API: `ca-ptu-conversation-api`, internal8000,0.5CPU/1Gi.
- UI: `ca-ptu-conversation-ui`,80,0.25CPU/0.5Gi, exact174.112.74.34/32 Allow rule.
- Shared environment: `cae-ptu-bundle`, EastUS2 Consumption only.
- All own data/AI PNA Disabled; keys/local auth disabled where applicable.
- Four own PEs are already deployed. Do not create another or repeat old
  missing-endpoint instructions.
- MI `id-ptu-conversation` has scoped Azure roles listed in
  `storage-and-roles-final.json`; SQL contained user
  `id-ptu-conversation-runtime` has reader/writer/ddl_admin, **not db_owner or
  server-admin**.

## Images and endpoints

Current API:
`acrptubundle7d804f70.azurecr.io/conversation/api@sha256:84ff9d2a31ddf2e71a75d26ca58433ce29e41af0eb46823c0a0c5d5ca4bbcaf0`

It uses the original API/base image plus the read-only serving entrypoint,
HTTP probe and SQL diagnostic. Legacy live-model evaluator scripts are not in
this image. CMD is `uvicorn src.api.ckm_serving:app --host 0.0.0.0 --port 8000`.
The original FastAPI app and data routes are retained. No dependency reinstall
or substitute app was introduced.

UI:
`acrptubundle7d804f70.azurecr.io/conversation/ui:8a00aa5-runtime`,
digest `sha256:aa01cc8701fc0756de15a7b27a1bf6c783c1854e0641034aab2770823266edb8`.

- UI: `https://ca-ptu-conversation-ui.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`
- API: `https://ca-ptu-conversation-api.internal.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`

External root/config/proxy requests previously returned403 despite the `/32`
and matching egress lookup. Do not broaden access. Authenticated control-plane
exec works; public access is not a prerequisite for internal verification.

## Status/start/pause

From the bundle directory:

```powershell
pwsh -File .\scripts\Manage-ConversationCloud.ps1 -Action Status
pwsh -File .\scripts\Manage-ConversationCloud.ps1 -Action Start
pwsh -File .\scripts\Manage-ConversationCloud.ps1 -Action Start -WarmForExec
pwsh -File .\scripts\Manage-ConversationCloud.ps1 -Action Idle
pwsh -File .\scripts\Manage-ConversationCloud.ps1 -Action Pause
```

Start validates internal API, component-phase tag, min0/max1 and exact UI
restriction, then activates an existing ready revision. HTTP may be needed to
scale a cold replica from zero.

**WarmForExec now works through a controlled approach, not a blanket refusal.**
It leaves UI paused, stops/waits for all old API replicas0, uses Multiple revision
bookkeeping and sets API min1/max1 with concurrency5. An optional `-ApiImage`
accepts only an immutable digest in the approved own API repository.
It never enables public API ingress or inference. Data/model metadata remain
durably configured. The helper refuses an older/unverified API image; the
serving entrypoint rejects missing/disarmed-flag changes rather than starting
an unguarded app.

Single-revision mode previously reactivated older replicas during updates even
after pause. The revised helper permits at most one active revision/replica and
stops the service if reported counts exceed1. Later controlled updates passed
these checks. Multiple mode does not mean multiple replicas are authorized.

Idle restores min0 through the same stop-first/Multiple-mode procedure.
**Always follow with Pause** to deactivate the newly created revision and verify
all old and new replicas0. Status includes inactive revisions with `--all`.
No app deletion is performed.

## Durable configuration and bounded internal checks

`evidence\conversation\serving-native-config.json` contains the16 nonsecret
native/runtime settings, including owned SQL/database, Blob/container,
Search/index and managed-identity client ID. They are stored in the Container
App template, not an evaluator's environment or `.env`. The original Foundry
Agent, legacy Foundry and CU endpoint settings remain empty because those
features are unsupported/disabled. The direct OpenAI endpoint is present but
all outbound inference is blocked by immutable serving code.

The completed one-time configuration used:

```powershell
pwsh -File .\scripts\Set-ConversationServing.ps1 -Attempt 1
pwsh -File .\scripts\Invoke-ConversationServingRead.ps1 -Attempt 1
```

Both have receipts and refuse blind repetition. **Do not rerun them now.**
One of the two permitted configure/read attempts was used; no further attempt
is needed. Ordinary future restart uses the existing configuration through
`Manage-ConversationCloud.ps1 -Action Start -WarmForExec`, followed by Idle and
Pause when finished. Do not redeploy the historical component-only hosting
template or override the guarded image.

Completed evidence `serving-http-attempt-1.json` has15 expected/actual checks:
health, automation-off, native SQL refresh, list and three original records,
plus eight explicit503 model/mutation denials. Real serving PID1 differed from
the probe PID. No model dispatch occurred; all original9 requests remain the
only consumed allowance.

The older model-free SQL diagnostic remains available for an explicitly needed
future identity investigation, but it is not a substitute for serving HTTP:

```powershell
pwsh -File .\scripts\Invoke-ConversationSqlIdentity.ps1 -Mode verify
```

This selects the sole active API revision, runs the baked diagnostic through
authenticated Azure exec and records current SQL user/roles/ground truth plus
native adapter reload. Expected: `id-ptu-conversation-runtime`, db_owner0,
reader/writer/ddl_admin1, three records/two categories/one source type.
It opens SQL and can delay auto-pause; stop after the needed bounded check.

For original serving API liveness, using the actual active revision:

```powershell
.\Invoke-LabAz.ps1 -AzArguments @(
  'containerapp','exec','--name','ca-ptu-conversation-api',
  '--resource-group','rg-ptu-conversation-demo',
  '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
  '--container','api','--command',
  'curl --silent --show-error --max-time 60 http://127.0.0.1:8000/'
)
```

Liveness alone is not deep application health. This serving deployment has
already returned native `/api/health`200, `/api/ingestion/refresh`200, and all
three original `/api/ingestion/documents/{id}` records through real HTTP.
Only GET root/health/document-list/document-by-ID/stats/filters/automation-config
and POST ingestion/refresh are permitted. Other routes return explicit503.
No admin secret is configured; use authenticated Azure control-plane exec and
retain internal API ingress.

Batch exec work, avoid parallel execs on the same app, and honor any429
Retry-After600. Use baked scripts/simple arguments rather than nested Python
`-c` quoting.

Last observed serving SQL connection:2026-09-12T05:18:57.464402Z.
The min0 replacement revision could initialize before shutdown; the final
all-zero snapshot bounds subsequent own-process activity. SQL ARM status at
05:24:37Z remained Online, auto-pause60 configured. Avoid extra data probes that
reset idle time. See `serving-sql-final-state.json` and `serving-results.json`.

## Preserve completed data and budget

`summary-results.json` and `data-workflow-results.json` are already exported.
Their wrappers reject another live run. The data evaluator also refuses a
nonempty SQL documents table, preventing replay on a fresh replica after models
were consumed. Do not clear data, delete results or invoke baked `run` directly.
Replica-local `/tmp` reports are not durable after pause; use the exported files.

Use `python .\scripts\ckm_finalize_data.py` for evidence reconciliation.
The summary-only finalizer refuses when later data results exist; do not run
the older offline finalizer, which predates live traffic.

Do not blindly rerun `Deploy-ConversationHosting.ps1`: its historical base-image
template clears endpoints and would replace the current evaluator image.
The data Bicep now defaults to the final lab-user SQL administrator, not the
temporary bootstrap MI. SQL bootstrap/repair is an explicit separate maintenance
operation, not a normal restart. No password, tenant Graph grant or app
registration is needed.

For service-principal SQL `CREATE USER ... WITH SID ... TYPE=E`, use **client ID**.
Azure RBAC assignments instead use the MI's **principal/object ID**.
The initial wrong-SID user remains without its data-role memberships; no users
or records were deleted. Evidence documents the failure and verified correction.

## Cost and remaining feature limits

Approved fixed-active review ceiling:$1.50/hour. Configured max2 SQL + Basic
Search + four PEs +32GB data allowance + both app replicas is about$1.479765/hour,
excluding separately metered consumption/shared allocation. Model token reference
for all9 requests:$0.05975725; not an invoice or PTU charge.

Pausing ACA does not pause Search/PE/storage charges. After SQL actually pauses,
Search/four PEs/32GB allowance remain about$0.146545/hour before other charges.
At SQL minimum0.5 billed vCore, that reference is about$0.459600/hour.
Do not repeatedly data-probe SQL merely to see whether it paused; use an ARM
database status read, which does not require opening a SQL connection.

Hosted private Search still needs the documented Standard Agent private
architecture and regional alignment; the listed dependencies are already
approved/deployed, not awaiting another budget decision. The native dashboard
and file-insight semantic defects are separate from that external compatibility
blocker. No full Explore, CU/audio, hybrid-vector search, production-auth or
public-browser acceptance is claimed.
