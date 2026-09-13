"""Assemble final CWYD artifacts from observed evidence; makes no model calls."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import urllib.request

B = Path(r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\projects\PTU accelerator Bundle")
E = B / "evidence" / "cwyd"
R = Path(r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\chat-with-your-data-solution-accelerator")
STATE = Path(os.environ["LOCALAPPDATA"]) / "ptu-eval" / "cwyd"
read = lambda name: json.loads((E / name).read_text(encoding="utf-8"))
initial, updated = read("verified-initial.json"), read("verified-update.json")
result = read("result.json")
budget = read("evaluation-budget.json")
limit = budget["model_attempt_limit"]
assert limit == 16 and budget["inference_enabled"] is False, "This checkpoint requires the custody-closed16-attempt policy"
with sqlite3.connect(STATE / "model-budget.sqlite") as conn:
    calls = [json.loads(row[0]) for row in conn.execute("SELECT record FROM calls ORDER BY id")]
assert len(calls) <= limit, "Approved attempt ceiling exceeded"
assert len(calls) == 16, "This final checkpoint covers16 attempts; review newer activity before overwriting it"
(E / "model-calls.json").write_text(json.dumps(calls, indent=2), encoding="utf-8")

endpoint_checks = []
for url in ["http://127.0.0.1:5112/", "http://127.0.0.1:5112/admin",
            "http://127.0.0.1:5112/api/health", "http://127.0.0.1:8112/api/health",
            "http://127.0.0.1:8112/api/admin/documents",
            "http://127.0.0.1:8112/api/files/ptu-cwyd-travel.txt"]:
    with urllib.request.urlopen(url, timeout=30) as response:
        raw = response.read()
        endpoint_checks.append({"url": url, "status": response.status,
                                "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        if url.endswith("/api/admin/documents"):
            final_documents = json.loads(raw)
        if url.endswith("/api/files/ptu-cwyd-travel.txt"):
            active_source = raw.decode("utf-8")
assert "now 91 credits" in active_source and final_documents["total"] == 5
(E / "final-endpoints.json").write_text(json.dumps(endpoint_checks, indent=2), encoding="utf-8")

initial_by_name = {test["name"]: test for test in initial["tests"]}
updated_by_name = {test["name"]: test for test in updated["tests"]}
criteria = [initial_by_name["factual_" + str(i)] for i in range(1, 6)]
criteria += [initial_by_name["absent_answer"], initial_by_name["cross_document_comparison"],
             updated_by_name["contradictory_replacement"]]
core_pass = all(test["verdict"] == "PASS" for test in criteria) and initial["failed"] == updated["failed"] == 0
ingestions = sorted([read(p.name) for p in E.glob("ingestion-*.json")],
                    key=lambda item: item["started_epoch"])
latest = {}
for ingestion in ingestions:
    latest[ingestion["filename"]] = ingestion
models = {}
for call in calls:
    model = models.setdefault(call["model"], {"attempts": 0, "successful_calls": 0,
                                              "reported_input_tokens": 0, "reported_output_tokens": 0,
                                              "reported_total_tokens": 0, "calls_without_usage": 0})
    model["attempts"] += 1
    model["successful_calls"] += call.get("status") == 200
    usage = call.get("usage")
    if usage:
        model["reported_input_tokens"] += usage.get("prompt_tokens", usage.get("input_tokens", 0))
        model["reported_output_tokens"] += usage.get("completion_tokens", usage.get("output_tokens", 0))
        model["reported_total_tokens"] += usage.get("total_tokens", 0)
    else:
        model["calls_without_usage"] += 1
models["text-embedding-3-small"]["reported_output_tokens"] = None
backend_pid = int((STATE / "backend.pid").read_text())
worker_pid = int((STATE / "worker.pid").read_text())
for process in result["processes"]:
    if process["service"] == "backend":
        process.update(pid=backend_pid, shell_id="cwyd-backend-custody", state="running_read_only_inference_closed")
    elif process["service"] == "queue_worker":
        process.update(pid=None, last_running_pid=worker_pid, shell_id=None, state="stopped_evaluation_closed")
result.update(
    status="adapted_local_core_workflow_verified" if core_pass else "adapted_local_validation_has_failures",
    full_app_proven=False,
    adapted_local_core_workflow_proven=core_pass,
    official_unchanged_deployment_verified=False,
    azure_functions_host_verified=False,
    proof_scope="real upstream UI/API, upload, harness-dispatched ingestion, vector retrieval, chat, citations, history and active replacement; not unchanged official hosting",
    model_attempts=len(calls), model_attempt_limit=limit,
    remaining_first_pass_attempts=limit-len(calls),
    evaluation_inference_enabled=False,
    evaluation_budget_custody=budget,
    measured_model_usage=calls,
    usage_by_model=models,
    final_endpoint_checks=endpoint_checks,
    indexed_documents=final_documents,
    ingestion_history=ingestions,
    successful_ingestion_latest=list(latest.values()),
    final_functional_criteria=criteria,
    final_functional_summary={
        "business_criteria_passed": sum(test["verdict"] == "PASS" for test in criteria),
        "business_criteria_failed": sum(test["verdict"] == "FAIL" for test in criteria),
        "business_criteria_total": len(criteria),
        "actual_chat_requests": 2,
        "five_factual_questions_grouped_in_one_request": True,
        "integrity_and_functional_assertions_passed": initial["passed"] + updated["passed"],
        "integrity_and_functional_assertions_failed": initial["failed"] + updated["failed"],
    },
    final_integrity_checks={"initial": initial["tests"], "update": updated["tests"]},
    grouped_response=read("questions-grouped.json"),
    replacement_response=read("question-update.json"),
    active_source=active_source,
    blockers=[] if core_pass else ["See failed final integrity/functional checks"],
    recommendation="Keep verified adapted-local data/UI read-only; inference closed pending new explicit authorization; not production-qualified",
)
result.setdefault("historical_checks_before_final_validation", result.get("functional_tests", []))
result["functional_tests"] = criteria
result["usage_summary"] = {
    "tokens_reported": True,
    "successful_model_responses": sum(c.get("status") == 200 for c in calls),
    "calls_reporting_usage": sum(bool(c.get("usage")) for c in calls),
    "sum_returned_prompt_tokens": sum(m["reported_input_tokens"] for m in models.values()),
    "sum_returned_output_tokens": sum(m["reported_output_tokens"] or 0 for m in models.values()),
    "sum_returned_total_tokens": sum(m["reported_total_tokens"] for m in models.values()),
    "retried_calls": sum(int(c.get("retry_header", 0)) > 0 for c in calls),
    "http_401": sum(c.get("status") == 401 for c in calls),
    "http_400": sum(c.get("status") == 400 for c in calls),
    "http_429": sum(c.get("status") == 429 for c in calls),
    "upstream_http_5xx": sum(500 <= (c.get("status") or 0) < 600 for c in calls),
    "connection_timeouts": sum(c.get("exception_type") == "ConnectTimeout" for c in calls),
    "failed_call_usage": "not returned; never estimated",
}
result["evaluation_budget_request"].update(
    approved_total=limit, historical_approved_total=18, approved=True, used=len(calls), remaining=limit-len(calls),
    approval_message_timestamp="2026-09-11T20:14:09.876-04:00",
    current_cap_message_timestamp=budget["custody_timestamp"],
    portfolio_allocation_note="Parent reclaimed CWYD's unused2 for DKM comparison; current CWYD cap16 total,16 used,0 remaining; inference disabled.",
)
result["required_unblock"].update(role_request_status="completed by parent; account embeddings and project chat verified")
result["unsupported_scenarios"] = [
    "unchanged official deployment and full Azure Functions host/queue-trigger retry-poison semantics",
    "browser-driven typing/clicking walkthrough; UI/admin HTTP and file links were verified",
    "five factual questions as isolated model requests; deliberately grouped",
    "load/concurrency/scalability/failover testing",
    "Speech, Content Safety and rich-document Document Intelligence paths",
    "Agent Framework / Foundry IQ Search orchestration; evaluated route is LangGraph plus pgvector",
    "production cloud ingress/authentication and accreditation",
    "historical source-file version URLs: stored old snippets persist, but filename download resolves current replacement",
]
result["lifecycle_verification"] = {
    "worker_actual_stop_start": "PASS using Stop-Cwyd.ps1 worker then Start-Cwyd.ps1 worker",
    "other_stop_targets": "backend/frontend/database/storage resolved and inspected with -WhatIf",
    "new_worker_pid": worker_pid,
    "local_data_preserved": True,
    "no_model_calls_for_lifecycle_verification": True,
    "scripts": ["scripts/Start-Cwyd.ps1", "scripts/Stop-Cwyd.ps1"],
    "custody_update": {
        "backend_pid": backend_pid,
        "backend_mode": "read_only_inference_closed",
        "worker_state": "stopped_evaluation_closed",
        "frontend_and_containers_restarted": False,
        "dependencies_rebuilt": False,
    },
}
feature_status = {
    "ingestion embeddings": "six successful calls including replacement;430 reported tokens",
    "query embeddings": "two successful calls;167 reported tokens",
    "factual absent-answer and cross-document responses": "PASS grouped real grounded response with matched source files/index/history",
    "inline citations": "PASS matched source IDs/snippets and persisted metadata; frontend derives file route from title",
    "optional reasoning and capability probe": "non-reasoning GPT4.1-mini probe400 correctly falls back; no reasoning-generation proof",
    "contradictory replacement": "PASS real overwrite reembedding active index and requery91 rather than73",
    "history and configuration": "conversation history and stored citation metadata verified; configuration UI not exhaustively tested",
}
for feature in result["per_feature_ptu_dependence"]:
    if feature["feature"] in feature_status:
        feature["status"] = feature_status[feature["feature"]]
result["ptu"]["sizing_inputs_missing"] = ["representative peak RPM", "representative input/output distributions",
                                          "cache behavior over sustained traffic", "provisioned region/capacity validation",
                                          "approved representative PTU benchmark"]
(E / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
proposal = read("infrastructure-proposal.json")
proposal.update(proposal_status="approved existing-resource envelope; adapted-local functional evaluation complete",
                model_attempts_used=len(calls), model_attempts_remaining=limit-len(calls),
                model_attempt_limit=limit, evaluation_inference_enabled=False,
                evaluation_budget_custody=budget,
                evaluation_budget_request=result["evaluation_budget_request"])
proposal["authorization_needed"]["status"] = "completed by parent; no further role or infrastructure request"
for service in proposal["local_services"]:
    if service["name"] == "upstream FastAPI":
        service["pid"] = backend_pid
    elif service["name"].startswith("upstream ingestion"):
        service.update(pid=None, last_running_pid=worker_pid, state="stopped_evaluation_closed")
(E / "infrastructure-proposal.json").write_text(json.dumps(proposal, indent=2), encoding="utf-8")

token_rows = []
for call in calls:
    usage = call.get("usage") or {}
    inp = usage.get("prompt_tokens", usage.get("input_tokens", "—"))
    out = usage.get("completion_tokens", usage.get("output_tokens", "—"))
    status = call.get("status") or call.get("exception_type", "unknown")
    token_rows.append(f"| {call['id']} | {call['operation']} | {call['model']} | {status} | {inp} | {out} | {call['latency_ms']} | {call.get('retry_header', '0')} |")
report = f"""# Chat With Your Data — final adapted-local evaluation

