"""Produce current evidence without spending inference or altering Azure state."""
import json
from datetime import datetime, timezone
from pathlib import Path

E = Path(__file__).resolve().parent.parent / "evidence" / "macae"


def read(name):
    return json.loads((E / name).read_text(encoding="utf-8-sig"))


r = read("result-first-pass-final.json")
ledger = read("cloud-model-ledger.json")
original = read("cloud-model-ledger-first-pass.json")
state = read("cloud-final-state.json")
inspection = read("second-pass-inspection.json")
migration = read("cloud-budget-migration.json")
source = read("cloud-serialization-source.json")
metrics = read("azure-metrics-final.json")
assert ledger["limit"] == 22 and ledger["used"] == 12
assert ledger["records"] == original["records"]
assert migration["priorRecordsPreserved"]
assert migration["beforeRecordsSha256"] == migration["afterRecordsSha256"]
assert source["sha256"] == inspection["nativeFix"]["sourceSha256"]
backend = next(c for c in state["app"]["containers"] if c["name"] == "backend")
assert backend["gate"] == ["false"]
assert backend["image"].endswith(inspection["remoteBuild"]["digest"])
assert state["app"]["scale"]["minReplicas"] == 0 and state["app"]["scale"]["maxReplicas"] == 1
totals = {
    m["name"]["value"]: sum(point.get("total", 0) or 0 for ts in m["timeseries"] for point in ts["data"])
    for m in metrics["value"]
}
assert totals["AzureOpenAIRequests"] == 12
assert totals["ProcessedPromptTokens"] == 20152
assert totals["GeneratedTokens"] == 1580
r["latestEvidenceUtc"] = datetime.now(timezone.utc).isoformat()
r["status"] = "NATIVE_SERIALIZER_FIXED_PAUSED_MINIMUM_WORKFLOW_CALLS_EXCEED_REMAINING_ALLOWANCE"
r["recommendation"] = inspection["requiredDecision"]
r["repository"]["trackedChanges"] = [
    "src/backend/orchestration/connection_config.py",
    "src/tests/backend/orchestration/test_connection_config.py",
]
r["repository"]["patchEvidence"] = "native-serialization.patch"
r["runtime"]["cloud"] = state
r["runtime"]["privateDataProbe"] = read("cloud-readiness.json")
r["modelAccounting"]["limit"] = 22
r["modelAccounting"]["remaining"] = 10
r["modelAccounting"]["newContinuationAttempts"] = 0
r["modelAccounting"]["budgetMigration"] = migration
r["modelAccounting"]["nextUpstreamAttemptBlocked"] = "Disabled inference flag; balance is ten, not exhausted"
r["modelAccounting"]["azureAccountAggregates"] = {
    "values": totals, "interval": metrics["timespan"], "evidence": "azure-metrics-final.json",
    "scope": "Dedicated MACAE account; separate independent metric source",
    "addToSdkSubtotal": False, "completeCachedInputTotal": None,
    "metricResponseCostIsCurrency": False,
}
r["validation"]["currentNativeSerializationTargetedTestsPassed"] = 39
r["validation"]["currentEvidence"] = "second-pass-inspection.json"
r["validation"]["additionalOfflineBudgetObserverTestsPassed"] = 9
r["validation"]["correctedObserverLiveRetest"] = "NOT RUN; offline mini model/input/output/cache JSON and SSE capture verified"
r["validation"]["coverage"] = [
    c.replace("twelve-request", "twenty-two-request") for c in r["validation"]["coverage"]
] + ["Exact idempotent12-to22 migration", "Native structured plan/replan payloads"]
r["operations"]["lastObservedReplicaCount"] = state["replicaCount"]
r["operations"]["replicaObservationUtc"] = state["observedAtUtc"]
r["continuationInspection"] = inspection
r["nativeSerializationFixDeployed"] = True
r["deviations"] = [d for d in r["deviations"] if d != "No modification to tracked original repository source"]
r["deviations"].append("Requested native WebSocket serialization fix; two tracked source/test files changed")
r["functionalTests"].append({
    "feature": "Native serialization remediation",
    "expected": "Structured plan/replan payloads, no blanket str fallbacks",
    "actual": "PASS39 targeted offline tests; deployed source hash matches; no fabricated or new live workflow events",
    "evidence": ["native-serialization.patch", "cloud-serialization-source.json", "second-pass-inspection.json"],
})
for test in r["functionalTests"]:
    if test["feature"] == "IT onboarding and final synthesis":
        test["currentBlocker"] = "Old in-memory checkpoint lost; fresh three-specialist minimum12 > remaining10"
r["blockingDecisions"] = [
    inspection["requiredDecision"],
    "RFP/contract service-side private egress is unconfigured; the exact existing-account path is unverified, not proven immutable. See network-agent-type-correction.json; no new infrastructure or grounding test authorized",
    "Cloud browser403 remains unresolved; no ingress changes",
]
r["commandsExecuted"].extend([
    "python -m pytest src/tests/backend/orchestration/test_connection_config.py -q --disable-warnings",
    "scripts/Build-MacaePatchRemote.ps1 -Retry (one corrected client-path retry; ACR run chn)",
    "scripts/Invoke-MacaeCloudTest.ps1 -Action second-pass-admin (one authenticated exec)",
    "az monitor metrics list (three named metrics, own dedicated account, Total, PT1M)",
    "scripts/Set-MacaeCloudMode.ps1 -Mode Pause",
])
r["historicalEvidence"].extend(["result-first-pass-final.json", "cloud-model-ledger-first-pass.json"])
(E / "result.json").write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": r["status"], "used": 12, "limit": 22, "remaining": 10,
                  "replicas": state["replicaCount"], "azureMetrics": totals}))
