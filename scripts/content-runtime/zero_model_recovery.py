"""Claim-scoped native Evaluate/Save recovery. No synthesis, tail invocation or DB rewrites."""
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

import certifi
import pymongo
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobClient
from azure.storage.queue import QueueClient
from cloud_entry import mongo_connection
from content_guard import redact, reserve

SCOPE = json.loads((Path(__file__).parent / "zero_recovery_scope.json").read_text())
CLAIM = SCOPE["claimId"]
HOST = "https://stptuvcontent260911.blob.core.windows.net"
credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])


def read_blob(container, name):
    return BlobClient(HOST, container, name, credential=credential).download_blob().readall()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def assert_disarmed():
    import httpx
    import requests
    if os.environ.get("CONTENT_INFERENCE_DISARMED") != "1":
        raise RuntimeError("Recovery requires hard inference disarm")
    if os.environ.get("CONTENT_NATIVE_GUARD") != "1":
        raise RuntimeError("Recovery requires the installed request guard")
    if any(method.__module__ != "content_guard" for method in (
            httpx.Client._send_single_request, httpx.AsyncClient._send_single_request,
            requests.Session.send)):
        raise RuntimeError("Required transport-level request guards are not installed")
    for url in (
        "https://aif-ptuv-content-260911.openai.azure.com/openai/deployments/gpt-5.1/chat/completions",
        "https://aif-ptuv-content-260911.cognitiveservices.azure.com/contentunderstanding/analyzers/prebuilt-layout:analyzeBinary"):
        try:
            reserve("POST", url, b'{"model":"gpt-5.1"}')
        except RuntimeError as exc:
            if "hard-disarmed" not in str(exc):
                raise
        else:
            raise RuntimeError("Inference disarm self-test failed")


def native_worker():
    assert_disarmed()
    sys.path.insert(0, "/app/src")
    from main import Application
    import asyncio
    app = Application()
    app.application_context.configuration.app_process_steps = ["evaluate", "save"]
    assert app.application_context.configuration.app_cosmos_container_schema == "Schemas"
    assert app.application_context.configuration.app_cps_processes == "ptu-content-processes"
    asyncio.run(app.run())


def process_record(database, process_id):
    record = database["ptu-content-processes"].find_one({"process_id": process_id})
    if record is None:
        raise RuntimeError("Approved document record is missing: " + process_id)
    return record


def queue_inventory():
    result = {}
    allowed = {item["processId"] for item in SCOPE["documents"]}
    for stage in ("evaluate", "save"):
        queue = QueueClient("https://stptuvcontent260911.queue.core.windows.net",
                            "content-pipeline-" + stage + "-queue", credential=credential)
        count = queue.get_queue_properties().approximate_message_count
        messages = list(queue.peek_messages(max_messages=32))
        entries = []
        for message in messages:
            text = message.content
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = json.loads(base64.b64decode(text, validate=True))
            pid = payload.get("process_id")
            if pid not in allowed:
                raise RuntimeError("Unrelated message in native recovery queue; no consumer will start")
            entries.append({"messageId": message.id, "processId": pid,
                            "dequeueCount": message.dequeue_count,
                            "payloadSha256": sha(text.encode())})
        result[stage] = {"approximateCount": count, "visibleMessages": entries}
        if count != len(messages) or count > 32:
            raise RuntimeError("Hidden or incomplete queue inventory; cannot safely select native recovery")
    return result


def artifacts(document):
    pid, name = document["processId"], document["fileName"]
    claim_bytes = read_blob("ptu-content-batches", f"{CLAIM}/{name}")
    process_bytes = read_blob("ptu-content-processes", f"{pid}/{name}")
    if sha(claim_bytes) != document["inputSha256"] or process_bytes != claim_bytes:
        raise RuntimeError("Input bytes do not match the approved claim and fixture: " + name)
    mapped_bytes = read_blob("ptu-content-processes", f"{pid}/gpt_output.json")
    mapped = json.loads(mapped_bytes)
    parsed = mapped["choices"][0]["message"]["parsed"]
    if not isinstance(parsed, dict):
        raise RuntimeError("Native mapping is not a parsed JSON object: " + name)
    result = {"processId": pid, "fileName": name, "inputSha256": sha(process_bytes),
              "mappingSha256": sha(mapped_bytes), "mappedFields": parsed,
              "returnedMappingUsage": mapped.get("usage")}
    try:
        evaluated_bytes = read_blob("ptu-content-processes", f"{pid}/evaluate_output.json")
    except ResourceNotFoundError:
        result["evaluatedFields"] = None
    else:
        result["evaluationSha256"] = sha(evaluated_bytes)
        result["evaluatedFields"] = json.loads(evaluated_bytes)
    return result