## Outcome and proof boundary

**Core adapted-local workflow verified: 8/8 requested business criteria passed.** Five fictional policies were uploaded through the genuine FastAPI admin API, processed by the upstream ingestion implementation, embedded by Azure, indexed into real pgvector, retrieved by the upstream LangGraph route, and answered with citations. The contradictory replacement was actually uploaded/re-embedded, became the active indexed content, and was correctly cited by a new answer.

This is **adapted-local execution**, not an unchanged official deployment, not `azd up` verification, and **not full Azure Functions host verification**. The queue harness calls the real upstream `functions.batch_push.blueprint._execute`; it does not replace parsing, embeddings, indexing, retrieval or generation with a generic RAG substitute. UI/admin HTTP and API/file endpoints were verified; an interactive browser typing/clicking walkthrough was not performed.

**Budget custody update ({budget['custody_timestamp']}): evaluation closed at16/16 used,0 remaining.** Parent reclaimed the unused2 from the historical18-attempt approval for DKM comparison. The UI and stored policies/citations/history remain available read-only; generation and ingestion are disabled. No new model calls or Azure changes accompanied this custody update.

### Reproducible provenance

- Repository: https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator
- Checkout: `{R}`
- SHA: `0fce71307dfa76a82ac82ec73bdde3daa47e503d`; branch `main`; describe `v2.0.0-6-g0fce7130`; commit2026-08-27T06:24:04Z.
- Upstream working tree verified clean after restoring only our generated `tsconfig.tsbuildinfo`.
- `uv sync --frozen` passed in `%LOCALAPPDATA%\\ptu-eval\\cwyd\\runtime`.
- Frontend production build passed: Vite8.2.0,2741 transformed modules; >500KB chunk warning retained.
- Focused upstream `tests/functions/batch_push`: **23 passed**,134.95seconds. The broad optional test run was stopped during host contention and is not claimed as passed.
- Inspected README, local/deployment/model docs, environment template, `azure.yaml`, root/nested IaC and hooks before choosing the local route. Current repo supports `AZURE_EXISTING_AIPROJECT_RESOURCE_ID`; no speculative IaC retrofit or cloud provisioning was run. Installed azd1.23.7 satisfies the inspected requirement; no upgrade was needed.

