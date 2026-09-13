"""Finalize actual advisory budget-stop evidence; no network or inference."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

E = Path(__file__).resolve().parent.parent / "evidence" / "macae"


def read(name):
    return json.loads((E / name).read_text(encoding="utf-8-sig"))


r = read("result-before-advisory.json")
ledger = read("cloud-model-ledger.json")
original = read("cloud-model-ledger-first-pass.json")
state = read("cloud-final-state.json")
plan = read("cloud-advisory-plan.json")
approval = read("cloud-advisory-approval.json")
final = read("cloud-advisory-final.json")
metrics = read("azure-metrics-advisory-final.json")
offline = read("advisory-offline.json")
networking = read("network-agent-type-correction.json")
root_cause = read("advisory-root-cause-review.json")
assert root_cause["investigationLookups"] <= 6
assert root_cause["preservedState"]["modelCallsDuringReview"] == 0
assert root_cause["preservedState"]["cloudWritesDuringReview"] == 0
assert root_cause["preservedState"]["cloudRestartsDuringReview"] == 0
assert networking["operationalInvariants"]["usedModelAttempts"] == 24
assert networking["operationalInvariants"]["modelCallsDuringCorrection"] == 0
assert networking["operationalInvariants"]["azureMutationsDuringCorrection"] == 0
records = sorted(ledger["records"].values(), key=lambda row: row["call_number"])
new = [row for row in records if row["call_number"] >= 13]
known = [row for row in records if row["input_tokens"] is not None]
assert ledger["used"] == ledger["limit"] == len(records) == 24
assert {key: ledger["records"][key] for key in original["records"]} == original["records"]
assert len(new) == 12 and all(row["http_status"] == 200 for row in records)
assert all(row["input_tokens"] is not None and row["output_tokens"] is not None for row in new)
assert approval["httpStatus"] == 200 and approval["submitted"]["approved"] is True
assert isinstance(plan["events"][0]["data"]["plan"], dict)
assert final["terminal"]["status"] == "error"
assert final["nativeTerminalAndBothSpecialistsVerified"] is False
assert set(final["specialistOutputs"]) == {"hrcompliancereviewer", "itreadinessreviewer"}
request = read("cloud-advisory-request.json")["input"]
assert "Handbook acknowledged2026-09-30" in request
assert "training completed2026-09-30" in request
assert final["state"]["plan"]["user_request"] == request
assert "no evidence" in final["specialistOutputs"]["hrcompliancereviewer"].lower()
backend = next(c for c in state["app"]["containers"] if c["name"] == "backend")
digest = "sha256:edb14961ca638605bc54a1f456e1f15ddf6b08eaabf977266b9f3df193b44ad9"
assert backend["gate"] == ["false"] and backend["image"].endswith(digest)
assert state["app"]["scale"]["minReplicas"] == 0 and state["app"]["scale"]["maxReplicas"] == 1
assert state["replicaCount"] == 0
totals = {
    m["name"]["value"]: sum(point.get("total", 0) or 0 for ts in m["timeseries"] for point in ts["data"])
    for m in metrics["value"]
}
assert totals == {"AzureOpenAIRequests": 24, "ProcessedPromptTokens": 36352, "GeneratedTokens": 3997}
new_usage = {field: sum(row[field] for row in new) for field in ("input_tokens", "output_tokens", "cache_tokens")}
assert new_usage == {"input_tokens": 16200, "output_tokens": 2417, "cache_tokens": 1280}
assert totals["ProcessedPromptTokens"] - 20152 == new_usage["input_tokens"]
assert totals["GeneratedTokens"] - 1580 == new_usage["output_tokens"]
r["latestEvidenceUtc"] = datetime.now(timezone.utc).isoformat()
r["status"] = "NATIVE_ADVISORY_TERMINAL_ERROR_AT_24_CALL_CAP_INFERENCE_DISABLED"
r["fullEndToEndSuccess"] = False
r["recommendation"] = "Keep disarmed. Advisory factual fidelity and final synthesis failed; no more model attempts authorized. Preserve original partial onboarding and separate RFP/network/browser limitations."
r["runtime"]["cloud"] = state
r["runtime"]["originalOnboarding"] = {
    key: r["runtime"][key] for key in
    ("workflowRevision", "workflowReplica", "workflowBackendDigest", "sessionId",
     "planId", "internalPlanId", "clarificationRequestId") if key in r["runtime"]
}
r["runtime"].update({
    "workflowRevision": "ptu-macae--0000009",
    "workflowReplica": "ptu-macae--0000009-6bc957fc4d-gvxw6",
    "workflowBackendDigest": digest,
    "sessionId": final["state"]["sessionId"],
    "planId": final["state"]["planId"],
    "internalPlanId": final["state"]["mplanId"],
})
r["runtime"].pop("clarificationRequestId", None)
r["runtime"]["advisory"] = {
    "revision": "ptu-macae--0000009", "replica": "ptu-macae--0000009-6bc957fc4d-gvxw6",
    "sameReplicaRetainedThroughTerminal": True, "state": final["state"],
    "terminal": final["terminal"], "scope": final["scope"],
}
r["modelAccounting"].update({
    "liveAttempts": 24, "limit": 24, "remaining": 0, "newContinuationAttempts": 12,
    "httpStatuses": {"200": 24},
    "byRequestedDeployment": dict(Counter(row["model_requested"] for row in records)),
    "advisoryByRequestedDeployment": dict(Counter(row["model_requested"] for row in new)),
    "advisoryUsage": new_usage,
    "knownUsageSubtotal": {
        "responses": len(known), "inputTokens": sum(row["input_tokens"] for row in known),
        "outputTokens": sum(row["output_tokens"] for row in known),
        "cachedInputTokens": sum(row["cache_tokens"] for row in known), "cacheIsSubsetOfInput": True,
    },
    "responsesWithUncapturedUsage": 5,
    "nextUpstreamAttemptBlocked": True,
    "budgetFinalMigration": read("cloud-budget-final-migration.json"),
    "azureAccountAggregates": {
        "values": totals, "interval": metrics["timespan"], "evidence": "azure-metrics-advisory-final.json",
        "addToSdkSubtotal": False, "completeCachedInputTotal": None, "metricResponseCostIsCurrency": False,
        "deltaMatchesNewSdkInputOutputAndRequests": True,
    },
    "advisoryLatencyMs": {"min": min(row["latency_ms"] for row in new),
                         "max": max(row["latency_ms"] for row in new),
                         "scope": "Observer wall time including wrapper/ledger, not pure service latency"},
})
for title, numbers in (
    ("advisory new-configuration RAI/upload", [13]),
    ("advisory request RAI/scope/facts/plan", [14, 15, 16, 17]),
    ("advisory approved routing/responses including HR reinvocation; no successful synthesis", list(range(18, 25))),
):
    r["modelAccounting"]["phases"].append({
        "phase": title, "callNumbers": numbers, "attempts": len(numbers),
        "byRequestedDeployment": dict(Counter(ledger["records"][str(i)]["model_requested"] for i in numbers)),
    })
r["validation"]["additionalOfflineBudgetObserverTestsPassed"] = 10
r["validation"]["currentEvidence"] = "advisory-offline.json"
r["validation"]["correctedObserverLiveRetest"] = "PASS during real workflow: all twelve new calls captured model/input/output/cache fields; no telemetry-only calls"
r["validation"]["nativePlanSerializationLive"] = "PASS: real structured approval event"
r["validation"]["coverage"] = [c.replace("twenty-two-request", "twenty-four-request") for c in r["validation"]["coverage"]]
r["operations"].update({
    "inferenceEnabled": False, "minReplicas": 0, "maxReplicas": 1,
    "lastObservedReplicaCount": state["replicaCount"],
    "replicaObservationUtc": state["observedAtUtc"], "productionReady": False,
})
r["advisoryOutcome"] = {
    "status": "BUDGET_STOP_AND_FACTUAL_FIDELITY_FAILURE",
    "scope": final["scope"], "specialistCount": 2,
    "selectedNativeTeamEvidence": "advisory-offline.json",
    "expectedNewMinimum": offline["expectedMinimumNewCalls"],
    "actualNewAttempts": 12, "explicitApprovalVerified": True,
    "terminalCompleted": False, "terminal": final["terminal"],
    "specialistOutputs": final["specialistOutputs"],
    "hrResponseInvocationsObserved": 2, "itResponseInvocationsObserved": 1,
    "failure": "App-level fact utilization mismatch: HR leaves handbook/training unmet despite prior-to-start dates in the request and saved plan. Actual specialist messages were not captured; context loss, effective policy and model reasoning cannot be distinguished. Orientation-on-start and missing manager approval are legitimate gaps. HR was reinvoked and final synthesis did not complete.",
    "exactPromptPropagationRootCauseConfirmed": False,
    "perCallPromptBodiesCaptured": False,
    "modelOnlyHallucinationEstablished": False,
    "rootCauseReview": "advisory-root-cause-review.json",
    "orientationFactualErrorEstablished": False,
    "realEnterpriseTransactions": False,
    "evidence": ["cloud-advisory-upload.json", "cloud-advisory-request.json", "cloud-advisory-plan.json",
                 "cloud-advisory-approval.json", "cloud-advisory-final.json", "cloud-model-ledger.json"],
}
r["functionalTests"].extend([
    {"feature": "Fresh native advisory config RAI and two-step plan",
     "expected": "Preserve RAI and encode structured advisory plan", "actual": "PASS: upload/request200 and real structured plan event",
     "evidence": ["cloud-advisory-upload.json", "cloud-advisory-plan.json"]},
    {"feature": "Advisory explicit plan approval", "expected": "Explicit inspected-plan approval",
     "actual": "PASS: approved=true and native approval recorded200", "evidence": "cloud-advisory-approval.json"},
    {"feature": "Advisory factual fidelity and final synthesis", "expected": "Both accurate reviews and completed native synthesis",
     "actual": "FAIL/BUDGET STOP: incorrect HR missing-evidence claims, HR reinvoked, terminal statuserror at24",
     "evidence": "cloud-advisory-final.json"},
])
r["blockingDecisions"] = [
    "No more model calls:24/24 consumed. Do not replay/reset ledger or claim completed advisory synthesis.",
    "Diagnose the app-level fact utilization mismatch and repeated routing before production. Deterministic context loss and model-only hallucination are not established; no further live diagnosis authorized.",
    "RFP/contract service-side private egress is unconfigured and exact existing-account enablement unverified; mandatory account recreation is not established. Public browser403 remains unresolved; no architecture changes or RFP grounding tests performed.",
]
r["continuationInspection"]["isHistoricalSnapshot"] = True
r["continuationInspection"]["supersededBy"] = "advisoryOutcome"
r["networkingClassification"] = networking
r["rootCauseReview"] = root_cause
r["rfpArchitecture"] = networking["rfpArchitecture"]
r["continuationInspection"]["rfpArchitecture"] = networking["rfpArchitecture"]
r["continuationInspection"]["networkingErratum"] = "The blanket account-recreation inference is superseded by network-agent-type-correction.json; historical model accounting is unchanged."
r["remoteAdvisoryBuild"] = {
    "runId": "chs", "reportedSeconds": 33, "archiveKiB": 9.311, "contextFiles": 6,
    "imageDigest": digest, "localBuildsStarted": 0, "status": "Succeeded",
}
r["commandsExecuted"].extend([
    "scripts/Validate-MacaeAdvisory.py (exact native pure parser, zero models)",
    "scripts/Build-MacaeAdvisoryRemote.ps1 (remote ACR chs)",
    "scripts/Invoke-MacaeCloudTest.ps1 -Action advisory-prepare",
    "scripts/Set-MacaeCloudMode.ps1 -Mode EnableInference",
    "scripts/Invoke-MacaeCloudTest.ps1 -Action advisory-plan",
    "scripts/Invoke-MacaeCloudTest.ps1 -Action advisory-approve with observed IDs and Approved true",
    "scripts/Set-MacaeCloudMode.ps1 -Mode Pause after terminal error",
])
(E / "result.json").write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": r["status"], "used": 24, "limit": 24,
                  "newUsage": new_usage, "azureTotals": totals, "replicas": state["replicaCount"]}))
