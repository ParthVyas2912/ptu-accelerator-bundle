"""Generate the first-pass result from actual captured evidence; no network I/O."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent.parent
E = B / "evidence" / "macae"


def load(name):
    return json.loads((E / name).read_text(encoding="utf-8-sig"))


old = load("result-before-private-runtime.json")
ledger = load("cloud-model-ledger.json")
state = load("cloud-final-state.json")
identity = load("runtime-identity.json")
ingestion = load("cloud-ingestion.json")
readiness = load("cloud-readiness.json")
records = list(ledger["records"].values())
assert ledger["used"] == ledger["limit"] == len(records) == 12
assert all(r["http_status"] == 200 for r in records)
assert readiness["success"]
assert len(ingestion["datasets"]) == 2
assert all(d["documentCount"] == 1 and len(d["matches"]) == 1 for d in ingestion["datasets"])
assert state["app"]["scale"]["minReplicas"] == 0
assert state["app"]["scale"]["maxReplicas"] == 1
backend = next(c for c in state["app"]["containers"] if c["name"] == "backend")
assert backend["gate"] == ["false"]
assert backend["image"].endswith("ef9b436b6bee78259d00180899a86f3724adb385843c54245e79893eb691386d")
known = [r for r in records if r["input_tokens"] is not None]
assert len(known) == 7
sub = old["subscriptionId"]
own = f"/subscriptions/{sub}/resourceGroups/rg-ptu-macae-demo"
platform = f"/subscriptions/{sub}/resourceGroups/rg-ptu-bundle-platform"
app_id = own + "/providers/Microsoft.App/containerApps/ptu-macae"
base = own + "/providers/"
resource_ids = {
    "app": app_id,
    "foundry": base + "Microsoft.CognitiveServices/accounts/ptumacae7d804f70",
    "project": base + "Microsoft.CognitiveServices/accounts/ptumacae7d804f70/projects/ptu-macae-project",
    "cosmos": base + "Microsoft.DocumentDB/databaseAccounts/ptu-macae-7d804f70-cosmos",
    "blob": base + "Microsoft.Storage/storageAccounts/ptumacae7d804f70st",
    "search": base + "Microsoft.Search/searchServices/ptu-macae-7d804f70-srch",
    "identity": identity["identity"]["id"],
    "searchPrivateEndpoint": platform + "/providers/Microsoft.Network/privateEndpoints/pe-macae-search",
}
resources = old["resourcesCreated"] + [
    {"name": "id-ptu-macae", "type": "User-assigned managed identity", "id": resource_ids["identity"]},
    {"name": "ptu-macae", "type": "Container App", "id": app_id, "sku": "Consumption",
     "location": "eastus2", "maxReplicas": 1, "minReplicas": 0, "cpu": 1, "memoryGiB": 2},
    {"name": "pe-macae-search", "type": "Private endpoint", "id": resource_ids["searchPrivateEndpoint"],
     "groupId": "searchService", "createdBy": "MACAE through approved parent helper"},
]
for dataset in ingestion["datasets"]:
    resources += [
        {"name": dataset["blob"], "type": "Synthetic Blob object", "container": dataset["container"],
         "bytes": dataset["bytes"], "sha256": dataset["sha256"]},
        {"name": dataset["index"], "type": "Search index", "documents": dataset["documentCount"],
         "parent": "ptu-macae-7d804f70-srch"},
    ]

tests = [
    {"feature": "Private data connectivity", "expected": "Private DNS and MI access to Cosmos/Blob/Search",
     "actual": "PASS", "modelCalls": 0, "evidence": "cloud-readiness.json"},
    {"feature": "Native HR save/select", "expected": "Official team persisted and selected",
     "actual": "PASS: both HTTP200; two native agents", "modelCalls": 0,
     "evidence": ["cloud-hr-seed.json", "cloud-hr-selection.json"]},
    {"feature": "Native planning", "expected": "Approval-gated structured plan",
     "actual": "PARTIAL: request200 and plan event; event data is dataclass repr, not structured object",
     "modelCalls": 4, "callNumbers": [1, 2, 3, 4], "evidence": ["cloud-hr-request.json", "cloud-hr-events.json"]},
    {"feature": "Explicit human approval", "expected": "Continue only after tester approval",
     "actual": "PASS through native API: approval200, then HR clarification",
     "modelCalls": 3, "callNumbers": [5, 6, 7], "evidence": "cloud-approval-events.json"},
    {"feature": "Clarification and HR demo actions", "expected": "Clarify inputs and execute native HR tools",
     "actual": "PARTIAL PASS: clarification200; seven demonstration actions reported and seven MCP action calls observed",
     "modelCalls": 5, "callNumbers": [8, 9, 10, 11, 12],
     "realEnterpriseTransactions": False, "individualToolParametersSeparatelyInstrumented": False,
     "evidence": ["cloud-clarification-events.json", "cloud-mcp-execution-observation.json"]},
    {"feature": "IT onboarding and final synthesis", "expected": "Successful full workflow",
     "actual": "BLOCKED: cap exhausted; native generic Connection error; no successful final result",
     "additionalUpstreamRequests": 0, "evidence": "cloud-clarification-events.json"},
    {"feature": "Native RFP/contract ingestion", "expected": "Two synthetic documents privately indexed",
     "actual": "PASS: one document per index, keyword Canada matched both; replay retained document counts",
     "modelCalls": 0, "adaptation": ingestion["adaptation"],
     "evidence": ["cloud-ingestion-initial.json", "cloud-ingestion.json"]},
    {"feature": "RFP grounding and contract conflicts", "expected": "Grounded findings, three seeded conflicts and approval",
     "actual": "BLOCKED/UNVERIFIED: hosted-tool private egress, server-side accounting and call allowance",
     "modelCalls": 0, "notProvenBy": "Successful keyword ingestion/search"},
    {"feature": "Native MCP unavailable tool and repeatability", "expected": "ToolError and identical blueprint",
     "actual": "PASS at component level; no full repeated onboarding", "modelCalls": 0,
     "evidence": "cloud-mcp-check.json"},
    {"feature": "Genuine frontend", "expected": "Native local and cloud browser UI",
     "actual": "Local build/browser PASS; internal cloud proxy/config PASS; public cloud browser403",
     "modelCalls": 0, "evidence": ["ui-browser.json", "cloud-readiness.json"]},
    {"feature": "Plan rejection/cancellation", "expected": "Reject/cancel workflow safely",
     "actual": "UNVERIFIED: not exercised within allowance"},
]
phases = [
    {"phase": "request/planning", "callNumbers": [1, 2, 3, 4]},
    {"phase": "approval continuation", "callNumbers": [5, 6, 7]},
    {"phase": "clarification continuation", "callNumbers": [8, 9, 10, 11, 12]},
]
for phase in phases:
    phase["attempts"] = len(phase["callNumbers"])
    phase["byRequestedDeployment"] = dict(Counter(
        ledger["records"][str(i)]["model_requested"] for i in phase["callNumbers"]))

result = {
    "app": "Multi-Agent Custom Automation Engine",
    "evaluationDate": "2026-09-12",
    "latestEvidenceUtc": datetime.now(timezone.utc).isoformat(),
    "status": "VERIFIED_PARTIAL_NATIVE_CLOUD_WORKFLOW_INFERENCE_DISABLED",
    "fullEndToEndSuccess": False,
    "recommendation": "Retain disabled scale-to-zero evaluation. Resolve allowance/resumability, hosted-KB private egress/accounting and restricted browser access before more live work.",
    "repository": old["repository"],
    "subscriptionId": sub,
    "tenantId": old["tenantId"],
    "resourcesCreated": resources,
    "resourceIds": resource_ids,
    "finalPaaSSettings": load("cloud-service-state.json"),
    "resourcesModified": old["resourcesModified"] + identity["assignments"],
    "runtimeIdentity": identity["identity"],
    "runtimeRoleAssignmentsCount": len(identity["assignments"]),
    "resourcesReusedForInference": [],
    "sharedResourcesReused": {
        "environmentId": platform + "/providers/Microsoft.App/managedEnvironments/cae-ptu-bundle",
        "registryId": platform + "/providers/Microsoft.ContainerRegistry/registries/acrptubundle7d804f70",
        "registrySku": "Basic", "registryAdminEnabled": False,
        "vnet": "vnet-ptu-bundle", "tenantNetworkType": "MCAPS isolated platform, NOT JDCP hub",
        "cosmosAndBlobPrivateEndpointsCreatedBy": "parent",
        "modificationsByMacae": ["Own macae/* image pushes", "AcrPull for own UAMI",
                                 "Approved Search private endpoint and integrated existing-zone DNS records"],
        "createdAdditionalVnet": False, "createdAdditionalEnvironment": False,
        "createdAdditionalRegistry": False, "createdPrivateDnsZone": False,
    },
    "failedResourceCreations": old["failedResourceCreations"],
    "policy": {"protectedResourcesTouched": False, "policyDisabledPublicDataAccessReenabled": False,
               "localAuthEnabled": False, "ptuPurchases": 0, "capacityIncreases": 0,
               "networkPolicyBypassed": False, "duplicateNetworkCreated": False, "syntheticDataOnly": True,
               "currentServiceSettingsEvidence": "cloud-service-state.json"},
    "runtime": {
        "cloud": state,
        "url": "https://" + state["app"]["ingress"]["fqdn"],
        "workflowRevision": "ptu-macae--0000002",
        "workflowReplica": "ptu-macae--0000002-7b884d764-qvrkr",
        "workflowBackendDigest": "sha256:ee9c1c763aa3b2a7310ec0ace64427f5e10ee2bca452ac52e5547fe7ea62d65f",
        "sessionId": "ptu-macae-cloud-91dfa4d3",
        "planId": "82e5df2b-00a2-4a12-a248-af425f12caa6",
        "internalPlanId": "2100d6d3-110f-4b44-a9e5-62d90f59e87c",
        "clarificationRequestId": "315b4659-bd2e-4a99-8f25-90da1014999f",
        "local": [{"component": "backend/UI", "port": 8111, "formerPid": 15244, "status": "STOPPED"},
                  {"component": "MCP", "port": 5111, "formerPid": 13380, "status": "STOPPED"}],
        "ingress": {"allowedCidr": "174.112.74.34/32", "cloudBrowserHttpStatus": 403,
                    "bodyObserved": "RBAC: access denied", "cause": "UNRESOLVED; no restriction changed",
                    "nativeSampleUserAuthEnabled": False, "productionAuthVerified": False},
        "privateDataProbe": readiness,
    },
    "functionalTests": tests,
    "modelAccounting": {
        "liveAttempts": 12, "limit": 12, "remaining": 0, "httpStatuses": {"200": 12},
        "byRequestedDeployment": dict(Counter(r["model_requested"] for r in records)),
        "phases": phases,
        "knownUsageSubtotal": {
            "responses": len(known),
            "inputTokens": sum(r["input_tokens"] for r in known),
            "outputTokens": sum(r["output_tokens"] for r in known),
            "cachedInputTokens": sum(r["cache_tokens"] for r in known),
            "cacheIsSubsetOfInput": True,
        },
        "responsesWithUncapturedUsage": 5,
        "completeWorkloadTokenTotal": None,
        "missingUsageCause": "Evaluation observer pretty-JSON parsing defect; not proven service omission. Fixed offline/final image, no historic backfill.",
        "latencyMs": {"min": min(r["latency_ms"] for r in records), "max": max(r["latency_ms"] for r in records),
                      "scope": "Observed HTTPX wrapper/ledger wall time, not pure service latency"},
        "ledgerEvidence": "cloud-model-ledger.json",
        "zeroWireInitialFlagFailureEvidence": "cloud-initial-guard-failure.json",
        "budgetDocumentId": ledger["id"],
        "budgetPartition": "__ptu_macae_evaluation__",
        "nextUpstreamAttemptBlocked": True,
        "fullWorkflowCallCount": None,
    },
    "ptu": {
        "purchasedOrTested": False,
        "actualDeploymentSku": "GlobalStandard",
        "capacity10MeansTenPtus": False,
        "exactGpt54AndMiniProvisionedEligibility": "UNVERIFIED",
        "sizing": "Insufficient complete workload/usage/concurrency evidence; no one-PTU fixed-token assumption",
        "featureDependence": {
            "planningSpecialistAndFinalReasoning": "Inference layer only; Standard proved adequate for observed segment",
            "humanApprovalWaitAndUi": "No direct PTU dependence; surrounding continuation reasoning separate",
            "nativeMcpDemoTools": "No model/PTU consumption in tested tool implementations",
            "nativeTextBlobToSearchIngestion": "No model or embedding calls",
            "rfpContractGrounding": "Agent/KB reasoning potentially inference-billed; hosted-tool path unverified",
            "dataComputeNetworkMonitoring": "Separate Azure charges, not included in PTUs",
        },
    },
    "costReference": {
        "currency": "USD", "bindingQuoteOrInvoice": False,
        "searchBasicHourly": 0.101, "searchBasic730Hours": 73.73,
        "acaFullyActiveHourlyForRequestedResources": 0.108,
        "acaRequestsPerMillion": 0.4,
        "separateCharges": ["Cosmos Serverless RU/storage", "Blob storage/operations",
                            "Shared Basic ACR", "Private endpoints/DNS", "Cross-region traffic",
                            "Model input/output/cache tokens", "Any diagnostics"],
        "exactTotalHourlyBaseline": None,
        "pauseDoesNotStopSearchAndSharedFixedCosts": True,
        "freeGrantsAssumed": False,
    },
    "deviations": [
        "Approved single ACA app with three native sidecar services; not stock azd up",
        "Evaluation-only HTTPX observer, persistent Cosmos CAS gate and app entrypoint",
        "MCP UV_NO_SYNC=true and TCP9000 probes for official image runtime compatibility",
        "Native index_datasets.py credential constructor adapted from AzureCliCredential to runtime MI only",
        "No modification to tracked original repository source",
    ],
    "validation": {"repositoryFocusedUnitTestsPassed": 123,
                   "evidence": "final-offline-validation.json",
                   "additionalOfflineBudgetObserverTestsPassed": 7,
                   "additionalOfflineModelRequests": 0,
                   "coverage": ["CAS", "concurrency", "no reset", "fail closed", "twelve-request hard cap",
                                "remote KB block", "pretty JSON", "fragmented SSE", "bounded JSON capture"],
                   "correctedObserverLiveRetest": "NOT RUN: allowance exhausted"},
    "operations": {"inferenceEnabled": False, "minReplicas": 0, "maxReplicas": 1,
                   "lastObservedReplicaCount": state["replicaCount"],
                   "replicaObservationUtc": state["observedAtUtc"],
                   "livenessAndTcpProbes": True, "privateDependencyProbe": "PASS",
                   "appInsightsConfigured": False, "durableEnvironmentLogDestination": None,
                   "alertsDeployed": False, "automaticRollbackVerified": False,
                   "backupRestoreVerified": False, "productionReady": False},
    "commandsExecuted": [
        "scripts/Deploy-MacaeCloud.ps1 (guarded ARM validate/create)",
        "scripts/Add-LabPrivateEndpoints.ps1 -App macae -ParametersFile scripts/macae-search-pe.parameters.json",
        "scripts/Invoke-MacaeCloudTest.ps1 -Action probe|seed-hr|plan|ledger|ingest (individual calls)",
        "scripts/Invoke-MacaeCloudProgram.ps1 with native approval/clarification/MCP test scripts",
        "scripts/Set-MacaeCloudMode.ps1 -Mode Start",
        "scripts/Set-MacaeCloudMode.ps1 -Mode Pause",
        "scripts/Get-MacaeCloudState.ps1",
        "python scripts/test_macae_cloud_budget.py",
        "docker build/push own macae/backend:8ac703a7-eval3 and eval4; full commands in cloud runbook",
        "git status --porcelain and git rev-parse HEAD (original tracked source unchanged)",
    ],
    "blockingDecisions": [
        "No further calls authorized. Possible next request: up to12 additional attempts, total24, only after supported session-resume inspection; no guarantee of full completion or permission to reset ledger.",
        "Approve supported private Foundry-hosted-tool egress and service-side call accounting before RFP/contract reasoning; no policy/firewall weakening.",
        "Resolve approved-client403 without broadening ingress; cloud browser workflow remains unverified.",
    ],
    "report": "reports/macae.md",
    "runbook": "reports/macae-cloud-runbook.md",
    "historicalEvidence": ["result-before-private-runtime.json", "report-before-private-runtime.md",
                           "continuation-infrastructure.json", "container-preparation.json"],
}
(E / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "liveAttempts": 12,
                  "usageSubtotal": result["modelAccounting"]["knownUsageSubtotal"],
                  "replicasObserved": state["replicaCount"], "file": str(E / "result.json")}))