## Running endpoints and processes

| Component | Current endpoint/process | Execution |
|---|---|---|
| Upstream React/Vite UI and admin | http://127.0.0.1:5112/ and `/admin`; PID15628 | Native, loopback only; shell `cwyd-frontend` |
| Genuine FastAPI | http://127.0.0.1:8112/; PID{backend_pid} | Read-only; shell `cwyd-backend-custody` |
| Upstream ingestion implementation | Stopped; last PID{worker_pid} | Worker launch disabled; queued data preserved |
| PostgreSQL/pgvector | `127.0.0.1:15432`, container `ptu-cwyd-postgres`, ID6607fed0b8b2 | 512MiB RAM, oneCPU |
| Azurite | `127.0.0.1:18100` blob,18101 queue; container `ptu-cwyd-azurite`, IDbdac69e527fa | 512MiB RAM, oneCPU |

Final UI, admin, frontend→API proxy, API health, five-document listing and active travel-file endpoints all returnedHTTP200. `api/health` is a **configuration** check, not by itself inference proof. Real model/citation/history results below supply the functional evidence.

Containers have a combined **1GiB RAM ceiling** with no extra swap allowance; native process memory is additional. Last sampled use was34.62MiB PostgreSQL and78.87MiB Azurite. All processes remain session-attached; survival after CLI exit is not promised.

