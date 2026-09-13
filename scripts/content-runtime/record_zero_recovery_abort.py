"""Record the observed recovery abort without altering its immutable source evidence."""
import datetime
import hashlib
import json
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[2]
EVIDENCE = BUNDLE / "evidence" / "content"


def read(name):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8-sig"))


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


baseline = read("inference-result.json")
export = read("batch-zero-export-complete-recovery.json")
rows = export["content-call-budget.json"]["requests"]
original = [row for row in baseline["requestLedger"] if row["kind"] == "model"]
models = [row for row in rows if row["kind"] == "model"]
original_ids = {row["id"] for row in original}
retained = [row for row in models if row["id"] in original_ids]
assert original == retained and len(original) == 10
assert digest(original) == "e8028913511c9377a114de8eb3100a5ebfe94d36d3dba4bffc73ef8840a8b272"
additional = [row for row in models if row["id"] not in original_ids]
assert len(additional) == 1 and additional[0]["id"] == 33
assert "status" not in additional[0] and "usage" not in additional[0]
cu = [row for row in rows if row["kind"] == "cu-analyze"]
assert len(cu) == 9
scope = read("zero-recovery-build-context.json")["scope"]
assert scope["claimId"] == "9f9b9c98-2d6e-440f-9a67-099ffea26f51"
stop = read("cloud-stop-all-all-revisions.json")
assert len(stop["services"]) == 4
assert all(
    not revision["active"] and revision["replicas"] == 0
    for service in stop["services"] for revision in service["revisions"]
)
incident = {
    "recordedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "aborted_rollout_zero_inference_condition_not_met",
    "approvedScope": scope,
    "fullClaimE2ePassed": False,
    "nativeRecoveryWorkerStarted": False,
    "abortReason": "Live ledger has eleven model reservations, not the required ten. Both controller executions failed before Mongo/queue access or native worker startup.",
    "disarmedProcessor": {
        "revision": "ca-ptu-content-processor--0000008",
        "image": "acrptubundle7d804f70.azurecr.io/content/eval-processor:659eaa1-zero-r1",
        "digest": "sha256:fe0f073563841b7b9dd6f5c7faf204129dc05af2d7f977ecc4c46bff55b535a9",
        "remoteBuildRun": "chy",
        "inImageDisarmTestsPassed": 5,
    },
    "rolloutIncident": {
        "observedActiveCallerRevision": "ca-ptu-content-processor--0000007",
        "source": "Client ledger rows32 and33 identify the previous regular Processor revision, not the new hard-disarmed revision8.",
        "additionalCuRequest": next(row for row in rows if row["id"] == 32),
        "additionalModelReservation": additional[0],
        "newModelProviderTransmission": "unknown",
        "newModelHttpStatus": None,
        "newModelReturnedUsage": None,
        "newModelClaimAssociation": "not captured",
        "newModelBudgetCharge": 1,
        "zeroInferenceConditionMetAcrossRollout": False,
        "claimQueueEffects": "Unverified for the previous revision, which could have consumed retained work. The scoped recovery controller never reached queue inspection. No assurance that all original Map retries were untouched is made.",
        "directQueueDeletionOrManualSuccessWrites": False,
        "fakeResponsesOrCrossClaimReplay": False,
    },
    "ledgerSnapshotUtc": export["localCaptureUtc"],
    "liveSnapshotFile": "evidence/content/batch-zero-export-complete-recovery.json",
    "liveModelReservations": len(models),
    "returnedModelResponses": len(original),
    "originalTenRecordsIdentical": True,
    "originalTenModelSha256": digest(original),
    "liveElevenModelSha256": digest(models),
    "budgetResetOrRecordRewrite": False,
    "returnedUsageTotals": {
        "promptTokens": 39760, "completionTokens": 23301, "totalTokens": 63061,
        "caveat": "Ten returned responses only; reservation33 has no captured usage. These are not a verified current total of provider-billed tokens.",
    },
    "cuSubmissionsObserved": len(cu),
    "cuSuccessfulReturnedPages": 6,
    "cuRejected400": sum(row.get("status") == 400 for row in cu),
    "previouslyOmittedCuRetry": next(row for row in rows if row["id"] == 31),
    "documentRecovery": [
        dict(document, recoveryVerified=False,
             actualOutcome="Not freshly inspected: ledger precondition aborted before artifact/DB access.")
        for document in scope["documents"]
    ],
    "nativeWholeClaimCheckpointReuse": {
        "supported": False,
        "evidence": "ClaimProcessor starts document_processing; DocumentProcessExecutor submits every file; ContentProcessService.submit creates a fresh UUID and Extract message.",
        "observedNormalRunModelCalls": 7,
        "currentAllocation": 12,
        "conservativeBudgetUsed": 11,
        "cleanRunConservativeTotalCeiling": 18,
        "additionalAllocationNeededForThatPlan": 6,
        "additionalCallsRequestedOrAuthorizedHere": False,
    },
    "shutdownCorrection": {
        "priorChecks": "Latest-revision-only zero counts did not prove all-revision shutdown.",
        "observedOlderApiRevision": "ca-ptu-content-api--0000008",
        "observedOlderApiReplicas": 1,
        "action": "Older API and all active revisions explicitly deactivated. Stop now checks all revisions and never redeploys an image.",
        "deploymentInterlock": "Deploy-ContentCloud.ps1 rejects deployments while result.json modelCallsOnHold is true; do not clear without coordinated authorization/isolation.",
        "offlineLifecycleRegressionTestsPassed": 2,
    },
    "finalStop": stop,
    "paidCallsRemainOnHold": True,
    "decision": "Do not reset the eleven-reservation ledger or weaken its recovery gate. Stop and return the incident; resolve rollout-wide disarm and reservation33 before any further recovery.",
}
(EVIDENCE / "zero-model-recovery-abort.json").write_text(
    json.dumps(incident, indent=2) + "\n", encoding="utf-8"
)
result = read("result.json")
result["status"] = "paused_all_revisions_zero_recovery_aborted_previous_revision_activity"
result["zeroModelRecovery"] = incident
result["modelCallsOnHold"] = True
traffic = result["measuredTraffic"]
traffic.update({
    "liveModelCallsInitiated": None,
    "modelTransmissionCountKnownLowerBound": 10,
    "modelTransmissionCountKnownUpperBound": 11,
    "sdkReservedModelAttempts": 11,
    "clientObservedModelHttpResponses": 10,
    "modelReservationsWithoutReturnedResponse": 1,
    "modelTransmissionCountCaveat": "Additional reservation33 has no recorded transport outcome; do not equate all eleven reservations to returned/provider requests.",
    "liveCuAnalysesInitiated": 9,
    "cuRejected400": 3,
    "callSequence": rows,
    "liveErrors": [row for row in rows if row.get("error")],
    "requestLedgerFile": incident["liveSnapshotFile"],
    "requestLedgerSnapshotUtc": export["localCaptureUtc"],
    "returnedUsageCaveat": incident["returnedUsageTotals"]["caveat"],
    "modelRequestCountReconciliation": "Historical ten HTTP200 responses versus six Azure requests remain unresolved; the later unfinished reservation33 is outside that metric snapshot window and is separately counted.",
})
result["cloudStopState"] = {
    "recordedUtc": stop["checkedUtc"], "source": stop["source"],
    "evidence": "evidence/content/cloud-stop-all-all-revisions.json",
    "resourcesDeleted": [], "requestBudgetReset": False,
    **{service["service"]: service["replicas"] for service in stop["services"]},
}
result["currentBlockers"] = [
    "Recovery aborted: previous Processor revision7 recorded CU400 and additional unfinished model reservation33 during rollout. Ten original returned records are unchanged, but zero-inference isolation was not maintained.",
    "Four approved recovery-claim document outcomes were not freshly verified; controller stopped before Mongo/queue access.",
    "Budget remains on hold: eleven reservations, ten HTTP200 responses, one unknown transmission/outcome. No budget reset or extra approval.",
    "Original Map/other retained queue work must be isolated; prior revision's exact queue effects remain unverified.",
    "Native whole-claim rerun does not reuse existing artifacts; observed path is seven model calls, not a supported three-call tail resume.",
    "Full claim E2E and public browser walkthrough remain unpassed/unverified.",
]
result["recommendation"] = incident["decision"]
result["inferenceEvaluation"]["historicalSnapshotNote"] = (
    "Preserved earlier run evidence, not current reservation/CU totals or all-revision shutdown proof. "
    "See zeroModelRecovery and measuredTraffic for the subsequent rollout incident."
)
(EVIDENCE / "result.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(json.dumps({
    "status": result["status"], "originalTenIdentical": True,
    "modelReservations": len(models), "responses": len(original),
    "cuSubmissions": len(cu), "allRetainedRevisionsZero": True,
    "artifact": "evidence/content/zero-model-recovery-abort.json",
}, indent=2))
