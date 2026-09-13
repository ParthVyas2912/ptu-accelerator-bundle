"""Finalize DKM evidence from actual saved results; never initiate cloud/model operations."""
import difflib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

b = Path(__file__).resolve().parents[1]
e = b / "evidence/documents"
repo = Path.home() / "OneDrive - Microsoft/Desktop/repo/Document-Knowledge-Mining-Solution-Accelerator"
def load(name):
    return json.loads((e / name).read_text(encoding="utf-8-sig"))
def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

metrics = load("final-metrics-summary.json")
post_pause = load("post-pause-metrics-summary.json")
budget = load("model-budget.json")
if budget["cap_including_retries"] > 12:
    raise SystemExit("Twelve-call finalizer is historical; use documents-finalize14.py for the approved comparison supplement.")
state = load("final-runtime-state.json")
restart = load("restart-verified-health.json")
source_restart = load("restart-verified-sources.json")
assert metrics["requests"] == 12 and budget["remaining_attempts"] == 0
assert post_pause["requests"] == 12 and post_pause["total_tokens"] == metrics["total_tokens"] and post_pause["alias_check"]
assert budget["pending_operation"] is None
assert all(not rev["active"] and rev["replicas"] == 0 for app in state["apps"] for rev in app["revisions"])
assert restart["result"]["kernel"]["status"] == restart["result"]["backend"]["status"] == 200
assert json.loads(restart["result"]["backend"]["body"])["totalRecords"] == 2
assert all(x["status"] == 200 for x in source_restart["result"])
assert {(x["name"], x["sha256"], x["bytes"]) for x in source_restart["result"]} == {
    (x["name"], x["sha256"], x["bytes"]) for x in load("retry-phase-sources.json")["result"]}
subprocess.run(["python", str(b / "scripts/documents-functional-checks.py")], check=True)
checks = load("functional-checks.json")
second = json.loads(load("retry-phase-ingest-second.json")["result"]["body"])
fixture = load("second-policy-fixture.json")
doc_qa = load("retry-phase-qa-document.json")
doc_answer = json.loads(doc_qa["result"]["body"])
c = load("cloud-functional-result.json")
c.setdefault("historical_first_phase_tests", c["tests"])
c.setdefault("historical_first_phase_telemetry", c["model_telemetry"])
c.setdefault("historical_first_phase_restart", c["restart_verification"])
for s in c["hosting"]["services"]:
    if s["name"] == "ca-dkm-api":
        s.update(image="acrptubundle7d804f70.azurecr.io/dkm/backend:7df8ed3-evalretry-r1",
                 manifest_digest="sha256:2c462b7af6ce04e33c3b2122e498ad5e0a73d7273133d0d175f82b141f4c9c79")
    elif s["name"] == "ca-dkm-kernel":
        s.update(image="acrptubundle7d804f70.azurecr.io/dkm/kernelmemory:7df8ed3-evalretry-r1",
                 manifest_digest="sha256:48b17a3319ede52dd0a409beabfdbb500aee22e6f9c5edfe2c1a175f8720dacc")
    s["runtime_state"] = "PAUSED_ZERO_REPLICAS"
c["hosting"]["image_packaging"] = "Original Dockerfiles unchanged; clean app-only source contexts. Approved opt-in SDK retry controls in three construction paths; no business/prompt/output changes."
c["ingestions"] = [c["ingestion"], {
    "file": second["fileName"], "document_id": second["documentId"],
    "imported_time_utc": second["importedTime"], "sha256": fixture["sha256"], "bytes": fixture["bytes"],
    "http_status": 200, "client_elapsed_ms": load("retry-phase-ingest-second.json")["ms"],
    "server_processing_seconds": 25.6951030, "summary": second["summary"],
    "logical_case": 2, "original_txt_rendition_uploaded": False
}]
latencies = {}
weights = {}
for m in load("final-metrics-totals.json")["value"]:
    if m["name"]["value"] != "ModelRequests":
        continue
    for s in m["timeseries"]:
        deployment = s["metadatavalues"][0]["value"]
        for p in s["data"]:
            if p.get("total") is not None:
                weights[deployment, p["timeStamp"]] = p["total"]