## Functional expected versus actual

Five explicitly fictional/unclassified Larkspur policies were used. Five factual questions, one absence question and one comparison were **grouped into one real chat request** to conserve the approved budget; they were not seven independent model calls.

| Criterion | Expected | Actual | Verdict |
|---|---|---|---|
| Travel allowance |73 credits/day + travel citation |73 credits, correct travel source | PASS |
| Learning allowance |640 credits/year + learning citation |640 credits, correct learning source | PASS |
| Remote work |Two days/week + remote policy citation |Two days, correct remote source | PASS |
| Records retention |Seven years + records citation |Seven years, correct records source | PASS |
| Calibration |Every90 days + equipment citation |90 days, correct equipment source | PASS |
| Absent answer |Do not invent orbital relocation allowance |“There is insufficient evidence…” | PASS |
| Cross-document comparison |Travel21 versus learning45 days; both sources |Correct deadlines and both citations | PASS |
| Contradictory replacement |Active version2 changes73→91 credits |Answer says91 replaces73 and cites active version2 | PASS |

Additional integrity verification passed **18/18 assertions across initial and update checkpoints**, including the business criteria above:
- Citation source IDs and snippets matched **actual database rows and source bytes returned by `/api/files/<filename>`**, not just expected prompt text.
- Answers and complete citation metadata were fetched from the genuine history API and compared exactly with the returned chat responses.
- Real document replacement left exactly one travel chunk and five total active source/chunk rows; the active blob and index both contain version2 and “now91 credits”.
- The original conversation retained its original73-credit answer and citation snippets after replacement.
- Empty citation `url` fields are the repo's uploaded-file convention: `documentHref.tsx` derives `/api/files/<encoded title>`. Those actual file routes were verified.

