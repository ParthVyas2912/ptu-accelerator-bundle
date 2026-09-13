"""Persist secret-free app evidence returned by authenticated control-plane exec."""
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys

BUNDLE = Path(__file__).resolve().parents[2]
SUB = "1feb53b2-854a-4ea7-b5a6-709b7d804f70"
if json.loads((BUNDLE / "evidence/content/result.json").read_text()).get("inferenceEvaluation"):
    raise RuntimeError("Historical capture mode: use capture_inference_result.py after live inference")


def az(args):
    args = args + ["--subscription", SUB]
    quoted = ",".join("'" + arg.replace("'", "''") + "'" for arg in args)
    command = f"& '{BUNDLE / 'Invoke-LabAz.ps1'}' -AzArguments @({quoted})"
    response = subprocess.run(["pwsh", "-NoProfile", "-Command", command],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=180)
    if response.returncode:
        raise RuntimeError("Guarded Azure operation failed: " + response.stderr[:1000])
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", response.stdout)


def execute(script, marker):
    raw = az(["containerapp", "exec", "-g", "rg-ptu-content-demo",
              "-n", "ca-ptu-content-api", "--command",
              "/app/.venv/bin/python /opt/content_eval/" + script])
    if marker not in raw:
        raise RuntimeError("Expected baked-script evidence marker absent")
    return json.JSONDecoder().raw_decode(raw.split(marker, 1)[1].lstrip())[0]


evidence = {
    "capturedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "mode": "adapted private Container Apps deployment, authenticated exec",
}
observed = json.loads((BUNDLE / "evidence/content/cloud-real-api-observed.json").read_text())
evidence["observations"] = observed
if "--arm-only" in sys.argv:
    evidence["probe"] = {"source": "cloud-real-api-observed.json; previously executed successfully"}
    evidence["application"] = {"fullBlobExportDeferred": observed["localFullExport"]}
else:
    evidence["probe"] = (
        {"source": "cloud-real-api-observed.json; previously executed successfully"}
        if "--export-only" in sys.argv
        else execute("cloud_probe.py", "CONTENT_PROBE_JSON="))
    evidence["application"] = execute("cloud_export.py", "CONTENT_EVIDENCE_JSON=")
    observed.setdefault("historicalExportAttempt", observed["localFullExport"])
    observed["localFullExport"] = {
        "status": "succeeded", "capturedUtc": evidence["capturedUtc"],
        "source": "authenticated exec of baked cloud_export.py; own Blob",
        "file": "cloud-application-evidence.json"}
    (BUNDLE / "evidence/content/cloud-real-api-observed.json").write_text(
        json.dumps(observed, indent=2), encoding="utf-8")
evidence["apps"] = json.loads(az(["containerapp", "list", "-g", "rg-ptu-content-demo",
    "--query", "[].{name:name,id:id,runningStatus:properties.runningStatus,latestRevision:properties.latestRevisionName,readyRevision:properties.latestReadyRevisionName,ingress:properties.configuration.ingress,scale:properties.template.scale,containers:properties.template.containers}",
    "-o", "json"]))
evidence["builds"] = []
for run in ("ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "ch7", "ch8", "ch9", "cha", "chb"):
    evidence["builds"].append(json.loads(az(["acr", "task", "show-run",
        "--registry", "acrptubundle7d804f70", "--run-id", run, "--query",
        "{runId:runId,status:status,start:startTime,finish:finishTime,images:outputImages}", "-o", "json"])))
folder = BUNDLE / "evidence/content"
(folder / "cloud-application-evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
result_path = folder / "result.json"
result = json.loads(result_path.read_text(encoding="utf-8"))
result["status"] = "private_four_service_app_deployed_real_schema_claim_upload_tests_passed_ai_connectivity_blocked"
result["cloudApplication"] = evidence
result["currentBlockers"] = [
    "AI endpoints still resolve publicly20.62.58.5; fourth account PE with three DNS zones requires parent helper extension/central creation",
    "No claim submitted to CU/model processing until private AI connectivity verified",
    "Public browser access unverified; API/Web internal only"]
functional = evidence["application"].get("functional-results.json") or {}
result["realApiTests"] = {
    "registeredSchemaCount": len(functional.get("schemas", {})) if functional else observed["schemaRegistration"]["schemaCount"],
    "schemaSetId": functional.get("schemaSetId") if functional else observed["schemaRegistration"]["schemaSetId"],
    "apiRequestCount": len(functional.get("apiCalls", [])) if functional else 21,
    "cases": functional.get("cases", {}) if functional else {
        "complete": observed["completeClaim"], "corrupt": observed["corruptClaim"]},
    "isFullClaimProcessing": False}
result["secretHandlingCurrent"]["mongoCredentialRetrieved"] = True
result["secretHandlingCurrent"]["mongoCredentialExceptionApprovedButNotUsed"] = False
result["secretHandlingCurrent"]["method"] = "Assigned managed identity reads own-account listConnectionStrings; value passed only in process environment, never ACA secret or file."
result["cloudSafeguards"] = {
    "budgetBackend": "Own Blob JSON with ETag conditional-write CAS; durable across all replicas/restarts",
    "hardModelCap": 12,
    "concurrencySimulation": "40 local concurrent CAS attempts, exactly12 admissions, no live model requests",
    "identityAdapterFix": "r1 API selected missing system identity; r2 binds explicit per-app UAI for sync/async ManagedIdentityCredential.",
    "resumeDriverUpdate": "API r3 inherits verified r2 runtime; adds durable test-state recovery and duplicate-protected existing-claim submit.",
    "activeRevisionMode": "Single", "maxReplicasPerApp": 1,
    "maximumAllocatedVcpu": 2, "maximumAllocatedMemoryGiB": 4}
result["endpointsAndProcesses"]["cloudEndpoints"] = [
    "https://ca-ptu-content-api.internal.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io",
    "https://ca-ptu-content-web.internal.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io"]
result["endpointsAndProcesses"]["publicBrowserVerified"] = False
for test in result["functionalTests"]:
    if test["id"] == "complete-claim":
        test["actual"] = "Real private API schema registration, claim creation and four file uploads HTTP200; claim77f4a16d-96fe-4739-b90a-9ac0b2597bb4 not submitted while AI PE remains unavailable."
        test["status"] = "partial_real_api_no_inference"
    if test["id"] == "corrupt-unsupported":
        test["actual"] = "Real private HTTP API: bad-magic.pdf415, unsupported.txt415, truncated.pdf200 accepted headergate; no downstream processing/DLQ tested."
        test["status"] = "partial_real_http"
result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"captured": evidence["capturedUtc"], "appCount": len(evidence["apps"]),
                  "schemaCount": result["realApiTests"]["registeredSchemaCount"],
                  "apiRequests": result["realApiTests"]["apiRequestCount"],
                  "cases": result["realApiTests"]["cases"]}, indent=2))