for m in load("final-metrics-latency.json")["value"]:
    for s in m["timeseries"]:
        operation = s["metadatavalues"][0]["value"]
        deployment = "text-embedding-3-large" if "embedding" in operation.lower() else "gpt-5-mini"
        pairs = [(p["average"], weights.get((deployment, p["timeStamp"]), 0))
                 for p in s["data"] if p.get("average") is not None]
        count = sum(n for _, n in pairs)
        if count:
            latencies[operation] = sum(value * n for value, n in pairs) / count
di = {}
for m in load("document-intelligence-metrics.json")["value"]:
    di[m["name"]["value"]] = sum(p.get("total") or 0 for s in m["timeseries"] for p in s["data"])
c["model_telemetry"] = {
    "source": "Dedicated-account Azure Monitor ModelRequests, cross-checked against AzureOpenAIRequests status series; aliases not summed",
    "total_observed_requests": 12, "cap": 12, "remaining_attempts": 0,
    "by_deployment": [
        {"model": k, "requests": v["ModelRequests"], "input_tokens": v.get("InputTokens", 0),
         "output_tokens": v.get("OutputTokens", 0), "total_tokens": v["TotalTokens"], "http_status": 200}
        for k, v in metrics["by_deployment"].items()
    ],
    "input_tokens": metrics["input_tokens"], "output_tokens": metrics["output_tokens"],
    "total_tokens": metrics["total_tokens"], "operation_average_latency_ms": latencies,
    "latency_caveat": "Request-count-weighted provider minute averages; not per-request traces or p95.",
    "wire_count_caveat": "Observed fan-out4+4+2+2, all account statuses200. New SDK retries0; no load test.",
    "metric_delay_caveat": "Early snapshots omitted new calls; only settled reconciled counts used.",
    "ptu_test": False, "deployment_sku": "GlobalStandard", "provisioned_capacity_created": False
}
c["document_intelligence_telemetry"] = di | {
    "scope": "Separate extraction billing:3 successful DI HTTP calls including polling,1 processed page; not OpenAI requests or PTU traffic."
}
c["tests"] = checks["checks"] + [
    {"name": "Full browser UI", "status": "BLOCKED", "expected": "Usable original UI at approved CIDR",
     "actual": "Observed403 RBAC; restriction unchanged; no browser E2E claim"},
    {"name": "Upstream frontend unit suite", "status": "FAIL", "expected": "Four cases execute",
     "actual": "Missing @testing-library/dom; zero cases executed"},
    {"name": "Full /chat orchestration and suggestions", "status": "NOT_RUN",
     "expected": "UI chat synthesis/suggestions path", "actual": "Actual /Documents/Ask tested instead; /chat not called"},
    {"name": "Ten-document, chart and handwriting coverage", "status": "NOT_RUN",
     "expected": "Ten mixed documents including chart/handwriting", "actual": "Only2/10 logical cases ingested; one TXT and one table PDF rendition"},
    {"name": "Pause/resume source persistence", "status": "PASS", "expected": "Two documents and exact files survive restart",
     "actual": "Health200, metadata count2, both downloaded hashes match; final all revisions inactive/zero replicas"}
]
c["retry_budget_finding"] = "Approved opt-in SDK controls deployed and tested. All12 attempts consumed:4 first ingestion,4 second ingestion,2 document QA,2 corpus attempt. No repeat after Unicode capture failure."
c["current_runtime_action"] = "PAUSED_VERIFIED: every retained revision inactive/zero replicas; no resources deleted."
c["restart_verification"] = {
    "procedure": "Set-DocumentsRuntime.ps1 Pause -> Resume -> actual health/source checks -> Pause",
    "resume_executed": True, "post_restart_kernel_health": "HTTP200",
    "post_restart_backend_data": "HTTP200,totalRecords2", "source_hashes_match": True,
    "persistence_verified": True, "final_state": "All revisions active=false,replicas=0",
    "evidence": ["restart-verified-health.json","restart-verified-sources.json","final-runtime-state.json"]
}
c["full_application_e2e_passed"] = False
c["scope_qa"] = {
    "document": {"status": "PASS", "endpoint": "/Documents/Ask", "elapsed_ms": doc_qa["ms"],
                 "facts": "2025;10 annual training days", "citation_document_ids": [x["documentId"] for x in doc_answer["relevantSources"]]},
    "corpus_comparison": load("retry-phase-qa-corpus-uncaptured.json")
}
c["finalized_utc"] = datetime.now(timezone.utc).isoformat()
save(e / "cloud-functional-result.json", c)
phase = {
    "status": "CORE_INGESTION_AND_DOCUMENT_QA_VERIFIED_PAUSED_PARTIAL",
    "source_sha": c["source_sha"], "finalized": True, "full_application_e2e_passed": False,
    "retry_regression": {"run": "chg", "legacy_assertions": 16, "modern_assertions": 13,
                         "live_model_calls": 0, "result": "PASS",
                         "caveat": "Stock fake-transport baseline1 with injected HttpClient; factory-identity tests prove unset/empty follows unchanged original construction. Eval0=1 attempt;eval2=3."},
    "remote_builds": {"backend": {"run": "che","status": "Succeeded","duration_seconds": 111},
                      "kernelmemory": {"run": "chh","status": "Succeeded","duration_seconds": 195}},
    "build_failures_preserved": ["chc: harness run executable-path mismatch","chd: absolute task path invalid remotely",
                                 "chf: legacy ACR dependency scanner cannot parse original FROM --platform"],
    "kernel_build_adaptation": "Native Docker Buildx within approved ACR quick command task; original Dockerfile unchanged.",
    "tests": checks["counts"], "model_metrics": metrics, "document_intelligence": di,
    "remaining_attempts": 0, "comparison_verified": False, "browser_verified": False,
    "unicode_transport_probe": load("retry-phase-encoding-probe.json"),
    "runtime_state": state, "post_pause_metrics_unchanged": post_pause,
    "cost_usd_hour": c["cost_usd_hour"]
}
save(e / "retry-evaluation-final.json", phase)
r = load("result.json")
r["status"] = phase["status"]
r["finalized"] = True
r["current_phase_evidence"] = "evidence/documents/retry-evaluation-final.json"
r["repository"]["source_deviation"] = (
    "Approved worker-SKU parameterization; narrow Docker context exclusions; explicit opt-in DKM_EVAL_MAX_MODEL_RETRIES helper in three Semantic Kernel construction paths. "
    "Unset/empty uses unchanged production factories. Original Dockerfiles, prompts, business logic and outputs unchanged. ACA hosting adapter in bundle."
)
r["runtime"].update(status=c["current_runtime_action"], cloud_services=c["hosting"]["services"],
                    running_full_app=False, core_ingestion_verified=True, full_browser_e2e_verified=False,
                    restart_verification=c["restart_verification"], document_qa_verified=True)
