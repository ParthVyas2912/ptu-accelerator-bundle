"""Persist measured inference, failures, negative results and current stop state."""
import datetime
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

BUNDLE = Path(__file__).resolve().parents[2]
FOLDER = BUNDLE / "evidence/content"
SUB = "1feb53b2-854a-4ea7-b5a6-709b7d804f70"


def az(arguments):
    arguments += ["--subscription", SUB, "-o", "json"]
    quoted = ",".join("'" + value.replace("'", "''") + "'" for value in arguments)
    response = subprocess.run(["pwsh", "-NoProfile", "-Command",
        f"& '{BUNDLE / 'Invoke-LabAz.ps1'}' -AzArguments @({quoted})"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if response.returncode:
        raise RuntimeError("Guarded state capture failed: " + response.stderr[:1000])
    return json.loads(response.stdout)


latest = json.loads((FOLDER / "batch-run-complete-recovery.json").read_text())
evidence = latest["evidence"]
negative = json.loads((FOLDER / "batch-negative-complete.json").read_text())["negative"]
rows = evidence["content-call-budget.json"]["requests"]
models = [row for row in rows if row["kind"] == "model"]
page_reports = {}
for row in rows:
    if row["kind"] == "cu-poll" and row.get("usage"):
        page_reports[row["operation"]] = sum(
            usage.get("documentPagesStandard", 0) for usage in row["usage"])
token_totals = {
    key: sum(usage.get(key, 0) for row in models for usage in row.get("usage") or [])
    for key in ("prompt_tokens", "completion_tokens", "total_tokens")}
token_totals["reasoning_tokens_included_in_completion"] = sum(
    usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    for row in models for usage in row.get("usage") or [])
token_totals["cached_prompt_tokens_included_in_prompt"] = sum(
    usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
    for row in models for usage in row.get("usage") or [])
state = {"recordedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "source": "Fresh guarded ARM replica list, one query per owned service",
         "resourcesDeleted": [], "requestBudgetReset": False}
reuse = "--reuse-capture" in sys.argv
previous = json.loads((FOLDER / "inference-result.json").read_text()) if reuse else None
if reuse:
    state = previous["stopState"]
else:
    for service in ("api", "processor", "workflow", "web"):
        replicas = az(["containerapp", "replica", "list", "-g", "rg-ptu-content-demo",
                       "-n", "ca-ptu-content-" + service])
        state[service] = len(replicas)
(FOLDER / "cloud-stop-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
if any(state[service] for service in ("api", "processor", "workflow", "web")):
    raise RuntimeError("Some compute remains active; do not claim a zero-replica stop")
apps = previous["apps"] if reuse else az(["containerapp", "list", "-g", "rg-ptu-content-demo", "--query",
    "[].{name:name,id:id,latestRevision:properties.latestRevisionName,readyRevision:properties.latestReadyRevisionName,ingress:properties.configuration.ingress,scale:properties.template.scale,containers:properties.template.containers}"])
throughput = previous["mongoSharedThroughput"] if reuse else az(["cosmosdb", "mongodb", "database", "throughput", "show",
    "-g", "rg-ptu-content-demo", "-a", "cosmos-ptuv-content-260911", "-n", "ptu-content-db",
    "--query", "{throughput:resource.throughput,autoscale:resource.autoscaleSettings}"])
assert throughput["throughput"] == 400 and not throughput["autoscale"]
builds = previous["newBuilds"] if reuse else [az(["acr", "task", "show-run", "--registry", "acrptubundle7d804f70",
    "--run-id", run, "--query",
    "{runId:runId,status:status,start:startTime,finish:finishTime,images:outputImages}"])
    for run in ("chj", "chk", "chm", "chp", "chq")]
summary = {
    "capturedUtc": state["recordedUtc"], "fullClaimE2ePassed": False,
    "deploymentMode": "Adapted private container deployment on the approved shared Consumption platform",
    "preflight": evidence["ai-preflight.json"], "modelAttempts": len(models),
    "modelHttpStatusCounts": {str(code): sum(row.get("status") == code for row in models)
                             for code in sorted({row.get("status") for row in models})},
    "modelTokens": token_totals,
    "cuAnalysisSubmissions": sum(row["kind"] == "cu-analyze" for row in rows),
    "cuSuccessfulPageReports": page_reports,
    "cuReturnedDocumentPagesStandard": sum(page_reports.values()),
    "cuRejectedSubmissions": sum(row["kind"] == "cu-analyze" and row.get("status") == 400 for row in rows),
    "failedCuChargeablePages": None,
    "apiRequestsRecorded": len(evidence["functional-results.json"]["apiCalls"]),
    "originalClaim": "77f4a16d-96fe-4739-b90a-9ac0b2597bb4",
    "recoveryClaim": "9f9b9c98-2d6e-440f-9a67-099ffea26f51",
    "observedFailure": "Both claim records say Completed despite four Error documents; downstream summary/gap operated without successfully completed documents",
    "schemaRepair": evidence["schema-name-repair.json"],
    "tokenizerRepair": {
        "image": "content/eval-processor:659eaa1-r4",
        "buildRun": "chq",
        "method": "Precache official tiktoken o200k_base during credential-free remote build; runtime guard remains enabled",
        "verification": "Original confidence evaluator passed inside image with runtime guard; live police-report extract/map/evaluate outputs subsequently recovered",
        "remainingDocuments": "Other three step-output exports still held previous errors at last read; no successful full-claim tail rerun"},
    "negativeSingleFile": negative,
    "requestLedger": rows,
    "remainingModelAllowance": 12 - len(models),
    "requestedDecision": {
        "additionalAttempts": 5, "proposedTotalCap": 17,
        "purpose": "One clean four-document claim after both dependency fixes",
        "observedPerClaimPlan": {"mapping": 4, "rai": 1, "summary": 1, "gap": 1},
        "newInfrastructure": False, "notYetAuthorized": True,
        "missingPoliceAndMismatch": "Not executed; additional variants require a separately bounded budget after clean E2E"},
    "apps": apps, "newBuilds": builds, "mongoSharedThroughput": throughput,
    "stopState": state, "publicBrowserVerified": False,
    "noPtuPurchaseOrEvaluation": True, "runtimeMongoRoleUnchanged": True,
    "protectedDataPlaneCalls": 0}
assert len(models) == 10 and len(models) <= 12
assert token_totals["total_tokens"] == 63061
assert summary["cuReturnedDocumentPagesStandard"] == 6
assert negative["passed"] and negative["modelAttemptsBefore"] == negative["modelAttemptsAfter"]
(FOLDER / "inference-result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
result_path = FOLDER / "result.json"
result = json.loads(result_path.read_text())
result["status"] = "real_cu_and_mapping_executed_negative_passed_full_claim_failed_compute_paused_budget_decision_required"
result["inferenceEvaluation"] = summary
result["cloudStopState"] = state
result["cloudApplication"]["apps"] = apps
result["cloudApplication"]["application"] = evidence
result["cloudApplication"]["capturedUtc"] = state["recordedUtc"]
result["cloudApplication"]["probe"] = {
    "ai": evidence["ai-preflight.json"],
    "earlierStorageQueueMongoChecks": "cloud-real-api-observed.json"}
by_run = {item["runId"]: item for item in result["cloudApplication"]["builds"]}
by_run.update({item["runId"]: item for item in builds})
result["cloudApplication"]["builds"] = list(by_run.values())
traffic = result["measuredTraffic"]
traffic.setdefault("historicalPrePrivateEndpointErrors", traffic.get("liveErrors", []))
latencies = [row["elapsed_ms"] for row in models]
result["measuredTraffic"].update({
    "liveModelCallsInitiated": len(models), "liveCuAnalysesInitiated": summary["cuAnalysisSubmissions"],
    "returnedModelUsage": token_totals, "returnedCuDocumentPagesStandard": 6,
    "requestLedgerFile": "evidence/content/inference-result.json",
    "callSequence": rows,
    "returnedInputTokens": token_totals["prompt_tokens"],
    "returnedOutputTokens": token_totals["completion_tokens"],
    "returnedCachedTokens": token_totals["cached_prompt_tokens_included_in_prompt"],
    "modelLatencyMs": latencies,
    "p50Ms": statistics.median(latencies),
    "p95Ms": sorted(latencies)[math.ceil(len(latencies) * .95) - 1],
    "latencyStatisticsCaveat": "Only10 synthetic model requests, no load; p95 uses nearest rank and is not a PTU sizing benchmark",
    "cuMetadataRequests": traffic.get("cuMetadataRequests", [])[:1] + [
        row for row in rows if row["kind"] == "cu-metadata"],
    "liveErrors": [row for row in rows if row.get("error")]})
result["realApiTests"]["apiRequestCount"] = summary["apiRequestsRecorded"]
result["realApiTests"]["cases"] = evidence["functional-results.json"]["cases"]
result["endpointsAndProcesses"]["runningCloudReplicas"] = 0
result["currentBlockers"] = [
    "Only two model attempts remain; request five additional (total cap17) for one clean seven-call claim after both fixes",
    "Upstream claim Completed status masks document failures; no successful full-claim summary/gap result is claimed",
    "Retained old map messages are deferred until2026-09-12T04:26:20Z; handle them before any future Processor warm-up",
    "Public browser walkthrough remains unverified"]
result["cloudSafeguards"]["resumeDriverUpdate"] = "API r6 retains duplicate-safe submission plus batched execution and real corrupt-file tests; Processor r4 has guarded tokenizer cache."
result["costCaveatsCurrent"]["privateEndpointsCreated"] = 4
result["costCaveatsCurrent"]["currentReplicaCount"] = 0
for test in result["functionalTests"]:
    if test["id"] == "complete-claim":
        test.update(status="failed_end_to_end", actual=summary["observedFailure"])
    elif test["id"] == "corrupt-unsupported":
        test.update(status="passed_http_validation_and_downstream_rejection_dlq_unverified",
                    actual="Bad-magic/unsupported uploads415; separate real truncated-PDF pipeline202->500 after CU400, zero new model calls. DLQ not observed.")
    elif test["id"] in ("visual-table", "image-table-extraction", "image-table"):
        test.update(status="partial_cu_and_model_mapping", actual="Real CU and four structured model mappings executed; confidence/save failures prevented complete visual/table acceptance.")
result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({key: summary[key] for key in (
    "modelAttempts", "modelTokens", "cuAnalysisSubmissions", "cuReturnedDocumentPagesStandard",
    "apiRequestsRecorded", "fullClaimE2ePassed", "remainingModelAllowance", "stopState")}, indent=2))
