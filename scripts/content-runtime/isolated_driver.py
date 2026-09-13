"""One real native missing-police claim, six model attempts maximum; raw evidence retained."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

from azure.core.exceptions import ResourceNotFoundError
import cloud_budget
import exercise_app as app
import isolated_scope as scope
from content_guard import redact

BASELINE = "4d37d6806585a217d851e77dbd4a7c816ceea605df79c5212abee9c7db1bd543"


def model_fingerprint(ledger):
    models = [row for row in ledger["requests"] if row["kind"] == "model"]
    return len(models), scope.sha(json.dumps(models, sort_keys=True, separators=(",", ":")).encode())


def prepare():
    if model_fingerprint(cloud_budget.snapshot()) != (11, BASELINE):
        raise RuntimeError("Preserved eleven-reservation baseline differs; no new claim")
    try:
        scope.read_control()
    except ResourceNotFoundError:
        pass
    else:
        raise RuntimeError("Run control already exists; do not create/submit another claim")
    app.create_case(scope.RUN, fixture_case="missing-police", scoped_metadata=True)
    claim_id = app.DATA["cases"][scope.RUN]["claimId"]
    manifest = json.loads(scope.blob(f"{claim_id}/manifest.json", "ptu-content-batches").download_blob().readall())
    mapping = {"claim-form.pdf": "autoclaim.json", "repair-estimate.pdf": "repairestimate.json",
               "damage-diagram.png": "damagedcarimage.json"}
    if {item["file_name"] for item in manifest["items"]} != set(mapping):
        raise RuntimeError("Native manifest does not contain exactly the three approved files")
    expected = {}
    root = Path(os.environ["CONTENT_FIXTURE_ROOT"]) / "content" / "missing-police"
    for item in manifest["items"]:
        name = item["file_name"]
        if item["metadata_id"] != claim_id or item["schema_id"] != app.DATA["schemas"][mapping[name]]:
            raise RuntimeError("Native uploaded metadata/schema differs")
        source = (root / name).read_bytes()
        cloud = scope.blob(f"{claim_id}/{name}", "ptu-content-batches").download_blob().readall()
        if cloud != source:
            raise RuntimeError("Native upload bytes differ")
        expected[name] = {"sha256": scope.sha(source), "schemaId": item["schema_id"]}
    state = {"run": scope.RUN, "claimId": claim_id, "approvedTotal": 17, "mode": "disarmed",
             "baselineSha256": BASELINE, "expected": expected, "documents": {},
             "preparedAt": time.time(), "expectedGapRule": "REQ-PR-THIRD-PARTY-006", "events": []}
    scope.blob().upload_blob(json.dumps(state), overwrite=False)
    return state


def export():
    state = scope.read_control()
    result = {"control": state, "ledger": cloud_budget.snapshot(), "documents": {}, "nativeAgents": {}}
    claim_id = state["claimId"]
    result["claimDetail"] = app.request("GET", f"/claimprocessor/claims/{claim_id}", expected=None)
    for name, item in state["documents"].items():
        outputs = {}
        for filename in ("gpt_output.json", "evaluate_output.json", "save_output.json", "step_outputs.json", "process-status.json"):
            try:
                raw = scope.blob(f"{item['processId']}/{filename}", "ptu-content-processes").download_blob().readall()
            except ResourceNotFoundError:
                outputs[filename] = {"missing": True}
            else:
                outputs[filename] = {"sha256": scope.sha(raw), "value": json.loads(raw)}
        result["documents"][name] = {"processId": item["processId"], "artifacts": outputs}
    for stage in ("rai", "summary", "gaps", "processor-logs", "workflow-logs"):
        try:
            result["nativeAgents"][stage] = json.loads(scope.blob(f"evaluation/{scope.RUN}-{stage}.json").download_blob().readall())
        except ResourceNotFoundError:
            result["nativeAgents"][stage] = {"missing": True}
    scope.blob(f"evaluation/{scope.RUN}-result.json").upload_blob(json.dumps(result), overwrite=True)
    return result


def run():
    state = scope.read_control()
    if state["mode"] != "disarmed" or state.get("armedAt") or state["documents"]:
        raise RuntimeError("No repeat arming, claim replay or prior documents permitted")
    if model_fingerprint(cloud_budget.snapshot()) != (11, BASELINE):
        raise RuntimeError("Baseline differs or six-attempt headroom unavailable")
    app.submit_existing(scope.RUN)
    def arm(value):
        value.update(mode="armed", armedAt=time.time(), deadline=time.time() + 600)
    scope.change_control(arm)
    try:
        deadline = time.monotonic() + 570
        while time.monotonic() < deadline:
            current = scope.read_control()
            if current["mode"] != "armed":
                break
            detail = app.request("GET", f"/claimprocessor/claims/{state['claimId']}", expected=None)
            data = detail.get("data", {})
            if data.get("status") in ("Completed", "Failed") or any(
                    item.get("status") == "Error" for item in data.get("processed_documents", [])):
                break
            time.sleep(10)
    finally:
        scope.change_control(lambda value: value.update(mode="disarmed", disarmedAt=time.time()))
    time.sleep(5)
    return export()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "run", "export", "disarm"))
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            output = prepare()
        elif args.action == "run":
            output = run()
        elif args.action == "disarm":
            scope.change_control(lambda value: value.update(mode="disarmed", disarmedAt=time.time()))
            output = export()
        else:
            output = export()
    except Exception as exc:
        print("CONTENT_ISOLATED_JSON=" + json.dumps({"error": {"type": type(exc).__name__, "message": redact(exc)}}), flush=True)
        raise
    print("CONTENT_ISOLATED_JSON=" + json.dumps(output), flush=True)