r["tests"] = c["tests"]
r.setdefault("historical_paths_investigated", r["paths_investigated"])
r["paths_investigated"] = [
    {"path": "Official AKS dev stack, including approved equivalent worker parameterization",
     "outcome": "AKSCapacityHeavyUsage; no AKS/worker exists; seven successfully created PaaS retained"},
    {"path": "Documented native/local original services",
     "outcome": "Native .NET builds and original image builds passed; local private-data route blocked by PNA Disabled, not bypassed"},
    {"path": "Approved original-container hosting on shared Consumption ACA",
     "outcome": "Genuine2-document ingestion, PDF table/metadata, document-scoped QA and restart/persistence verified; paused; public UI/comparison response remain unverified"}
]
r["azure"]["current_actual_inventory"] = load("current-resource-inventory.json")
r["azure"]["required_inventory_scope"] = "Original official-stack requirements retained for reference; actual shared-host adaptation and created/reused IDs are recorded separately."
r["ptu"].setdefault("historical_per_feature", r["ptu"].get("per_feature", []))
r["ptu"]["separately_billed_infrastructure"] = [
    "Document Intelligence S0", "AI Search Basic", "Consumption ACA", "Cosmos MongoDB",
    "App Configuration Standard", "shared Basic ACR/builds", "Blob/Queue Storage", "private endpoints/networking"]
