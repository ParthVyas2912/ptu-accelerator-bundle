"""Compare saved client responses and the parent metric snapshot; no network calls."""
import datetime
import hashlib
import json
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[2]
FOLDER = BUNDLE / "evidence/content"
metric_path = BUNDLE / "evidence/model-metrics/aif-ptuv-content-260911.json"
raw_bytes = metric_path.read_bytes()
raw = json.loads(raw_bytes)
inference_path = FOLDER / "inference-result.json"
inference = json.loads(inference_path.read_text())
models = [row for row in inference["requestLedger"] if row["kind"] == "model"]
model_hash = hashlib.sha256(json.dumps(models, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
assert model_hash == "e8028913511c9377a114de8eb3100a5ebfe94d36d3dba4bffc73ef8840a8b272"

metrics = {}
for metric in raw["value"]:
    points = {}
    for series in metric["timeseries"]:
        dimensions = {item["name"]["value"].lower(): item["value"]
                      for item in series.get("metadatavalues", [])}
        if dimensions.get("modeldeploymentname") != "gpt-5.1":
            continue
        for point in series["data"]:
            if point.get("total") is not None:
                points[point["timeStamp"]] = points.get(point["timeStamp"], 0) + point["total"]
    metrics[metric["name"]["value"]] = {
        "total": sum(points.values()) if points else None, "points": points}

observations = []
for ordinal, row in enumerate(models, 1):
    usage = row.get("usage") or []
    assert row.get("status") == 200 and not row.get("error") and usage
    observations.append({
        "attemptOrdinal": ordinal, "ledgerId": row["id"], "service": row["service"],
        "startedUtc": row["started"], "host": row["host"], "path": row["path"],
        "httpStatusObserved": row["status"], "elapsedMs": row["elapsed_ms"],
        "promptTokensReturned": sum(item["prompt_tokens"] for item in usage),
        "completionTokensReturned": sum(item["completion_tokens"] for item in usage),
        "error": row["error"]})
groups = {}
for service in ("processor", "workflow"):
    subset = [item for item in observations if item["service"] == service]
    groups[service] = {
        "responseCount": len(subset),
        "promptTokensReturned": sum(item["promptTokensReturned"] for item in subset),
        "completionTokensReturned": sum(item["completionTokensReturned"] for item in subset)}
assert len(models) == 10
assert sum(item["promptTokensReturned"] for item in observations) == metrics["ProcessedPromptTokens"]["total"]
assert sum(item["completionTokensReturned"] for item in observations) == metrics["GeneratedTokens"]["total"]

matches = []
for minute, ids in (
    ("2026-09-12T02:17:00Z", [10, 11, 12]),
    ("2026-09-12T02:29:00Z", [20]),
    ("2026-09-12T02:30:00Z", [24, 25]),
    ("2026-09-12T02:31:00Z", [26]),
    ("2026-09-12T02:32:00Z", [27, 28, 29])):
    selected = [item for item in observations if item["ledgerId"] in ids]
    prompt = sum(item["promptTokensReturned"] for item in selected)
    completion = sum(item["completionTokensReturned"] for item in selected)
    assert metrics["ProcessedPromptTokens"]["points"][minute] == prompt
    assert metrics["GeneratedTokens"]["points"][minute] == completion
    matches.append({
        "metricMinuteUtc": minute, "matchingLedgerIdsByTokenTotals": ids,
        "clientResponseCount": len(selected),
        "azureRequestMetric": metrics["AzureOpenAIRequests"]["points"].get(minute),
        "matchingPromptTokens": prompt, "matchingCompletionTokens": completion})

reconciliation = {
    "createdUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "modelRecordSha256Unchanged": model_hash,
    "metricSnapshotFile": str(metric_path), "metricSnapshotSha256": hashlib.sha256(raw_bytes).hexdigest(),
    "metricTimespan": raw["timespan"], "metricInterval": raw["interval"],
    "deploymentDimension": "gpt-5.1",
    "sdkReservationsChargedToBudget": 10,
    "clientObservedHttpResponses": 10, "clientObservedHttp200": 10,
    "responsesWithParsedUsage": 10, "reservedWithoutReturnedResponse": 0,
    "reservedModelTransportErrorsRecorded": 0,
    "azureOpenAIRequestsSnapshot": metrics["AzureOpenAIRequests"]["total"],
    "azureProcessedPromptTokensSnapshot": metrics["ProcessedPromptTokens"]["total"],
    "azureGeneratedTokensSnapshot": metrics["GeneratedTokens"]["total"],
    "tokenTotalsMatch": True, "requestCountAgreement": False,
    "responseGroups": groups, "responseEvidence": observations, "matchingTokenBuckets": matches,
    "httpEvidenceBoundary": "content_guard.py records response.status_code and parses response content only after the underlying HTTPX send returns; status200 is not a reservation default",
    "tokenizerFailureBoundary": "Evaluate called tiktoken after reading the saved mapping response. The subsequent unapproved public-asset GET was blocked before transmission and did not reserve a model attempt.",
    "fourMappingsWereLocalFailuresBeforeModelTransmission": False,
    "limits": [
        "Raw HTTP headers and Azure request IDs were not retained, so there is no per-request server-ID reconciliation",
        "Token-bucket correspondence is arithmetic corroboration, not unique server request-ID correlation",
        "The cause of the six-versus-ten request-count difference is unresolved; reporting delay or differing metric behavior is not established",
        "Do not add account and deployment totals, rewrite Azure metric6 as10, or credit four attempts back to the budget"],
    "newCloudOrModelCalls": 0, "budgetUsedRemains": 10}
(FOLDER / "model-metric-reconciliation.json").write_text(
    json.dumps(reconciliation, indent=2), encoding="utf-8")
inference["modelMetricReconciliation"] = reconciliation
inference_path.write_text(json.dumps(inference, indent=2), encoding="utf-8")
result_path = FOLDER / "result.json"
result = json.loads(result_path.read_text())
result["modelMetricReconciliation"] = reconciliation
result["inferenceEvaluation"]["modelMetricReconciliation"] = reconciliation
result["measuredTraffic"].update({
    "sdkReservedModelAttempts": 10, "clientObservedModelHttpResponses": 10,
    "clientObservedModelHttp200Responses": 10, "modelResponsesWithReturnedUsage": 10,
    "azureOpenAIRequestsMetricSnapshot": metrics["AzureOpenAIRequests"]["total"],
    "modelRequestCountReconciliation": "Unresolved:10 client-observed HTTP200+usage responses versus6 in the saved Azure request metric; token totals match"})
assert result["measuredTraffic"]["liveModelCallsInitiated"] == 10
result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"clientHttp200WithUsage": len(observations), "groups": groups,
                  "azureRequestMetric": reconciliation["azureOpenAIRequestsSnapshot"],
                  "matchingTokenBuckets": matches, "recordsUnchanged": True,
                  "newCalls": 0}, indent=2))