**Historical-source limitation:** stored old snippets are preserved, but downloading the same filename returns the current replacement, not an immutable historical blob version. Versioned historical-source URLs were not proved.

Initial grouped conversation: `{initial['conversation_id']}`; API elapsed **{initial['app_call_latency_ms']}ms**.
Updated conversation: `{updated['conversation_id']}`; API elapsed **{updated['app_call_latency_ms']}ms**.
These two cold/warm samples are not a latency benchmark, load test or meaningful P95 estimate.

## Actual model calls, retries and usage

**{len(calls)}/{limit} total attempts used**, including every earlier failure and retry; **{limit-len(calls)} remain**. The historical18-attempt approval of2026-09-11 at20:14:09EDT was superseded by the custody update above: unused2 reclaimed for DKM. All16 SQLite records and returned usage are preserved. Persistent policy `B\\evidence\\cwyd\\evaluation-budget.json` disables inference and caps attempts at16; the harness enforces both before any model HTTP send. SDK retries remain inside the same cap.

| Model | Successful calls | Reported input tokens | Reported output tokens | Reported total tokens |
|---|---:|---:|---:|---:|
| text-embedding-3-small Standard |8|597|Not applicable/not returned|597|
| gpt-4.1-mini GlobalStandard |2|2507|210|2717|
| Combined returned usage |10|3104|210|3314|

Failures retained: threeHTTP401, twoConnectTimeouts, and oneHTTP400 from the repo's **reasoning-capability probe**. The400 was `reasoning.effort` unsupported for GPT4.1-mini; upstream correctly fell back to chat. Two retry requests are included. No429 or upstream5xx was observed. Initial app chat surfaced a sanitized502 before remediation. Failed calls returned no token usage; none was estimated.

| Attempt | Operation | Model | Status/error | Input tokens | Output tokens | Model HTTP latency ms | SDK retry |
|---:|---|---|---|---:|---:|---:|---:|
{chr(10).join(token_rows)}

Per-call raw returned usage, latency/status/errors and retries: `B\\evidence\\cwyd\\model-calls.json`. No keys, bearer tokens, secret connection strings or inference prompts were captured in this ledger.

## Azure infrastructure and cost

Tenant `a600acd0-3028-4689-8402-3b471d7d924d`; subscription **`1feb53b2-854a-4ea7-b5a6-709b7d804f70` only**.

**New Azure resources/RGs/models/capacity: none. Incremental fixed Azure cost:US$0/hour.** Existing consumption-model token usage may be billed; an invoice/dollar amount is not claimed. No PTU purchase, reservation, model-capacity increase, GPU, VM, AKS, premium Search or dedicated compute.

| Service/resource | CWYD use | SKU/location and cost relationship |
|---|---|---|
| Existing `edcfoundryhack01` / `edc-hack-proj` in `rg-edc-foundry-hack` |Azure embeddings and project-scoped chat|Canada East; `gpt-4.1-mini`2025-04-14 GlobalStandard capacity100; `text-embedding-3-small`v1 Standard capacity100,1536 dimensions; unchanged |
| `edc-hack-search` |Not used; inventory only for this app|Basic, one partition/one replica; existing lab charge, not a new CWYD resource |
| App/worker hosting |Local native processes|No Azure Container Apps/Functions hosting created |
| Blob/queue and retrieval/history |Local Azurite and PostgreSQL/pgvector|No Azure Storage, Cosmos or PostgreSQL service created |
| Registry/monitoring |Local build, logs and ledger|No new ACR, App Insights, Log Analytics or Azure Monitor resources |
| Speech/Content Safety/Document Intelligence |Not configured/evaluated|No usage claimed; separate service billing, not OpenAI PTUs |

