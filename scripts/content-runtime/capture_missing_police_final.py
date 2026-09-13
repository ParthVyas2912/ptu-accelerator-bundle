"""Verify and summarize immutable real responses; never rewrite provider/app outputs."""
from collections import Counter
import datetime
import hashlib
import json
import math
from pathlib import Path
import statistics
from claim_acceptance import assert_missing_police_result

bundle = Path(__file__).resolve().parents[2]
evidence = bundle / "evidence" / "content"


def read(name):
    return json.loads((evidence / name).read_text(encoding="utf-8-sig"))


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def usage(rows):
    values = [item for row in rows for item in (row.get("usage") or [])]
    return {
        "promptTokens": sum(item.get("prompt_tokens", 0) for item in values),
        "completionTokens": sum(item.get("completion_tokens", 0) for item in values),
        "totalTokens": sum(item.get("total_tokens", 0) for item in values),
        "reasoningTokensIncludedInCompletion": sum(item.get("completion_tokens_details", {}).get("reasoning_tokens", 0) for item in values),
        "cachedPromptTokensIncludedInPrompt": sum(item.get("prompt_tokens_details", {}).get("cached_tokens", 0) for item in values),
    }


actual = read("isolated-run-result.json")
assert_missing_police_result(actual)
baseline = read("batch-zero-export-complete-recovery.json")["content-call-budget.json"]["requests"]
rows = actual["ledger"]["requests"]
assert rows[:len(baseline)] == baseline
models = [row for row in rows if row["kind"] == "model"]
new_rows = rows[len(baseline):]
new_models = [row for row in new_rows if row["kind"] == "model"]
assert len(models) == 17 and len(new_models) == 6
assert rows[32] == baseline[32] and "status" not in rows[32]
assert all(row["claimId"] == actual["control"]["claimId"] for row in new_rows)
stop = read("cloud-stop-all-all-revisions.json")
assert all(not revision["active"] and revision["replicas"] == 0
           for service in stop["services"] for revision in service["revisions"])
