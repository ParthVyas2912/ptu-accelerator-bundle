"""Bounded real-app orchestration and one-session evidence export."""
import argparse
import datetime
import hashlib
import json
import os
import socket
import sys
import time

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobClient
from content_guard import redact

AI = "aif-ptuv-content-260911"
credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])


def blob(name):
    return BlobClient("https://stptuvcontent260911.blob.core.windows.net",
                      "ptu-content-configuration", "evaluation/" + name,
                      credential=credential)


def read(name, optional=False):
    try:
        return json.loads(blob(name).download_blob().readall())
    except ResourceNotFoundError:
        if optional:
            return None
        raise


def save(name, value):
    blob(name).upload_blob(json.dumps(value), overwrite=True)


def export():
    return {name: read(name, optional=True) for name in (
        "ai-preflight.json", "functional-results.json", "content-call-budget.json",
        "claim-run-complete.json", "claim-run-corrupt.json",
        "claim-run-missing-police.json", "claim-run-vin-date-mismatch.json",
        "claim-run-complete-recovery.json", "schema-name-repair.json",
        "complete-recovery-document-outputs.json")}


def repair_schema_names():
    import certifi
    import pymongo
    from azure.storage.queue import QueueClient
    from cloud_entry import mongo_connection
    import exercise_app as app
    failed = app.DATA["cases"]["complete"]["lastDetail"]["data"]["processed_documents"]
    if len(failed) != 4 or any(item["status"] != "Error" for item in failed):
        raise RuntimeError("Repair requires the four verified failed original document records")
    expected_ids = {item["process_id"] for item in failed}
    queue = QueueClient("https://stptuvcontent260911.queue.core.windows.net",
                        "content-pipeline-map-queue", credential=credential)
    messages = list(next(queue.receive_messages(
        messages_per_page=4, visibility_timeout=7200).by_page(), []))
    held = []
    for message in messages:
        payload = json.loads(message.content)
        process_id = payload.get("process_id") or payload["pipeline_status"]["process_id"]
        if process_id not in expected_ids:
            queue.update_message(message, visibility_timeout=0)
            raise RuntimeError("Unexpected queue work; released it without deletion")
        held.append({"messageId": message.id, "processId": process_id,
                     "nextVisibleUtc": str(message.next_visible_on)})
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "heldOriginalMessages": held, "sourceCollection": "ptu-content-schemas",
              "targetCollection": "Schemas", "schemas": [], "dataDeleted": False,
              "reason": "API used configurable prefix; upstream Processor hardcodes case-sensitive Schemas"}
    save("schema-name-repair.json", result)
    if {item["processId"] for item in held} != expected_ids:
        raise RuntimeError("Not all four original messages were available to defer; Processor must stay stopped")
    client = pymongo.MongoClient(mongo_connection(), tlsCAFile=certifi.where(),
                                 serverSelectionTimeoutMS=15000)
    database = client["ptu-content-db"]
    for filename, schema_id in app.DATA["schemas"].items():
        source = database["ptu-content-schemas"].find_one({"Id": schema_id})
        if not source or source["FileName"] != filename:
            raise RuntimeError("Unexpected registered schema; refusing migration")
        target = database["Schemas"].find_one({"Id": schema_id})
        if target is None:
            database["Schemas"].insert_one(source.copy())
        elif target != source:
            raise RuntimeError("Existing target schema differs; refusing overwrite")
        old_name = f"ptu-content-schemas/{schema_id}/{filename}"
        new_name = f"Schemas/{schema_id}/{filename}"
        old = BlobClient("https://stptuvcontent260911.blob.core.windows.net",
                         "ptu-content-configuration", old_name, credential=credential)
        new = BlobClient("https://stptuvcontent260911.blob.core.windows.net",
                         "ptu-content-configuration", new_name, credential=credential)
        content = old.download_blob().readall()
        if not isinstance(json.loads(content), dict):
            raise RuntimeError("Schema must remain a JSON object")
        try:
            existing = new.download_blob().readall()
        except ResourceNotFoundError:
            new.upload_blob(content, overwrite=False)
        else:
            if existing != content:
                raise RuntimeError("Existing target schema blob differs; refusing overwrite")
        if new.download_blob().readall() != content:
            raise RuntimeError("Schema copy verification failed")
        result["schemas"].append({"schemaId": schema_id, "source": old_name, "target": new_name,
                                  "sha256": hashlib.sha256(content).hexdigest(), "verified": True})
        save("schema-name-repair.json", result)
    client.close()
    result["dataCopyVerified"] = len(result["schemas"]) == 4
    save("schema-name-repair.json", result)
    return result


