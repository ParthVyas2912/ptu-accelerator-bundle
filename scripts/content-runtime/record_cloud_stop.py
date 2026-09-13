"""Record measured stop state without reopening throttled exec sessions."""
import json
from pathlib import Path

folder = Path(__file__).resolve().parents[2] / "evidence/content"
path = folder / "result.json"
result = json.loads(path.read_text(encoding="utf-8"))
if result.get("inferenceEvaluation"):
    raise RuntimeError("Historical pre-inference recorder: use capture_inference_result.py after live processing")
result["cloudStopState"] = json.loads((folder / "cloud-stop-state.json").read_text())
assert all(result["cloudStopState"][service] == 0
           for service in ("api", "processor", "workflow", "web")), "Stop state must be measured zero"
result["status"] = "four_private_services_deployed_real_api_tests_passed_paused_zero_replicas_ai_private_endpoint_blocked"
result["cloudRunbook"] = "reports/content-cloud-runbook.md"
result["endpointsAndProcesses"]["runningCloudReplicas"] = 0
if not result["cloudApplication"]["application"].get("functional-results.json"):
    note = "Complete Blob evidence export deferred; inspect the last export outcome before retry."
    if note not in result["currentBlockers"]:
        result["currentBlockers"].append(note)
result["cloudSafeguards"]["resumeDriverUpdate"] = "API r3 published: recover functional state from Blob and protect existing-claim submission against duplicates. Workers remain r2."
result["cloudSafeguards"]["pauseVerification"] = "All four replica counts0 after min0/no-worker-scalers and explicit worker revision deactivation."
result["costCaveatsCurrent"] = {
    "knownDependencyBaselineUsdPerHour": 0.082,
    "privateEndpointsCreated": 3,
    "privateLinkEndpointAndDataChargesAdditional": True,
    "privateLinkRateVerified": False,
    "sharedPlatformChargesAdditional": True,
    "allFourActiveComputeScenarioUsdPerHour": 0.216,
    "measuredCloudBill": None,
    "currentReplicaCount": 0}
apps = result["cloudApplication"]["apps"]
known = {item.get("id") for item in result["azure"]["createdResources"]}
for app in apps:
    if app["id"] not in known:
        result["azure"]["createdResources"].append({
            "id": app["id"], "name": app["name"], "type": "Microsoft.App/containerApps",
            "location": "eastus2"})
identity_values = [
    ("api", "7df1b86c-d3b0-483e-aa4e-c9d8b204f1e8", "a5e65d18-76ca-4896-a9e0-64e09ab452a4"),
    ("processor", "5101963f-1e38-45d2-9f7c-efa9e9f6d122", "2fb78897-c99b-4447-a2c9-4c74ed974b9f"),
    ("workflow", "835c3d55-d53a-489d-964c-48fd4f158870", "43eb7397-f10e-4616-86e0-2022c1aabba6"),
    ("web", "6d199236-8792-4d88-8952-6ea8211a2f7b", "2c87d345-6056-4fd1-88ad-f71adf151d27")]
result["cloudManagedIdentities"] = []
for service, client, principal in identity_values:
    name = "id-ptu-content-" + service
    identity = {
        "service": service, "name": name, "clientId": client, "principalId": principal,
        "id": "/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/rg-ptu-content-demo/providers/Microsoft.ManagedIdentity/userAssignedIdentities/" + name,
        "type": "Microsoft.ManagedIdentity/userAssignedIdentities", "location": "eastus2",
        "source": "Succeeded ptu-content-cloud-identities deployment outputs"}
    result["cloudManagedIdentities"].append(identity)
    if identity["id"] not in known:
        result["azure"]["createdResources"].append(identity)
result["originalApplicationSourceUnchanged"] = True
path.write_text(json.dumps(result, indent=2), encoding="utf-8")
assert result["measuredTraffic"]["liveModelCallsInitiated"] == 0
assert result["measuredTraffic"]["liveCuAnalysesInitiated"] == 0
for app in apps:
    for container in app["containers"]:
        assert "APP_COSMOS_CONNSTR" not in {env["name"] for env in container.get("env", [])}
print("Final cloud report JSON validated; runtime credential absent from ACA env; model0/CU0; all replicas0.")
