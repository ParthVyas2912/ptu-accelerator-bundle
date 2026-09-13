"""Read-only dependency/contract verification; never imports cloud clients."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

BUNDLE = Path(__file__).resolve().parents[2]
REPO = Path.home() / "OneDrive - Microsoft/Desktop/repo/content-processing-solution-accelerator"
FOLDER = BUNDLE / "evidence/content"
BASELINE = "e8028913511c9377a114de8eb3100a5ebfe94d36d3dba4bffc73ef8840a8b272"

inference = json.loads((FOLDER / "inference-result.json").read_text())
rows = [row for row in inference["requestLedger"] if row["kind"] == "model"]
digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
assert len(rows) == 10 and digest == BASELINE, "Recorded paid calls must remain unchanged"

repair = json.loads((FOLDER / "batch-repair-complete.json").read_text())["repair"]
template = (BUNDLE / "scripts/content-native.bicep").read_text()
configured = re.search(r"APP_COSMOS_CONTAINER_SCHEMA:\s*'([^']+)'", template).group(1)
assert configured == "Schemas"
map_source = (REPO / "src/ContentProcessor/src/libs/pipeline/handlers/map_handler.py").read_text()
api_source = (REPO / "src/ContentProcessorAPI/app/routers/logics/schemavault.py").read_text()
assert "/Schemas/{context.data_pipeline.pipeline_status.schema_id}" in map_source
assert "{self.config.app_cps_configuration}/{self.config.app_cosmos_container_schema}" in api_source
schema_checks = []
for item in repair["schemas"]:
    name = item["target"].rsplit("/", 1)[1]
    original = REPO / "src/ContentProcessorAPI/samples/schemas" / name
    sha = hashlib.sha256(original.read_bytes()).hexdigest()
    assert sha == item["sha256"] and item["verified"]
    assert item["target"] == f"Schemas/{item['schemaId']}/{name}"
    schema_checks.append({"name": name, "sha256": sha, "matchesRecordedVerifiedCopy": True})
assert len(schema_checks) == 4

dockerfile_path = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/tokenizer-processor-r4/Dockerfile"
dockerfile = dockerfile_path.read_text()
assert "ENV TIKTOKEN_CACHE_DIR=/opt/content_tokenizer_cache" in dockerfile
assert "tiktoken.get_encoding('o200k_base')" in dockerfile
assert "assert os.environ['CONTENT_NATIVE_GUARD']=='1'" in dockerfile
assert "evaluate_confidence({}, {'message': {'content': '{}'}, 'logprobs': None})" in dockerfile
assert dockerfile.rfind("USER gsauser") > dockerfile.find("CONTENT_NATIVE_GUARD=0")
build = next(item for item in inference["newBuilds"] if item["runId"] == "chq")
assert build["status"] == "Succeeded"
assert build["images"][0]["digest"] == "sha256:8a9a254663ee525d843f8b5a7d670ff2b9facf0fdf0cd6af0ce1ef7cbc8ee39a"
outputs = json.loads((FOLDER / "batch-run-complete-recovery.json").read_text())["evidence"][
    "complete-recovery-document-outputs.json"]["police-report.pdf"]
assert any(item["step_name"] == "evaluate" and "extracted_result" in item["step_result"] for item in outputs)
asset_url = "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken"
cache_root = Path(os.environ.get("TIKTOKEN_CACHE_DIR", os.environ.get(
    "DATA_GYM_CACHE_DIR", str(Path(tempfile.gettempdir()) / "data-gym-cache"))))
cache_present = (cache_root / hashlib.sha1(asset_url.encode()).hexdigest()).is_file()

sources = [
    ("src/ContentProcessorWorkflow/src/steps/claim_processor.py", 'elif event.type == "output":',
     "Completed is assigned on graph output, without aggregating child statuses"),
    ("src/ContentProcessorWorkflow/src/steps/document_process/executor/document_process_executor.py",
     "document_results.extend([t.result() for t in tasks])",
     "Per-document errors/exceptions remain results and are forwarded downstream"),
    ("src/ContentProcessorWorkflow/src/steps/summarize/executor/summarize_executor.py",
     'if document["status"] != 302:', "Non-successful documents are explicitly skipped"),
    ("src/ContentProcessorWorkflow/src/steps/rai/executor/rai_executor.py",
     'if document["status"] != 302:', "Non-successful documents are explicitly skipped"),
    ("src/ContentProcessorWorkflow/src/repositories/model/claim_process.py",
     "COMPLETED:            All stages finished successfully.",
     "Documentation describes stages, not an explicit all-child-success guarantee")]
references = []
for relative, needle, meaning in sources:
    lines = (REPO / relative).read_text().splitlines()
    line = next(index for index, text in enumerate(lines, 1) if needle in text)
    references.append({"file": relative, "line": line, "observation": meaning})
for name in ("claim_acceptance.py", "test_claim_acceptance.py", "invoke_cloud_batch.py"):
    ast.parse((BUNDLE / "scripts/content-runtime" / name).read_text())

verification = {
    "recordedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "mode": "offline only; no cloud commands, image builds, model calls or CU calls",
    "modelRecordCount": 10, "modelRecordsSha256Before": BASELINE, "modelRecordsSha256After": digest,
    "schemaPrefix": configured, "schemaChecks": schema_checks,
    "tokenizer": {
        "dockerfileSha256": hashlib.sha256(dockerfile_path.read_bytes()).hexdigest(),
        "archivedBuildRun": "chq", "archivedBuildGuardedEvaluatorCheckPassed": True,
        "recordedLivePoliceReportEvaluationPresent": True,
        "localAssetAvailableForNewRuntimeCheck": cache_present,
        "limitation": "No local tokenizer cache was available; no download or new runtime/container test was attempted"},
    "statusContract": {
        "references": references,
        "decision": "No native status change: all-child-success intent is not explicit enough. Completed is not clean processing acceptance.",
        "driverChange": "After preserving the raw response, reject a run unless every expected submitted file is present exactly once and Completed",
        "nativeSourceChanged": False, "nativeOutputsRewritten": False},
    "regression": {"runner": "unittest", "testFile": "scripts/content-runtime/test_claim_acceptance.py",
                   "testsPassed": 11, "failures": 0, "execution": "948"},
    "compute": {"changedDuringHold": False, "lastVerifiedStopState": inference["stopState"]},
    "budget": {"hold": True, "used": 10, "currentAllowance": 12, "newAllocationApproved": False,
               "portfolioCeiling": 100, "allocationSource": "Pending redistribution within existing portfolio ceiling"}}
(FOLDER / "offline-verification.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
result_path = FOLDER / "result.json"
result = json.loads(result_path.read_text())
result["offlineVerification"] = verification
result["modelCallsOnHold"] = True
result["inferenceEvaluation"]["requestedDecision"]["allocationStatus"] = "Unallocated; awaiting redistribution within existing global100, not a portfolio ceiling increase"
result["status"] = "paused_model_budget_hold_offline_driver_acceptance_verified_native_status_unchanged"
check_rows = [row for row in result["measuredTraffic"]["callSequence"] if row["kind"] == "model"]
assert hashlib.sha256(json.dumps(check_rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == BASELINE
result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"schemaCopiesVerified": len(schema_checks), "tokenizerBuildEvidenceVerified": True,
                  "newTokenizerRuntimeCheck": False, "nativeSourceChanged": False,
                  "modelRecordsUnchanged": True, "modelCalls": len(rows), "hold": True}, indent=2))