def preflight():
    if os.environ["CONTENT_SERVICE"] != "processor":
        raise RuntimeError("CU authorization must be verified with the Processor identity")
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "service": "processor", "clientId": os.environ["AZURE_CLIENT_ID"], "dns": {}}
    for suffix in ("cognitiveservices.azure.com", "openai.azure.com", "services.ai.azure.com"):
        host = AI + "." + suffix
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(
            host, 443, family=socket.AF_INET)})
        result["dns"][host] = addresses
        if not addresses or not all(ip.startswith("10.246.2.") for ip in addresses):
            save("ai-preflight.json", result)
            raise RuntimeError("AI hostname did not resolve entirely inside the approved PE subnet: " + host)
    sys.path.insert(0, "/app/src")
    from libs.azure_helper.content_understanding import AzureContentUnderstandingHelper
    helper = AzureContentUnderstandingHelper("https://" + AI + ".cognitiveservices.azure.com")
    start = time.perf_counter()
    analyzer = helper.get_analyzer_detail_by_id("prebuilt-layout")
    result["cuMetadata"] = {
        "status": 200, "apiVersion": "2025-11-01", "analyzerId": "prebuilt-layout",
        "elapsedMs": round((time.perf_counter() - start) * 1000, 3),
        "returnedKeys": sorted(analyzer)}
    result["passed"] = True
    save("ai-preflight.json", result)
    return result


def run_claim(case, seconds, submit, create):
    import exercise_app as app
    check = read("ai-preflight.json")
    age = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(check["utc"])
    if not check.get("passed") or age.total_seconds() > 3600:
        raise RuntimeError("Require a recent successful Processor private-DNS/CU authorization check")
    if create:
        if case not in app.DATA["cases"]:
            app.create_case(case, fixture_case="complete" if case == "complete-recovery" else None)
        else:
            raise RuntimeError("Refusing duplicate case creation")
    record = app.DATA["cases"][case]
    run = {"case": case, "claimId": record["claimId"],
           "startedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "statuses": [], "submittedThisRun": False}
    if submit:
        app.submit_existing(case)
        run["submittedThisRun"] = True
    elif not record.get("submitted"):
        raise RuntimeError("Claim is not submitted; explicit --submit is required")
    save("claim-run-" + case + ".json", run)
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        status = app.request("GET", f"/claimprocessor/claims/{record['claimId']}/status",
                             expected=(200, 302), allow_redirects=False)
        run["statuses"].append({"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                "value": status})
        ledger = read("content-call-budget.json", optional=True) or {"requests": []}
        run["modelAttemptsObserved"] = sum(item["kind"] == "model" for item in ledger["requests"])
        save("claim-run-" + case + ".json", run)
        state = status.get("status")
        if state in ("Completed", "Failed"):
            run["terminalStatus"] = state
            break
        if run["modelAttemptsObserved"] >= 12 and any(
                item.get("error") or (item.get("status") or 0) >= 400
                for item in ledger["requests"] if item["kind"] == "model"):
            run["budgetExhausted"] = True
            break
        time.sleep(15)
    else:
        run["pollingDeadlineReached"] = True
    detail = app.request("GET", f"/claimprocessor/claims/{record['claimId']}", expected=None)
    documents = detail.get("data", {}).get("processed_documents", [])
    run["documentStatuses"] = {item["file_name"]: item["status"] for item in documents}
    run["allDocumentsCompleted"] = bool(documents) and all(item["status"] == "Completed" for item in documents)
    if run.get("terminalStatus") == "Completed":
        outputs = {}
        for item in documents:
            outputs[item["file_name"]] = app.request(
                "GET", f"/contentprocessor/processed/{item['process_id']}/steps", expected=None)
        save(case + "-document-outputs.json", outputs)
    app.DATA["cases"][case]["lastDetail"] = detail
    app.DATA["cases"][case]["lastStatus"] = run["statuses"][-1]["value"] if run["statuses"] else None
    app.save()
    run["finishedUtc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save("claim-run-" + case + ".json", run)
    return run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("preflight", "run", "export", "repair"))
    parser.add_argument("--case", default="complete", choices=(
        "complete", "complete-recovery", "corrupt", "missing-police", "vin-date-mismatch"))
    parser.add_argument("--seconds", type=int, default=360)
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--create", action="store_true")
    args = parser.parse_args()
    if not 15 <= args.seconds <= 600:
        raise ValueError("Bounded polling requires 15..600 seconds")
    if args.action == "preflight":
        return {"preflight": preflight(), "evidence": export()}
    if args.action == "run":
        return {"run": run_claim(args.case, args.seconds, args.submit, args.create),
                "evidence": export()}
    if args.action == "repair":
        return {"repair": repair_schema_names(), "evidence": export()}
    return {"evidence": export()}


if __name__ == "__main__":
    try:
        output = main()
    except Exception as exc:
        output = {"error": {"type": type(exc).__name__, "message": redact(exc)},
                  "evidence": export()}
        print("CONTENT_BATCH_JSON=" + json.dumps(output), flush=True)
        sys.exit(1)
    print("CONTENT_BATCH_JSON=" + json.dumps(output), flush=True)