r["ptu"]["stock_aks_required_but_not_created"] = True
r["ptu"]["per_feature"] = [
    {"feature": "Upload/control and source download", "chat_ptu_dependence": "Transport/control itself none; upload triggers separately classified inference stages",
     "azure_infrastructure": ["Consumption ACA backend/KM", "Blob/Queue Storage", "Cosmos MongoDB", "App Configuration"],
     "verification": "PASS:2 genuine ingestions and matching source downloads"},
    {"feature": "PDF/table extraction", "chat_ptu_dependence": "None; DI is separately metered, not OpenAI PTUs",
     "azure_infrastructure": ["Document Intelligence S0", "Blob Storage", "Consumption ACA"],
     "verification": "PASS:1page, correct15-day table value/columns;3DIHTTPcalls,0errors"},
    {"feature": "Chart/image/handwriting interpretation", "chat_ptu_dependence": "Potential multimodal chat inference in source; provisioned compatibility requires separate validation",
     "azure_infrastructure": ["Document Intelligence", "Azure OpenAI", "Blob Storage", "Consumption ACA"],
     "verification": "NOT_RUN; no claim from table-PDF test"},
    {"feature": "Summaries and entity metadata", "chat_ptu_dependence": "GPT-5-mini GlobalStandard actual; no PTUs required/deployed",
     "azure_infrastructure": ["Azure OpenAI", "Consumption ACA", "Blob/Queues", "Cosmos MongoDB", "App Configuration"],
     "verification": "Metadata PASS; both summaries FAIL grounding due unsupported greeting"},
    {"feature": "Vectorization/indexing", "chat_ptu_dependence": "Embedding-3-large separate GlobalStandard stream; Search writes are not model calls",
     "azure_infrastructure": ["Azure OpenAI embeddings", "AI Search Basic", "Storage", "Consumption ACA"],
     "verification": "PASS:two documents persisted/retrieved;6embedding requests including2queries"},
    {"feature": "Metadata filtering", "chat_ptu_dependence": "None at query execution; extraction inference occurs earlier",
     "azure_infrastructure": ["Cosmos MongoDB", "Consumption ACA backend", "App Configuration"],
     "verification": "PASS:unfiltered2,CedarBay2,Neverland0,Omar1"},
    {"feature": "Document-scoped QA/citations", "chat_ptu_dependence": "Query embedding plus GPT answer; actualGlobalStandard, no PTU test",
     "azure_infrastructure": ["Azure OpenAI", "AI Search", "Blob Storage", "Consumption ACA", "App Configuration"],
     "verification": "PASS:2025/10days, only selected document in citations, real original /Documents/Ask"},
    {"feature": "Corpus QA/two-document comparison", "chat_ptu_dependence": "Query embedding plus GPT answer, actual2account requests200; no PTUs",
     "azure_infrastructure": ["Azure OpenAI", "AI Search", "Blob Storage", "Consumption ACA", "App Configuration"],
     "verification": "ATTEMPTED_UNVERIFIED:CLI Unicode response loss; no repeat or fabricated answer"},
    {"feature": "Full /chat synthesis and follow-up suggestions", "chat_ptu_dependence": "Additional GPT call in original source; current template onlyStandard/GlobalStandard",
     "azure_infrastructure": ["Azure OpenAI", "Consumption ACA backend/frontend", "Cosmos conversation persistence"],
     "verification": "NOT_RUN; directAsk does not prove fullchat/UI"}
]
r["cost"] = c["cost_usd_hour"] | {"currency": "USD", "actual_invoice_cost": None}
r["inference_telemetry"].update(
    live_model_requests=12, retries=0, input_tokens=1899, output_tokens=5872, total_tokens=7771,
    model_latency_ms=latencies, model_latency_caveat=c["model_telemetry"]["latency_caveat"],
    model_http_statuses=[200] * 12, per_deployment=c["model_telemetry"]["by_deployment"],
    model_errors=[], test_transport_errors=["Corpus answer lost to Azure CLI cp1252 UnicodeEncodeError; not repeated"],
    document_intelligence=c["document_intelligence_telemetry"],
    ptu_claim="No PTUs created or tested; all12 OpenAI requests used GlobalStandard.")
