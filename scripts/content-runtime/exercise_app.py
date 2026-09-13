"""Exercise the accelerator's real API; no service stubs or direct model calls."""
import argparse
import datetime
import json
import mimetypes
import os
from pathlib import Path
import time
import requests

BUNDLE = Path(__file__).resolve().parents[2]
REPO = Path.home() / "OneDrive - Microsoft/Desktop/repo/content-processing-solution-accelerator"
EVIDENCE = Path(os.environ.get("CONTENT_EVIDENCE_ROOT", str(BUNDLE / "evidence/content")))
EVIDENCE.mkdir(parents=True, exist_ok=True)
STATE = EVIDENCE / "native-functional.json"
BASE = os.environ.get("CONTENT_API_BASE_URL", "http://127.0.0.1:8113")
DATA = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {
    "syntheticOnly": True, "api": BASE, "apiCalls": [], "schemas": {}, "cases": {}}
if not STATE.exists() and os.environ.get("CONTENT_BUDGET_BACKEND") == "blob":
    from azure.identity import ManagedIdentityCredential
    from azure.storage.blob import BlobClient
    from azure.core.exceptions import ResourceNotFoundError
    blob = BlobClient("https://stptuvcontent260911.blob.core.windows.net",
                      "ptu-content-configuration", "evaluation/functional-results.json",
                      credential=ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"]))
    try:
        DATA = json.loads(blob.download_blob().readall())
    except ResourceNotFoundError:
        pass


def save():
    STATE.write_text(json.dumps(DATA, indent=2, ensure_ascii=False), encoding="utf-8")
    if os.environ.get("CONTENT_BUDGET_BACKEND") == "blob":
        from azure.identity import ManagedIdentityCredential
        from azure.storage.blob import BlobClient
        client = BlobClient("https://stptuvcontent260911.blob.core.windows.net",
                            "ptu-content-configuration", "evaluation/functional-results.json",
                            credential=ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"]))
        client.upload_blob(json.dumps(DATA), overwrite=True)


def request(method, path, expected=200, **kwargs):
    start = time.perf_counter()
    response = requests.request(method, BASE + path, timeout=90, **kwargs)
    try:
        result = response.json()
    except ValueError:
        result = response.text[:1500]
    DATA["apiCalls"].append({
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "method": method, "path": path, "status": response.status_code,
        "elapsedMs": round((time.perf_counter()-start)*1000, 3), "result": result})
    save()
    print(method, path, response.status_code, flush=True)
    if expected is not None and response.status_code not in (
            expected if isinstance(expected, tuple) else (expected,)):
        raise RuntimeError(f"Unexpected HTTP {response.status_code}: {str(result)[:1000]}")
    return result


def register():
    root = Path(os.environ["CONTENT_FIXTURE_ROOT"]) / "schemas" if os.environ.get(
        "CONTENT_FIXTURE_ROOT") else REPO / "src/ContentProcessorAPI/samples/schemas"
    descriptors = json.loads((root / "schema_info.json").read_text())
    current = request("GET", "/schemavault/")
    for schema in descriptors["schemas"]:
        existing = next((x for x in current if x["ClassName"] == schema["ClassName"]), None)
        if existing:
            result = existing
        else:
            with (root / schema["File"]).open("rb") as file:
                result = request("POST", "/schemavault/", expected=(200, 201),
                                 data={"data": json.dumps({k: schema[k] for k in (
                                     "ClassName", "Description")})},
                                 files={"file": (schema["File"], file, "application/json")})
        DATA["schemas"][schema["File"]] = result["Id"]
        save()
    sets = request("GET", "/schemasetvault/")
    target = next((x for x in sets if x["Name"] == "Auto Claim"), None)
    if target is None:
        target = request("POST", "/schemasetvault/", expected=(200, 201),
                         json=descriptors["schemaset"])
    DATA["schemaSetId"] = target["Id"]
    members = request("GET", f"/schemasetvault/{target['Id']}/schemas")
    member_ids = {x["Id"] for x in members}
    for schema_id in DATA["schemas"].values():
        if schema_id not in member_ids:
            request("POST", f"/schemasetvault/{target['Id']}/schemas",
                    json={"SchemaId": schema_id})
    save()


def create_case(case, submit=False, fixture_case=None, scoped_metadata=False):
    if case in DATA["cases"]:
        raise RuntimeError("Case already exists; refusing duplicate creation/submission")
    claim = request("PUT", "/claimprocessor/claims", expected=(200, 201), json={
        "schema_collection_id": DATA["schemaSetId"],
        "metadata_id": "PTU-CONTENT-" + case})
    claim_id = claim["claim_id"]
    DATA["cases"][case] = {"claimId": claim_id, "submitted": False}
    save()
    mapping = {
        "claim-form.pdf": "autoclaim.json", "police-report.pdf": "policereport.json",
        "repair-estimate.pdf": "repairestimate.json", "damage-diagram.png": "damagedcarimage.json",
        "bad-magic.pdf": "autoclaim.json", "unsupported.txt": "autoclaim.json",
        "truncated.pdf": "autoclaim.json"}
    fixture = Path(os.environ["CONTENT_FIXTURE_ROOT"]) / "content" if os.environ.get(
        "CONTENT_FIXTURE_ROOT") else BUNDLE / "test-data/content"
    for path in sorted((fixture / (fixture_case or case)).iterdir()):
        if not path.is_file():
            continue
        schema_file = mapping[path.name]
        with path.open("rb") as file:
            result = request("POST", f"/claimprocessor/claims/{claim_id}/files",
                expected=None if case == "corrupt" else (200, 201),
                data={"data": json.dumps({"Claim_Id": claim_id,
                      "Metadata_Id": claim_id if scoped_metadata else "PTU-CONTENT-" + case,
                      "Schema_Id": DATA["schemas"][schema_file]})},
                files={"file": (path.name, file, mimetypes.guess_type(path.name)[0]
                                 or "application/octet-stream")})
    if submit:
        request("POST", "/claimprocessor/claims", expected=(200, 201, 202),
                json={"claim_process_id": claim_id})
        DATA["cases"][case]["submitted"] = True
    save()
    print("Case", case, "claimId", claim_id, "submitted", submit)


def poll(case):
    claim_id = DATA["cases"][case]["claimId"]
    result = request("GET", f"/claimprocessor/claims/{claim_id}/status")
    DATA["cases"][case]["lastStatus"] = result
    detail = request("GET", f"/claimprocessor/claims/{claim_id}", expected=None)
    DATA["cases"][case]["lastDetail"] = detail
    save()
    print(json.dumps(result, indent=2))


def submit_existing(case):
    record = DATA["cases"][case]
    if record.get("submitted"):
        raise RuntimeError("Claim already submitted; refusing duplicate queue/model work")
    # Store intent first. An uncertain HTTP result requires inspection, not
    # automatic resubmission that might duplicate the paid workflow.
    if record.get("submissionAttempted"):
        raise RuntimeError("Previous submit intent exists; inspect actual status before retry")
    record["submissionAttempted"] = True
    save()
    request("POST", "/claimprocessor/claims", expected=(200, 201, 202),
            json={"claim_process_id": record["claimId"]})
    record["submitted"] = True
    save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("register", "create", "poll", "health", "submit"))
    parser.add_argument("--case", choices=("complete", "missing-police",
                       "vin-date-mismatch", "visual-table", "corrupt"), default="complete")
    parser.add_argument("--submit", action="store_true")
    args = parser.parse_args()
    if args.action == "register":
        register()
    elif args.action == "create":
        create_case(args.case, args.submit)
    elif args.action == "poll":
        poll(args.case)
    elif args.action == "submit":
        submit_existing(args.case)
    else:
        request("GET", "/health")
        request("GET", "/startup")
