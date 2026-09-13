"""Secret-free read-only ARM/runtime snapshot and evaluation-result update."""
import datetime
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import psutil

BUNDLE = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval"
SUB = "1feb53b2-854a-4ea7-b5a6-709b7d804f70"
RG = "rg-ptu-content-demo"
BASE = f"/subscriptions/{SUB}/resourceGroups/{RG}"


def az(arguments, query):
    args = arguments + ["--subscription", SUB, "--query", query, "-o", "json"]
    quoted = ",".join("'" + arg.replace("'", "''") + "'" for arg in args)
    command = f"& '{BUNDLE / 'Invoke-LabAz.ps1'}' -AzArguments @({quoted})"
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", command],
                            capture_output=True, text=True, timeout=150)
    if result.returncode:
        return {"inspectionError": result.stderr[:1500]}
    return json.loads(result.stdout)


state = {"capturedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "approval": "content-native-eastus2", "subscription": SUB, "resourceGroup": RG}
state["resources"] = az(["resource", "list", "-g", RG],
                        "[].{id:id,name:name,type:type,location:location,sku:sku}")
state["storage"] = az(["storage", "account", "show", "-g", RG, "-n", "stptuvcontent260911"],
    "{state:provisioningState,publicNetworkAccess:publicNetworkAccess,networkRules:networkRuleSet,sharedKeyAccess:allowSharedKeyAccess,sku:sku.name}")
state["cosmos"] = az(["cosmosdb", "show", "-g", RG, "-n", "cosmos-ptuv-content-260911"],
    "{state:provisioningState,capacity:capacity,api:apiProperties,publicNetworkAccess:publicNetworkAccess,ipRules:ipRules}")
state["mongoDatabaseThroughput"] = az(["cosmosdb", "mongodb", "database", "throughput", "show",
    "-g", RG, "-a", "cosmos-ptuv-content-260911", "-n", "ptu-content-db"],
    "{throughput:resource.throughput,autoscale:resource.autoscaleSettings}")
state["ai"] = az(["cognitiveservices", "account", "show", "-g", RG, "-n", "aif-ptuv-content-260911"],
    "{state:properties.provisioningState,disableLocalAuth:properties.disableLocalAuth,publicNetworkAccess:properties.publicNetworkAccess,network:properties.networkAcls}")
state["model"] = az(["cognitiveservices", "account", "deployment", "show",
    "-g", RG, "-n", "aif-ptuv-content-260911", "--deployment-name", "gpt-5.1"],
    "{name:name,sku:sku,model:properties.model,state:properties.provisioningState}")
state["appconfig"] = az(["appconfig", "show", "-g", RG, "-n", "appcs-ptuv-content-260911"],
    "{state:provisioningState,sku:sku.name,disableLocalAuth:disableLocalAuth,dataPlaneProxy:dataPlaneProxy,publicNetworkAccess:publicNetworkAccess}")
state["storagePolicyModification"] = az(["monitor", "activity-log", "list",
    "--resource-id", BASE + "/providers/Microsoft.Storage/storageAccounts/stptuvcontent260911",
    "--offset", "2h"], "[?operationName.value=='Microsoft.Authorization/policies/modify/action'].{time:eventTimestamp,properties:properties}")
state["memoryAvailableGiB"] = round(psutil.virtual_memory().available / 1024**3, 3)
state["runtime"] = json.loads((ROOT / "native-state.json").read_text()) if (
    ROOT / "native-state.json").exists() else None
state["listeners"] = {}
for port in (8113, 5113):
    with socket.socket() as sock:
        state["listeners"][str(port)] = sock.connect_ex(("127.0.0.1", port)) == 0
ledger = ROOT / "native-requests.sqlite"
state["requestLedger"] = []
if ledger.exists():
    with sqlite3.connect(ledger) as db:
        db.row_factory = sqlite3.Row
        state["requestLedger"] = [dict(row) for row in db.execute("SELECT * FROM requests ORDER BY id")]
state["fixedCostUsdPerHour"] = 0.082
state["fixedCostIsMeasuredBill"] = False
state["blockers"] = [
    "MCAPSGovDeployPolicies / StorageAccount_PublicNetwork_Modify changed new storage publicNetworkAccess to Disabled; real Blob/Queue data-plane requests returned AuthorizationFailure. No network policy override or private endpoint was attempted.",
    "CU GA prebuilt-layout metadata GET returned HTTP403 Virtual Network/Firewall rules despite exact client-IP allowlist; no CU analysis was sent.",
    "Native supervisor admission refused startup with less than 5 GiB available; observed shared-host available memory fell to 0.62 GiB.",
    "Initial AppConfig key deployment failed because ARM data-plane proxy defaulted to local authentication. Narrow Entra pass-through/Data Owner repair was applied, but immediate ARM and SDK settings writes returned Forbidden; settings remain unpopulated at latest check."
]
folder = BUNDLE / "evidence/content"
(folder / "native-deployment.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
result_path = folder / "result.json"
result = json.loads(result_path.read_text(encoding="utf-8"))
result["status"] = "approved_native_infrastructure_created_e2e_blocked_by_network_policy_and_host_memory"
result["nativeDeployment"] = state
result["azure"]["proposalApproved"] = True
result["azure"]["createdResources"] = state["resources"]
result["azure"]["parentMessaging"] = "Approval received by parent turn; do not use session UUID as agent ID."
result["azure"]["proposedModel"] = {"name": "gpt-5.1", "version": "2025-11-13",
    "sku": "GlobalStandard", "capacityRequest": 50, "actualDeployment": state["model"]}
proposal = result["nativeInfrastructureProposal"]
proposal["status"] = "approved_resources_created_e2e_blocked"
proposal["approvedAt"] = "2026-09-11T20:19:24-04:00"
proposal["nameAvailabilityChecked"] = True
proposal["allListedExceptionsApproved"] = True
proposal["localMemoryPlan"] = {"aggregateBudgetGiB": 4, "hardWindowsJobCommitLimit": True,
    "aggregateRssWatchdog": True, "freeMemoryAdmissionGiB": 5, "minimumFreeMemoryGiB": 1,
    "perProcessGuardGiB": None, "sequentialServiceStartup": True, "guardImplementedYet": True,
    "observedAdmissionRejected": True}
result["requiredInfrastructureInterpretation"] = "Historical stock Azure stack below; actual adapted-native resource inventory is nativeDeployment.resources. Stock ACA/ACR/GRS resources were not provisioned."
result["runtimeScripts"] = ["scripts/Start-ContentNative.ps1", "scripts/Stop-ContentNative.ps1",
    "scripts/content-runtime/native_supervisor.py", "scripts/content-runtime/content_guard.py",
    "scripts/content-runtime/exercise_app.py"]
result["nativeSafeguardTests"] = {
    "guardUnitTest": "PASS using local MockTransport only: 12 admitted, 13th blocked, nonapproved endpoint blocked; zero live model requests",
    "hardMemoryJobTest": "PASS: Windows aggregate 4-GiB committed-memory job configured",
    "nativeStartup": "Refused before any child service or Mongo credential retrieval: free-memory admission",
    "frontendLocalhostBuild": {"status": "passed", "node": "22.22.0", "api": "http://127.0.0.1:8113",
                               "authDisabledOnlyForLoopback": True, "gzipJsBytesReportedKB": 427.76},
    "poppler": {"version": "26.07.0", "archiveSha256": "a711b0563b06edc488583d28198b6734c5a494afbbd1b9d87d3d2866062fb7e2",
                "syntheticClaimPdfPages": 1},
    "runtimeAgentFrameworkImports": "passed in Processor and Workflow locked environments",
}
result["measuredTraffic"]["liveModelCallsInitiated"] = sum(x["kind"] == "model" for x in state["requestLedger"])
result["measuredTraffic"]["liveCuAnalysesInitiated"] = sum(x["kind"] == "cu-analyze" for x in state["requestLedger"])
result["measuredTraffic"]["cuMetadataRequests"] = [x for x in state["requestLedger"] if x["kind"] == "cu-metadata"]
result["measuredTraffic"]["liveErrors"] = [{"service": "CU metadata, not analysis", "status": 403,
                                    "error": "Access denied due to Virtual Network/Firewall rules"}]
result["endpointsAndProcesses"]["nativeGuardAttempt"] = state["runtime"]
result["endpointsAndProcesses"]["listenerVerification"] = state["listeners"]
result["endpointsAndProcesses"]["cloudDependencyEndpoints"] = [
    "https://appcs-ptuv-content-260911.azconfig.io",
    "https://stptuvcontent260911.blob.core.windows.net",
    "https://stptuvcontent260911.queue.core.windows.net",
    "https://aif-ptuv-content-260911.openai.azure.com",
    "https://aif-ptuv-content-260911.cognitiveservices.azure.com",
    "https://aif-ptuv-content-260911.services.ai.azure.com/api/projects/ptu-content-project"]
for test in result.get("functionalTests", []):
    if test.get("id") == "complete-claim":
        test["actual"] = "Not submitted: approved dependencies created, but storage governance policy disables public access; native memory guard rejected startup."
result["secretHandlingCurrent"] = {"mongoCredentialRetrieved": False,
    "EntraTokensRuntimeOnly": True, "secretEnvFilesCreated": False,
    "foundryStorageAppConfigKeysRetrieved": False,
    "mongoCredentialExceptionApprovedButNotUsed": True}
result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"capturedUtc": state["capturedUtc"], "resourceCount": len(state["resources"]),
                  "listeners": state["listeners"], "requests": len(state["requestLedger"]),
                  "memoryAvailableGiB": state["memoryAvailableGiB"]}, indent=2))