r["synthetic_corpus"].update(uploaded=2, indexed=2, requested=10, completed_logical_cases=2,
    original_manifest_files_uploaded=1,
    counting_basis="Two actual documents: original case01 TXT and table-PDF rendition of logical case02; original case02 TXT not uploaded.")
r["functional_summary"] = {
    "requested_mixed_documents": 10, "completed_ingestions": 2, "completed_document_qa": 1,
    "verified": ["private routing", "health", "TXT/PDF table ingestion", "metadata filters",
                 "persisted source hashes", "document-scoped QA/citations", "pause/restart/persistence"],
    "quality_failure": "Both stored summaries contain unsupported greeting text; retained verbatim.",
    "full_app_e2e_passed": False,
    "blocked_or_not_run": ["corpus comparison response uncaptured", "public browser403", "full /chat synthesis",
                           "remaining8 logical cases", "chart", "handwriting", "matched demographic fairness"],
    "accuracy": None
}
r["local_execution"]["application_business_logic_modified"] = False
r["local_execution"]["evaluation_retry_configuration_modified"] = True
r["recommendation"] = (
    "Retain paused resources as authorized; residual estimate$0.245/hour plus shared allocations/usage. "
    "Do not count as fully verified running UI. Twelve-call cap exhausted. A separately authorized repeat of corpus /Documents/Ask needs2 more model attempts; "
    "lossless capture fix was verified without model traffic. Resolve public403 without weakening ingress; evaluate summary grounding before production."
)
save(e / "result.json", r)
budget["cap_exhausted"] = True
budget["further_paid_actions_blocked_reason"] = "All12 OpenAI attempts consumed; no further inference authorized"
save(e / "model-budget.json", budget)
fixture.update(uploaded=True, indexed=True, document_id=second["documentId"], imported_time_utc=second["importedTime"])
save(e / "second-policy-fixture.json", fixture)
manifest_path = b / "test-data/documents/manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for record in manifest["records"]:
    if record["filename"] == "02-policy-2026.txt":
        record.update(uploaded=False, indexed=False, logical_case_completed=True,
                      renditions=[fixture], note="Original TXT remains unuploaded; actual uploaded PDF rendition is recorded explicitly.")
manifest["logical_cases_ingested"] = 2
manifest["actual_uploaded_documents"] = 2
manifest["original_manifest_files_uploaded"] = 1
save(manifest_path, manifest)
tracked = subprocess.check_output(["git","-C",str(repo),"diff"], text=True)
for name in ["App/backend-api/Microsoft.GS.DPS.Host/Helpers/EvaluationRetryConfiguration.cs",
             "App/kernel-memory/service/Abstractions/Configuration/EvaluationRetryConfiguration.cs"]:
    tracked += "".join(difflib.unified_diff([], (repo / name).read_text().splitlines(keepends=True),
                                          fromfile="/dev/null", tofile="b/" + name))
(e / "source-deviations.diff").write_text(tracked, encoding="utf-8")
report = b / "reports/documents.md"
old = report.read_text(encoding="utf-8")
history_marker = "## Historical phase logs"
if history_marker in old:
    history = old.split(history_marker, 1)[1]
    history = history.removeprefix("\n\nEarlier snapshots below are retained for audit, not current runtime/call counts.\n")
else:
    history = old.split("\n", 1)[1].replace("## Current", "## Historical")
current = (b / "reports/documents-current-summary.md").read_text(encoding="utf-8")
report.write_text("# Document Knowledge Mining evaluation\n\n" + current +
                  "\n\n## Historical phase logs\n\nEarlier snapshots below are retained for audit, not current runtime/call counts.\n" +
                  history, encoding="utf-8")
print(json.dumps({"status": r["status"],"model_attempts":12,"tokens":7771,"logical_cases_ingested":2,
                  "paused":True,"provider_latency_ms":latencies,"functional_checks":checks["counts"]}, indent=2))