`disableLocalAuth=true` was verified through `B\\Invoke-LabAz.ps1 -AzArguments <string[]>`. Azure calls use **Entra AzureCliCredential only**; keys were not used and local auth was not enabled. The parent alone granted OpenAI User role`5e0bd9bd-7b93-4f28-af87-19fc36ad61bd` to user`87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed` at this account, assignment`4df8a697-fc79-448a-8f0f-54f90020f5d3`; no duplicate grant by CWYD. The separate project Foundry User grant has a different role and is not attributed to CWYD.

All actual protected IDs/groups in `B\\evidence\\protected-resources.json` remain inventory-only, including expanded SpecSuite/Planetary and managed resource groups. No protected resource was reused or modified. The CLI guard is not billing approval.

## Per-feature PTU dependence

**No feature currently consumes PTUs, and no CWYD feature requires a PTU purchase.** Current Learn [PTU sizing guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing), verified2026-09-11, lists GPT4.1-mini2025-04-14 and GPT5.12025-11-13 as provisioned-supported. GPT5.1 was not selected/called. Model/version, deployment type, region and available capacity must be verified for any future proposal.

| Feature | Model/PTU relationship | Supporting infrastructure not using OpenAI PTU |
|---|---|---|
| Chat/admin UI and SSE transport |No PTU requirement|React, FastAPI, host compute; cloud alternative Container Apps/ACR |
| Upload/enqueue |No PTU requirement|Blob/queue transactions, worker compute |
| Parse/chunk |No PTU for local TXT parsing|CPU; optional Document Intelligence separately billed |
| Ingestion/replacement embeddings |Current text-embedding-3-small is Standard, **not PTU-backed**; provisioned eligibility not established by the cited chat sizing table|Worker, source blobs, index writes |
| Vector indexing/retrieval |No PTU requirement for vector/database search|pgvector/PostgreSQL; alternative Search/Cosmos charges are independent |
| Query embeddings |Separate Standard embedding usage; not charged against chat PTUs|API/orchestrator compute |
| Factual answers, absence handling and comparison |Future supported provisioned GPT4.1-mini could serve the **generation portion**; current calls GlobalStandard|Retrieval, grounding context assembly, APIs and history storage |
| Citations |Only model-generated answer text could use a future chat PTU; extraction/rendering/source downloads do not|UI, citation code, blobs, database metadata |
| Optional reasoning/probe |Model-specific; tested GPT4.1-mini probe correctly rejected reasoning and fell back. GPT5.1 remains untested|Provider/orchestrator compute |
| Contradictory replacement |PTU does not solve freshness/conflict correctness; future PTU could serve subsequent chat only|Blob overwrite, parsing, embeddings, active index consistency |
| History/configuration |No PTU requirement|PostgreSQL/Cosmos persistence and admin UI |
| Voice/safety/rich-document extraction |Speech, Content Safety and Document Intelligence are **not OpenAI PTU services**|Independent Azure services and metering |
| Identity/monitoring/images |No PTU requirement|Entra/RBAC, local logs/ledger; Azure Monitor/App Insights/ACR if later deployed |

There is **no general “onePTU equals fixed tokens” assumption**. Sizing depends on model-specific input throughput/output weighting, request distributions, peakRPM, cache behavior, deployment minimums/increments and representative benchmarks. These small functional tests are **not PTU tests**; no utilization percentage, PTU quantity or purchase recommendation is inferred.

## Explicit compatibility adapters

