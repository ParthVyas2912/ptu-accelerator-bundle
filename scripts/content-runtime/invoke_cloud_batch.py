"""One authenticated exec, bounded timeout, secret-free structured local capture."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=("preflight", "run", "export", "repair", "negative", "zero", "zero-export"))
parser.add_argument("--case", default="complete",
                    choices=("complete", "complete-recovery", "corrupt", "missing-police", "vin-date-mismatch"))
parser.add_argument("--seconds", type=int, default=360)
parser.add_argument("--submit", action="store_true")
parser.add_argument("--create", action="store_true")
args = parser.parse_args()
if not 15 <= args.seconds <= 600:
    raise ValueError("Polling bound must be 15..600 seconds")
bundle = Path(__file__).resolve().parents[2]
service = "processor" if args.action in ("preflight", "zero", "zero-export") else "api"
command = f"/app/.venv/bin/python /opt/content_eval/cloud_batch.py {args.action} --case {args.case} --seconds {args.seconds}"
if args.action == "negative":
    command = "/app/.venv/bin/python /opt/content_eval/negative_file.py"
if args.action == "zero":
    command = "/app/.venv/bin/python /opt/content_eval/zero_model_recovery.py run"
if args.action == "zero-export":
    command = "/app/.venv/bin/python /opt/content_eval/cloud_export.py"
if args.submit:
    command += " --submit"
if args.create:
    command += " --create"
az_args = ["containerapp", "exec", "-g", "rg-ptu-content-demo",
           "-n", "ca-ptu-content-" + service, "--subscription",
           "1feb53b2-854a-4ea7-b5a6-709b7d804f70", "--command", command]
quoted = ",".join("'" + value.replace("'", "''") + "'" for value in az_args)
response = subprocess.run(["pwsh", "-NoProfile", "-Command",
    f"& '{bundle / 'Invoke-LabAz.ps1'}' -AzArguments @({quoted})"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=args.seconds + 180)
raw = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", response.stdout)
marker = "CONTENT_ZERO_JSON=" if args.action == "zero" else "CONTENT_BATCH_JSON="
if args.action == "zero-export":
    marker = "CONTENT_EVIDENCE_JSON="
if marker not in raw:
    from content_guard import redact
    diagnostic = redact(raw[-12000:] + "\n" + response.stderr[-1500:])
    diagnostic = re.sub(r"(?i)([?&](?:sig|access_token|token)=)[^&\s\"']+", r"\1[REDACTED]", diagnostic)
    (bundle / "evidence/content" / f"batch-{args.action}-exec-failure.json").write_text(
        json.dumps({"exitCode": response.returncode, "diagnostic": diagnostic}, indent=2),
        encoding="utf-8")
    raise RuntimeError("Exec returned no evidence marker: " + diagnostic)
data = json.JSONDecoder().raw_decode(raw.split(marker, 1)[1].lstrip())[0]
data["localCaptureUtc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
data["controlPlaneExitCode"] = response.returncode
folder = bundle / "evidence/content"
path = folder / ("batch-" + args.action + "-" + args.case + ".json")
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
archive = folder / (path.stem + "-" + stamp + ".json")
archive.write_text(json.dumps(data, indent=2), encoding="utf-8")
path.write_text(json.dumps(data, indent=2), encoding="utf-8")
rows = (data.get("evidence", {}).get("content-call-budget.json") or {}).get("requests", [])
if args.action == "zero-export":
    models = [row for row in data["content-call-budget.json"]["requests"] if row["kind"] == "model"]
    print(json.dumps({"file": str(path), "modelCount": len(models),
                      "modelSha256": hashlib.sha256(json.dumps(models, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                      "modelRows": [{"id": row["id"], "started": row["started"], "service": row["service"],
                                     "status": row.get("status"), "error": row.get("error")}
                                    for row in models]}, indent=2))
    raise SystemExit(response.returncode)
if args.action == "zero":
    print(json.dumps({"file": str(path), "claimId": data.get("claimId"),
                      "workerStarted": data.get("workerStarted"),
                      "allFourDocumentsCompleted": data.get("allFourDocumentsCompleted"),
                      "inferenceLedgerUnchanged": data.get("entireInferenceLedgerUnchanged"),
                      "failure": data.get("failure"),
                      "documentStatuses": {item["fileName"]: item.get("databaseRecord", {}).get("status")
                                           for item in data.get("after", [])}}, indent=2))
    if response.returncode or data.get("failure") or not data.get("allFourDocumentsCompleted"):
        raise SystemExit(1)
    raise SystemExit(0)
print(json.dumps({"file": str(path), "preflight": data.get("preflight"),
                  "run": data.get("run"), "repair": data.get("repair"), "error": data.get("error"),
                  "negativePassed": (data.get("negative") or {}).get("passed"),
                  "modelAttempts": sum(row["kind"] == "model" for row in rows),
                  "cuAnalyses": sum(row["kind"] == "cu-analyze" for row in rows)}, indent=2))
if response.returncode or data.get("error"):
    raise SystemExit(1)
if args.action == "run":
    from claim_acceptance import assert_clean_claim
    fixture_case = "complete" if args.case == "complete-recovery" else args.case
    expected = sorted(path.name for path in (bundle / "test-data/content" / fixture_case).iterdir()
                      if path.is_file())
    functional = data["evidence"]["functional-results.json"]
    assert_clean_claim(functional["cases"][args.case]["lastDetail"], expected)