cu_new = [row for row in new_rows if row["kind"] == "cu-analyze"]
pages_new = sum(item.get("documentPagesStandard", 0) for row in new_rows for item in (row.get("usage") or []))
assert len(cu_new) == 2 and pages_new == 2
events = actual["control"]["events"]
admitted = [item for item in events if item["kind"] == "admitted-native-message"]
assert len(admitted) == 13 and all(item["claimId"] == actual["control"]["claimId"] for item in admitted)
deferred = [item for item in events if item["kind"] == "deferred-unrelated"]
old_map_ids = {
    "ad3a7c0c-c6e3-42ed-9ece-528e27af87e6", "9c04bf44-7021-450b-a6c9-4f0d96582c57",
    "d99eca33-195d-43ef-9d9a-2f5e70b89afb", "e13169c0-1f38-4e7d-a291-501c2e1d7f52",
}
assert {item["messageId"] for item in deferred if item["queue"] == "content-pipeline-map-queue"} == old_map_ids
claim = actual["claimDetail"]["data"]
gap = json.loads(claim["process_gaps"])
per_stage = {
    stage: {"modelCalls": len(selected), **usage(selected),
            "latencyMs": [row["elapsed_ms"] for row in selected]}
    for stage in ("map", "rai", "summary", "gaps")
    for selected in [[row for row in new_models if row["stage"] == stage]]
}
summary = {
    "recordedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "passed_missing_police_native_case_with_provider_filter_warning",
    "claimId": actual["control"]["claimId"],
    "case": "Three submitted documents; police report intentionally omitted",
    "fourDocumentHappyPathPassed": False,
    "nativeApiAndFullStagesUsed": True,
    "allThreeDocumentsCompleted": True,
    "targetedSourceFieldAssertionsPassed": True,
    "mappedEvaluatedSavedValuesIdentical": True,
    "rawSourceFile": "evidence/content/isolated-run-result.json",
    "rawSourceSha256": hashlib.sha256((evidence / "isolated-run-result.json").read_bytes()).hexdigest(),
    "original33RequestRowsUnchanged": True,
    "originalElevenModelReservationsSha256": fingerprint([row for row in baseline if row["kind"] == "model"]),
    "originalTenResponseRecordsSha256": fingerprint([row for row in baseline if row["kind"] == "model" and row["id"] != 33]),
    "newModelCalls": 6, "newHttp200Responses": 6,
    "reservedTotal": 17, "returnedModelResponsesTotal": 16, "approvedTotal": 17, "remaining": 0,
    "unknownReservation": rows[32],
    "unknownReservationConservativelySpent": True,
    "newReturnedUsage": usage(new_models),
    "cumulativeKnownReturnedUsage": usage(models),
    "usageCaveat": "Returned usage excludes unobserved usage for reservation33. Do not claim this is the complete provider-billed total.",
    "perStage": per_stage,
    "newCuSubmissions": len(cu_new), "newCuReturnedPagesStandard": pages_new,
    "cumulativeCuSubmissions": sum(row["kind"] == "cu-analyze" for row in rows),
    "cumulativeCuReturnedPagesStandard": sum(item.get("documentPagesStandard", 0) for row in rows for item in (row.get("usage") or [])),
    "cumulativeCuRejected400": sum(row["kind"] == "cu-analyze" and row.get("status") == 400 for row in rows),
    "cuBillingSeparateFromOpenAi": True,
    "documents": [{
        "fileName": item["file_name"], "processId": item["process_id"], "status": item["status"],
        "schemaScore": item["schema_score"], "entityScore": item["entity_score"],
        "nativeProcessedTime": item["processed_time"],
        "inputSha256": actual["control"]["documents"][item["file_name"]]["sha256"],
    } for item in claim["processed_documents"]],
    "nativeRaiResult": json.loads(actual["nativeAgents"]["rai"]["text"]),
    "nativeMissingEvidenceGap": gap["gaps"][0],
    "nativeDiscrepancies": gap["discrepancies"],
    "summaryAndGapPersistedUnmodified": True,
    "providerWarning": {"requestId": 45, "httpStatus": 200, "message": rows[-1]["error"],
                        "interpretation": "Usable native gap output and usage returned, but provider-side content filtering is not verified. Native RAI is a separate check."},
    "syntheticImageCaveat": "Input is a fictional diagram, recognized as such in mapped notes. Native gap inventory counts it as one damage_photo; this does not validate real-photo authenticity.",
    "confidenceCaveat": "Native schema/entity scores are recorded, not treated as measured extraction accuracy.",
    "isolation": {
        "revisionMode": "Multiple", "idleHardDisarmedWorkerImages": True,
        "scopedNativeMessageAdmissions": len(admitted), "unrelatedMessagesDeferredWithoutDeletion": deferred,
        "allFourOriginalMapMessagesDeferred": True,
        "allNewInferenceRecordsBelongToApprovedClaim": True,
        "oneModelAttemptPerLogicalStage": True, "nativeOutputsReplayedOrManuallyMarkedSuccessful": False,
        "priorFailureNotErased": "Earlier zero-inference rollout failed: old revision7 produced CU400 and unfinished reservation33. This successful isolated run does not retroactively remove that failure.",
    },
    "nativeWorkflowElapsed": claim["processed_time"],
    "armedUtc": datetime.datetime.fromtimestamp(actual["control"]["armedAt"], datetime.timezone.utc).isoformat(),
    "disarmedUtc": datetime.datetime.fromtimestamp(actual["control"]["disarmedAt"], datetime.timezone.utc).isoformat(),
    "controlArmedSeconds": actual["control"]["disarmedAt"] - actual["control"]["armedAt"],
    "cloudStop": stop,
    "sourceRepositoryModified": False,
    "deploymentMode": "Adapted private Container Apps native pipeline with safety wrappers, not unchanged stock Azure deployment",
    "images": {
        "api": {"tag": "659eaa1-scope-r1", "digest": "sha256:7d5c97ad6a055fb806e6113fde10aa91af9ee73778d008f46126bf7ef90974e9", "build": "ch13"},
        "processor": {"tag": "659eaa1-scope-r2", "digest": "sha256:93a1cc122f4c32dc4286012c2ed20b3810f425991c17565cb9d0ef324db88799", "build": "ch14"},
        "workflow": {"tag": "659eaa1-scope-r1", "digest": "sha256:5f071948ec4baf8c5ae18a0c816fa7f7b09cae3f58959934b39a5d48ebd25194", "build": "ch12"},
    },
}
(evidence / "missing-police-native-final.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
result = read("result.json")
result["status"] = summary["status"]
result["latestNativeEvaluation"] = summary
result["modelCallsOnHold"] = True
result["modelCallsOnHoldReason"] = "All17 authorized attempt units consumed; live run disarmed and every owned revision inactive."
traffic = result["measuredTraffic"]
known = summary["cumulativeKnownReturnedUsage"]
latencies = [row["elapsed_ms"] for row in models if "elapsed_ms" in row]
traffic.update({
    "liveModelCallsInitiated": None,
    "modelTransmissionCountKnownLowerBound": 16, "modelTransmissionCountKnownUpperBound": 17,
    "sdkReservedModelAttempts": 17, "clientObservedModelHttpResponses": 16,
    "clientObservedModelHttp200Responses": 16, "modelResponsesWithReturnedUsage": 16,
    "modelReservationsWithoutReturnedResponse": 1,
    "requestCapIncludingRetries": 17, "deployedImageAdmissionCap": 17,
    "liveCuAnalysesInitiated": 11, "cuRejected400": 3,
    "returnedInputTokens": known["promptTokens"], "returnedOutputTokens": known["completionTokens"],
    "returnedCachedTokens": known["cachedPromptTokensIncludedInPrompt"],
    "returnedCuDocumentPagesStandard": 8,
    "returnedModelUsage": {"prompt_tokens": known["promptTokens"], "completion_tokens": known["completionTokens"],
                          "total_tokens": known["totalTokens"], "reasoning_tokens_included_in_completion": known["reasoningTokensIncludedInCompletion"],
                          "cached_prompt_tokens_included_in_prompt": known["cachedPromptTokensIncludedInPrompt"]},
    "callSequence": rows, "liveErrors": [row for row in rows if row.get("error")],
    "modelLatencyMs": latencies, "p50Ms": statistics.median(latencies),
    "p95Ms": sorted(latencies)[math.ceil(len(latencies) * 0.95) - 1],
    "latencyStatisticsCaveat": "Sixteen returned synthetic responses; unknown reservation33 excluded. No load/PTU benchmark.",
    "requestLedgerFile": "evidence/content/isolated-run-result.json",
    "requestLedgerSnapshotUtc": actual["capturedUtc"],
    "modelRequestCountReconciliation": "Historical metric6 vs ten initial HTTP200 responses remains unresolved; it predates reservation33 and this six-call run. No new provider metric reconciliation claimed.",
})
for test in result["functionalTests"]:
    if test["id"] == "missing-police":
        test.update(status="passed_native_with_provider_filter_warning",
                    actual="Three native documents Completed with checked saved source fields; RAI IsNotSafe=false; native high-severity REQ-PR-THIRD-PARTY-006 gap explicitly reports missing police_report; six model calls.",
                    evidence="evidence/content/missing-police-native-final.json")
    elif test["id"] == "image-table":
        test.update(status="passed_targeted_source_fields_in_missing_police_case",
                    actual="Native saved diagram fields recognize fictional front-left bumper damage; repair rows1000/1000/500, labor5x200 and total2500 match source. Real-photo authenticity and broad accuracy untested.")
    elif test["id"] == "complete-claim":
        test["actual"] += "; subsequent three-document negative case does not count as a four-document happy-path pass"
for feature in result["featurePtuAndInfrastructure"]:
    name = feature["feature"]
    feature["azureDependencies"] = [
        "Blob/Cosmos direct native access" if dep == "Processed document API" else dep
        for dep in feature["azureDependencies"]]
    if name == "Schema mapping/visual field extraction":
        feature["azureDependencies"].append("Cosmos Mongo schema collection")
        feature["latestMeasuredNativeCase"] = per_stage["map"]
    elif name == "PDF layout/table extraction":
        feature["latestMeasuredNativeCase"] = {"cuSubmissions": 2, "returnedPagesStandard": 2, "customerModelCalls": 0}
    elif name == "Confidence evaluation/merge":
        feature["latestMeasuredNativeCase"] = {"completedDocuments": 3, "newModelCalls": 0, "dependency": "Precached tiktoken o200k_base and actual persisted mappings"}
    elif name == "RAI claim analysis when enabled":
        feature["latestMeasuredNativeCase"] = per_stage["rai"]
    elif name == "Cross-document summary":
        feature["latestMeasuredNativeCase"] = per_stage["summary"]
    elif name == "Gap/VIN/date discrepancy reasoning":
        feature["latestMeasuredNativeCase"] = {**per_stage["gaps"], "missingPoliceRuleVerified": True, "vinDateMismatchNotRun": True}
result["cloudStopState"] = {
    "recordedUtc": stop["checkedUtc"], "source": stop["source"],
    "evidence": "evidence/content/cloud-stop-all-all-revisions.json",
    "resourcesDeleted": [], "requestBudgetReset": False,
    **{service["service"]: service["replicas"] for service in stop["services"]},
}
result["currentBlockers"] = [
    "Budget17/17 exhausted; no further activation/inference authorized.",
    "Four-document happy path and VIN/date discrepancy case remain unpassed/unrun.",
    "Reservation33 provider outcome/usage remains unknown and conservatively spent; prior zero-inference isolation failure is retained.",
    "Gap HTTP200 reported content_filter_error: The contents are not filtered. Provider filtering is not verified despite separate successful native RAI.",
    "Public browser access, production photo authenticity, broad extraction accuracy and PTU sizing remain unverified.",
]
result["recommendation"] = "Keep inference disarmed and every revision inactive. Accept only the evidenced three-document missing-police native case; retain provider-filter warning and four-document limitations."
result["billingAndPtu"]["canadianProcessingResidency"] = "Not established: this approved synthetic MCAPS run used EastUS2 resources and GlobalStandard model processing."
(evidence / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
assert read("result.json")["latestNativeEvaluation"] == read("missing-police-native-final.json")
print(json.dumps({"status": summary["status"], "claimId": summary["claimId"],
                  "newCalls": 6, "totalReserved": 17, "newUsage": summary["newReturnedUsage"],
                  "cuPages": pages_new, "allThreeCompleted": True,
                  "expectedMissingPoliceGap": True, "allOwnedReplicasZero": True}, indent=2))
