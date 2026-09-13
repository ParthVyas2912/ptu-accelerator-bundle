"""Reconcile the cap17 approval with preserved attempt evidence, without cloud calls."""
import datetime
import hashlib
import json
from pathlib import Path


bundle = Path(__file__).resolve().parents[2]
evidence = bundle / "evidence" / "content"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


contract_path = bundle / "deployment-contract.json"
contract = read(contract_path)
budget = contract["modelAttemptBudget"]
approved = budget["contentApprovedTotal"]
assert approved == 17 and budget["portfolioMaximum"] == 100
assert budget["allocatedTotal"] == 100 and budget["centrallyReserved"] == 0
snapshot = read(evidence / "batch-zero-export-complete-recovery.json")
models = [row for row in snapshot["content-call-budget.json"]["requests"] if row["kind"] == "model"]
baseline = [row for row in read(evidence / "inference-result.json")["requestLedger"] if row["kind"] == "model"]
ids = {row["id"] for row in baseline}
assert [row for row in models if row["id"] in ids] == baseline
assert len(baseline) == 10 and len(models) == 11
assert [row["id"] for row in models if "status" not in row] == [33]
stop = read(evidence / "cloud-stop-all-all-revisions.json")
assert {service["service"] for service in stop["services"]} == {"api", "processor", "workflow", "web"}
assert all(not revision["active"] and revision["replicas"] == 0
           for service in stop["services"] for revision in service["revisions"])
preflight = {
    "recordedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "not_started_clean_native_run_exceeds_remaining_approved_attempts",
    "approvedTotal": approved,
    "contractSha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
    "portfolioMaximum": budget["portfolioMaximum"],
    "portfolioAllocated": budget["allocatedTotal"],
    "portfolioReserve": budget["centrallyReserved"],
    "latestCapturedModelReservations": len(models),
    "latestCapturedModelResponses": len(baseline),
    "unresolvedReservationId": 33,
    "unresolvedReservationRefunded": False,
    "originalTenResponseRecordsUnchanged": True,
    "ledgerSnapshotUtc": snapshot["localCaptureUtc"],
    "remainingApprovedAttempts": approved - len(models),
    "nativeCleanRunModelPlan": {"documentMappings": 4, "responsibleAi": 1, "summary": 1, "gaps": 1},
    "nativeCleanRunCalls": 7,
    "nativeWholeClaimCheckpointReuseSupported": False,
    "nativeReuseEvidence": "evidence/content/zero-model-recovery-abort.json",
    "minimumTotalForObservedCleanPlan": len(models) + 7,
    "shortfall": len(models) + 7 - approved,
    "zeroRecoveryState": "Previously aborted, not in progress; unchanged ledger gate still rejects the additional reservation.",
    "cleanClaimCreated": False,
    "cleanClaimSubmitted": False,
    "newModelOrCuCallsThisTurn": 0,
    "newInfrastructureOrDeploymentThisTurn": False,
    "fullClaimE2ePassed": False,
    "allFourDocumentOutcomesFreshlyVerified": False,
    "decision": "Do not refund unknown reservation33 or spend six attempts on a known seven-call plan. Keep deployment interlocked and all revisions inactive; cap18 is not authorized.",
    "shutdown": stop,
    "inferenceSafety": {
        "processorCurrentImage": "eval-processor:659eaa1-zero-r1",
        "processorImageHardDisarmed": True,
        "allOwnedRevisionsInactive": True,
        "deploymentInterlockRetained": True,
        "deployedImageAdmissionCap": 12,
        "deployedCapNote": "Approval17 is recorded, but no image was rebuilt/activated; the older lower runtime cap was not presented as an applied cap17.",
    },
}
target = evidence / "clean-run-cap17-preflight.json"
target.write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")
result_path = evidence / "result.json"
result = read(result_path)
result["status"] = preflight["status"]
result["latestBudgetPreflight"] = preflight
result["modelCallsOnHold"] = True
result["modelCallsOnHoldReason"] = "Operational disarm: approval17 is valid, but eleven preserved reservations leave only six attempts for the required seven-call native plan."
result["measuredTraffic"]["requestCapIncludingRetries"] = approved
result["measuredTraffic"]["deployedImageAdmissionCap"] = 12
result["cloudStopState"] = {
    "recordedUtc": stop["checkedUtc"], "source": stop["source"],
    "evidence": "evidence/content/cloud-stop-all-all-revisions.json",
    "resourcesDeleted": [], "requestBudgetReset": False,
    **{service["service"]: service["replicas"] for service in stop["services"]},
}
result["currentBlockers"] = [
    "Cap17 is approved, not missing. Eleven preserved reservations leave six; the observed native four-document plus RAI/summary/gaps path requires seven.",
    "Reservation33 has unknown provider outcome and cannot be refunded; a seven-call clean run would require total18, which is not authorized.",
    "No native whole-claim checkpoint reuse was found. Prior scoped Evaluate/Save recovery aborted before worker startup; per-document recovery remains unverified.",
    "Retained old work must remain isolated and the earlier rollout incident resolved before any safe runtime restart.",
    "Full claim E2E and public browser walkthrough remain unpassed/unverified.",
]
result["recommendation"] = preflight["decision"]
result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
assert read(result_path)["latestBudgetPreflight"] == read(target)
print(json.dumps({
    "approved": approved, "reserved": len(models), "remaining": approved - len(models),
    "nativePlan": 7, "shortfall": 1, "newModelOrCuCalls": 0,
    "allOwnedRevisionsInactiveZero": True, "status": preflight["status"],
}, indent=2))