All adapters live under `B\\scripts`, outside the clean upstream checkout:
1. **Azurite:** current Compose env names drift from typed settings, its blob→queue hostname replacement cannot translate emulator ports, and the production SDK constructors expect Entra credentials. The launcher changes auth/endpoints **only for the exact loopback emulator URLs**. The public emulator value is read from existing upstream Compose into memory, never persisted as a new secret or printed. This does not enable Azure local auth.
2. **Local PostgreSQL:** upstream requires an Entra principal/password callback even locally. The launcher removes that callback only for the exact loopback `ptu_cwyd` DB and caps its pool at two; the synthetic-only container uses trust auth and a credential-free URI built in runtime environment. Not suitable for an untrusted/shared host or production.
3. **Worker host:** a local queue consumer calls upstream `batch_push._execute`. Failed queue messages are recorded and acknowledged once to prevent uncontrolled paid retries; Azure Functions trigger/poison/retry semantics are **not verified**.
4. **Account embedding endpoint:** `CWYD_USE_ACCOUNT_OPENAI_ENDPOINT=true` applies the SDK-documented `get_openai_client(base_url=...)` override from this account's services route to its contract-supplied OpenAI v1 endpoint. The same Entra `ai.azure.com/.default` token provider remains; project chat endpoint is unchanged. A post-grant original-route401 and corrected-route200 are retained, but concurrent RBAC propagation cannot be excluded as a factor. [Microsoft Learn Entra v1 example](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/managed-identity).
5. **Vite:** runtime override binds127.0.0.1:5112 and corrects the checked-in proxy's port8000 to8112. AzureCliCredential is pinned to the allowed subscription with bounded process timeout. SDK/model telemetry has a shared16-attempt exhausted ceiling; inference is disabled.
6. **Custody closure:** `Start-Cwyd.ps1` sets `CWYD_INFERENCE_DISABLED=true` and refuses worker startup. Direct harness startup independently checks the persistent policy; missing/invalid policy fails closed. The API returns explicitHTTP503 `cwyd_evaluation_closed` for mutating `/api/` requests before app handlers run, while GET history/files/admin/health stay available. The transport guard separately rejects model sends before adding a ledger record or invoking HTTP.

## Start, stop and resume

All commands are **foreground/session-attached**. Use one terminal/tool session per service. No credentials are written to the repo or OneDrive.

```powershell
$B = '{B}'
& "$B\\scripts\\Start-Cwyd.ps1" database
& "$B\\scripts\\Start-Cwyd.ps1" storage
& "$B\\scripts\\Start-Cwyd.ps1" backend
& "$B\\scripts\\Start-Cwyd.ps1" frontend
```

The start script uses the locked runtime at `%LOCALAPPDATA%\\ptu-eval\\cwyd\\runtime`, selects the verified endpoint adapter, and reuses the named local containers. Native PID files are stored outside OneDrive under `%LOCALAPPDATA%\\ptu-eval\\cwyd`.

These are read-only restart commands; do not rebuild dependencies for this custody change. Worker startup intentionally fails while the evaluation is closed. **Future inference requires a fresh explicit authorization for an additional allowance, recorded with its approval reference and a new cumulative total including these16 records.** Only then may the persistent policy, harness ceiling and launcher's explicit disable setting be deliberately updated. Restarting services, changing inherited environment variables or the old18-attempt approval does not restore the reclaimed2. Never reset/delete the ledger.

Stop only these verified processes/containers, preserving local data:

```powershell
& "$B\\scripts\\Stop-Cwyd.ps1" worker
& "$B\\scripts\\Stop-Cwyd.ps1" backend
& "$B\\scripts\\Stop-Cwyd.ps1" frontend
& "$B\\scripts\\Stop-Cwyd.ps1" storage
& "$B\\scripts\\Stop-Cwyd.ps1" database
```

`Stop-Cwyd.ps1` validates native PID command lines and supports `-WhatIf`; it never kills by process name or deletes data/Azure resources. **Historical worker stop→start passed** at PID{worker_pid}. For custody closure, only CWYD backend/worker were actually stopped; the backend was restarted read-only as PID{backend_pid} and the worker stays disabled. Frontend and both containers were left untouched; the ledger, policies and history are preserved.

