"""Record completed r3 publication/export and the observed cooldown stop."""
import datetime
import json
from pathlib import Path
import statistics
import subprocess

bundle = Path(__file__).resolve().parents[2]
folder = bundle / "evidence/content"
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
snapshot_path = folder / "cloud-application-evidence.json"
snapshot = json.loads(snapshot_path.read_text())
functional = snapshot["application"]["functional-results.json"]
assert len(functional["apiCalls"]) == 21
assert not any(case["submitted"] for case in functional["cases"].values())
assert snapshot["application"]["content-call-budget.json"] is None
args = ["containerapp", "list", "-g", "rg-ptu-content-demo", "--subscription",
        "1feb53b2-854a-4ea7-b5a6-709b7d804f70", "--query",
        "[].{name:name,id:id,runningStatus:properties.runningStatus,latestRevision:properties.latestRevisionName,readyRevision:properties.latestReadyRevisionName,ingress:properties.configuration.ingress,scale:properties.template.scale,containers:properties.template.containers}",
        "-o", "json"]
quoted = ",".join("'" + arg.replace("'", "''") + "'" for arg in args)
command = f"& '{bundle / 'Invoke-LabAz.ps1'}' -AzArguments @({quoted})"
response = subprocess.run(["pwsh", "-NoProfile", "-Command", command],
                          capture_output=True, text=True, timeout=120)
if response.returncode:
    raise RuntimeError("Guarded post-pause ARM capture failed")
snapshot["appsAtExport"] = snapshot["apps"]
snapshot["apps"] = json.loads(response.stdout)
snapshot["appsCapturedAfterPauseUtc"] = now
snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
ms = [item["elapsedMs"] for item in functional["apiCalls"]]
update = {
    "recordedUtc": now,
    "image": "acrptubundle7d804f70.azurecr.io/content/eval-api:659eaa1-r3",
    "build": next(run for run in snapshot["builds"] if run["runId"] == "chb"),
    "sourceContextKiB": 3.184, "localBuildsOrInstallsStarted": False,
    "cloudExecExportSucceeded": True, "apiRequestCount": len(ms),
    "apiElapsedMs": {"min": min(ms), "median": statistics.median(ms), "max": max(ms)},
    "statusCounts": {"200": 19, "415": 2},
    "modelAttempts": 0, "cuAnalyses": 0, "budgetBlobPresent": False,
    "interpretation": "Real schema/claim/upload/negative validation only; no inference or PTU evaluation",
    "parentAction": {
        "privateEndpointName": "pe-content-ai",
        "resourceId": "/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/rg-ptu-content-demo/providers/Microsoft.CognitiveServices/accounts/aif-ptuv-content-260911",
        "groupId": "account",
        "zones": ["privatelink.cognitiveservices.azure.com",
                  "privatelink.openai.azure.com", "privatelink.services.ai.azure.com"],
        "lastArmCheck": "ResourceNotFound; guarded execution692",
        "reason": "Fourth approved PE requires parent helper account/multi-zone support or central creation"}}
(folder / "api-resume-update.json").write_text(json.dumps(update, indent=2), encoding="utf-8")
stop_path = folder / "cloud-stop-state.json"
stop = json.loads(stop_path.read_text())
stop["previousMeasurementSource"] = stop["source"]
stop["source"] = "Guarded replica list execution716: Processor/Workflow/Web0; execution719: API[] after cooldown"
stop["recordedUtc"] = now
stop["apiInitiallyRetainedOneReplicaDuringCooldown"] = True
stop["apiTargetedPauseScript"] = "Stop-ContentCloud.ps1 -Service api"
stop_path.write_text(json.dumps(stop, indent=2), encoding="utf-8")
result_path = folder / "result.json"
result = json.loads(result_path.read_text())
result["cloudApplication"] = snapshot
result["apiResumeUpdate"] = update
result["cloudStopState"] = stop
result["currentBlockers"] = [
    "Fourth owned AI account PE and three DNS bindings require parent helper extension/central creation; do not relax PNA/firewall",
    "Actual CU/model processing not submitted pending private AI DNS/data authorization",
    "Public browser access unverified; API/Web internal only"]
result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"recordedUtc": now, "imageRevision": "r3",
                  "exportedApiRequests": len(ms), "model": 0, "cu": 0,
                  "replicas": {s: stop[s] for s in ("api", "processor", "workflow", "web")}}, indent=2))