def execute():
    assert_disarmed()
    budget_before = read_blob("ptu-content-configuration", "evaluation/content-call-budget.json")
    ledger = json.loads(budget_before)
    model_rows = [row for row in ledger["requests"] if row["kind"] == "model"]
    model_hash = sha(json.dumps(model_rows, sort_keys=True, separators=(",", ":")).encode())
    if len(model_rows) != 10 or model_hash != SCOPE["modelRecordSha256"]:
        raise RuntimeError("Ten original model response records must be unchanged")
    connection = mongo_connection()
    client = pymongo.MongoClient(connection, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=15000)
    database = client["ptu-content-db"]
    claim_before = database["claimprocesses"].find_one({"$or": [{"id": CLAIM}, {"_id": CLAIM}]})
    if claim_before is None:
        raise RuntimeError("Approved claim is missing")
    actual_ids = {item["process_id"] for item in claim_before["processed_documents"]}
    if actual_ids != {item["processId"] for item in SCOPE["documents"]}:
        raise RuntimeError("Claim/document scope differs from the approved captured record")
    result = {"claimId": CLAIM, "startedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "inferenceHardDisarmed": True, "nativeStages": ["evaluate", "save"],
              "modelRecordsBefore": len(model_rows), "modelRecordSha256Before": model_hash,
              "workerStarted": False, "logs": []}
    worker = None
    try:
        result["before"] = [
            dict(artifacts(item), databaseRecord=process_record(database, item["processId"]))
            for item in SCOPE["documents"]]
        result["queueInventoryBefore"] = queue_inventory()
        initial_records = {item["processId"]: item["databaseRecord"] for item in result["before"]}
        pending = {pid for pid, item in initial_records.items() if item.get("status") != "Completed"}
        queued = {message["processId"] for stage in result["queueInventoryBefore"].values()
                  for message in stage["visibleMessages"]}
        if not pending.issubset(queued):
            raise RuntimeError("Incomplete documents have no retry-eligible Evaluate/Save message; no redrive performed")
        if pending:
            env = dict(os.environ, APP_COSMOS_CONNSTR=connection)
            worker = subprocess.Popen(
                [sys.executable, __file__, "worker"], cwd="/app", env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                errors="replace", start_new_session=True)
            result["workerStarted"] = True
            result["ownedWorkerProcessGroup"] = worker.pid
            def capture():
                for line in worker.stdout:
                    result["logs"].append(redact(line.rstrip()))
                    if len(result["logs"]) > 160:
                        result["logs"].pop(0)
            reader = threading.Thread(target=capture, daemon=True)
            reader.start()
            deadline = time.monotonic() + 180
            while time.monotonic() < deadline:
                current = {pid: process_record(database, pid) for pid in actual_ids}
                if all(item.get("status") == "Completed" for item in current.values()):
                    break
                if any(item.get("status") == "Error" and item != initial_records[pid]
                       for pid, item in current.items()):
                    result["newNativeFailureObserved"] = True
                    break
                if worker.poll() is not None:
                    raise RuntimeError("Native stage host exited unexpectedly")
                time.sleep(3)
            else:
                result["boundedDeadlineReached"] = True
        else:
            result["alreadyCompletedBeforeRecovery"] = True
    except Exception as exc:
        result["failure"] = {"type": type(exc).__name__, "message": redact(exc)}
    finally:
        if worker is not None:
            try:
                os.killpg(worker.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                worker.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(worker.pid, signal.SIGKILL)
                worker.wait(timeout=10)
            reader.join(timeout=5)
        result["after"] = []
        for item in SCOPE["documents"]:
            try:
                observed = dict(artifacts(item), databaseRecord=process_record(database, item["processId"]))
            except Exception as exc:
                observed = {"processId": item["processId"], "fileName": item["fileName"],
                            "inspectionFailure": {"type": type(exc).__name__, "message": redact(exc)}}
                result.setdefault("failure", {"type": "InspectionFailure", "message": "Some document artifacts/statuses could not be read; see per-document failures"})
            result["after"].append(observed)
        result["allFourDocumentsCompleted"] = all(
            item.get("databaseRecord", {}).get("status") == "Completed" for item in result["after"])
        budget_after = read_blob("ptu-content-configuration", "evaluation/content-call-budget.json")
        result["entireInferenceLedgerUnchanged"] = budget_after == budget_before
        result["modelRecordSha256After"] = sha(json.dumps(
            [row for row in json.loads(budget_after)["requests"] if row["kind"] == "model"],
            sort_keys=True, separators=(",", ":")).encode())
        result["claimAggregateUnchanged"] = database["claimprocesses"].find_one(
            {"$or": [{"id": CLAIM}, {"_id": CLAIM}]}) == claim_before
        result["mappingArtifactsUnchanged"] = not result.get("before") or all(
            before.get("mappingSha256") == after.get("mappingSha256")
            for before, after in zip(result["before"], result["after"]))
        result["finishedUtc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        client.close()
        if not result["entireInferenceLedgerUnchanged"] or not result["mappingArtifactsUnchanged"]:
            raise RuntimeError("Recovery preservation invariant failed")
        BlobClient(HOST, "ptu-content-configuration",
                   "evaluation/zero-model-recovery.json", credential=credential).upload_blob(
                       json.dumps(result, default=str), overwrite=True)
    return result


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "idle"
    if mode == "idle":
        assert_disarmed()
        while True:
            time.sleep(300)
    elif mode == "worker":
        native_worker()
    elif mode == "run":
        output = execute()
        print("CONTENT_ZERO_JSON=" + json.dumps(output, default=str), flush=True)
        if output.get("failure") or not output["allFourDocumentsCompleted"]:
            sys.exit(1)
    else:
        raise ValueError("Unknown recovery mode")