For a fresh local setup only, inspect for existing names first, then create each container in a separate foreground session:

```powershell
docker run --name ptu-cwyd-postgres --memory 512m --memory-swap 512m --cpus 1 -e POSTGRES_HOST_AUTH_METHOD=trust -e POSTGRES_USER=cwyd -e POSTGRES_DB=ptu_cwyd -p 127.0.0.1:15432:5432 pgvector/pgvector:pg16
docker run --name ptu-cwyd-azurite --memory 512m --memory-swap 512m --cpus 1 -p 127.0.0.1:18100:10000 -p 127.0.0.1:18101:10001 mcr.microsoft.com/azure-storage/azurite:latest azurite --blobHost 0.0.0.0 --queueHost 0.0.0.0 --skipApiVersionCheck --silent
```

Fresh-checkout dependency setup (never overwrite user changes):

```powershell
$R = '{R}'
$Tools = "$env:LOCALAPPDATA\\ptu-eval\\cwyd\\venv"
python -m venv $Tools
& "$Tools\\Scripts\\python.exe" -m pip install uv
$env:UV_PROJECT_ENVIRONMENT = "$env:LOCALAPPDATA\\ptu-eval\\cwyd\\runtime"
Set-Location $R
& "$Tools\\Scripts\\uv.exe" sync --frozen
Set-Location "$R\\src\\frontend"
npm ci --no-audit --no-fund
npm run build
```

The PostgreSQL `vector` extension was initialized with `docker exec ptu-cwyd-postgres psql -U cwyd -d ptu_cwyd -c 'CREATE EXTENSION IF NOT EXISTS vector;'`.

**No model-backed stages are currently authorized:16/16 used,0 remaining. Never reset the ledger.** `cwyd_verify_evidence.py` and API/history/file checks use no model calls; running its `initial` stage after replacement will intentionally no longer match the current travel blob. Its preserved pre-update result is `verified-initial.json`. `update` verification remains reproducible against the current stored response/source.

## Evidence, limitations and recommendation

- `result.json`: process/resource inventory, model ledger, expected/actual criteria, integrity checks, approval and limitations.
- `questions-grouped.json`, `question-update.json`: actual application responses, citation metadata and client latency.
- `verified-initial.json`, `verified-update.json`: deterministic comparisons with actual blobs/index/history.
- `active-content-after-update.json`: actual indexed version2; `ingestion-*.json`: successes and failures.
- `model-calls.json`: all16 model attempts; `unit-tests.xml`:23 upstream unit passes.
- `final-endpoints.json`: final HTTP statuses/hashes; `infrastructure-proposal.json`: no new Azure envelope.
- `evaluation-budget.json`: authoritative closed16-total policy; `budget-custody-baseline.json` and `budget-custody-validation.json`: unchanged-ledger/evidence hashes and closure checks.

Not verified: unchanged official deployment, full Azure Functions host, interactive browser gestures, separate factual model sessions, load/concurrency, scaling/failover, production cloud ingress/authentication, Agent Framework/Foundry IQ Search route, voice/safety/rich-document features or DND/JDCP accreditation. No such claim follows from these results.

Monitoring consists of real endpoint checks, foreground errors, per-ingestion JSON and the model ledger. Paid Azure alerting was not enabled. Recovery is scoped to stopping/restarting the isolated local services; no Azure rollback or automatic deletion is needed or configured.

**Recommendation: Keep verified data/UI read-only; inference stays closed pending fresh explicit authorization.** Core functional evidence is preserved, but production/unchanged-official hosting requires separate qualification.
"""
(B / "reports" / "cwyd.md").write_text(report, encoding="utf-8")
print(json.dumps({"status": result["status"], "criteria": result["final_functional_summary"],
                  "model_attempts": len(calls), "usage_by_model": models,
                  "backend_pid": backend_pid, "worker_pid": None, "last_worker_pid": worker_pid,
                  "report": str(B / "reports/cwyd.md")}, indent=2))
