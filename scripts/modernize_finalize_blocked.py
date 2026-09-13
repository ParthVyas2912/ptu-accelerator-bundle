"""Refresh requested evidence from actual observations; no Azure/model operations."""
from datetime import datetime, timezone
import json
from pathlib import Path

B = Path(__file__).resolve().parents[1]
OUT = B/"evidence/modernize"
if (OUT/"cloud-e2e.json").exists():
    raise SystemExit("Cloud E2E evidence supersedes this historical blocked-state finalizer.")
def read(name):
    return json.loads((OUT/name).read_text(encoding="utf-8-sig"))

result = read("result.json")
ledger = read("native-model-events.json")
preflight = read("native-e2e.json")
persistence = read("persistence.json")
blocker = read("network-policy-blocker.json")
assert not preflight["processing_clicked"]
assert len(ledger["model_events"]) == 0, "Do not overwrite evidence after a live native run."
assert preflight["persistence_preflight"]["http_status"] == 500

result.update(
    status="partial_native_deployment_blocked_by_enforced_persistence_network_policy",
    full_deployment=False,
    full_functional_e2e=False,
    updated_at=datetime.now(timezone.utc).isoformat(),
    current_blocker=blocker,
    regression_tests=read("regression-tests.json"),
)
azure = result["azure"]
azure["created_resource_group"] = {"name": "rg-ptu-modernize-demo", "location": "canadacentral"}
azure["created_billable_infrastructure"] = [
    {"name": "stptumodernize0911pv", "type": "StorageV2", "sku": "Standard_LRS",
     "access_tier": "Hot", "region": "canadacentral", "status": "Succeeded",
     "public_network_access": "Disabled", "allow_shared_key_access": False,
     "allow_blob_public_access": False, "container": "ptu-modernize-files"},
    {"name": "cosmos-ptu-modernize-0911", "type": "Cosmos NoSQL",
     "capacity_mode": "Serverless", "region": "canadacentral",
     "status": "Failed regional access / capacity; retained, not deleted"},
    {"name": "cosmos-ptu-modernize-eus20911", "type": "Cosmos NoSQL",
     "capacity_mode": "Serverless", "region": "eastus2", "region_count": 1,
     "status": "Succeeded", "public_network_access": "Disabled", "disable_local_auth": True,
     "database": "ptu-modernize", "containers": [
         {"name": "ptu-modernize-batches", "partition_key": "/batch_id"},
         {"name": "ptu-modernize-files", "partition_key": "/file_id"},
         {"name": "ptu-modernize-logs", "partition_key": "/log_id"}]},
]
azure.pop("proposed_not_created", None)
azure["proposal_status"] = "Initial persistence and explicit East US 2 fallback approved and provisioned; network governance now blocks data-plane access"
azure["persistence_setup"] = persistence
azure["residency_limitation"] = persistence["residencyLimitation"]
azure["native_agent_ids"] = ledger.get("agents", [])
azure["retained_previous_agent_sets"] = ledger.get("previous_agent_sets", [])
azure["network_changes_on_new_accounts_only"] = {
    "request": "one source-IP-only public access enable request per new successful persistence account",
    "actual": "IP rules added, but management-group modify policies retained Disabled on both",
    "policy_bypassed_or_exempted": False, "source_ip": "20.236.11.102",
    "shared_foundry_network_changed": False,
}
result["endpoints"].update(
    native_agents_initialized=True, cosmos_history_http_status=500,
    cosmos_underlying_http_status=403,
    local_listen_addresses=["127.0.0.1:8114", "127.0.0.1:5114"],
    model_route_ingress="loopback only; original development auth mode unsuitable for public hosting",
)
for proc in result["processes"]:
    if proc["shell_id"] == "modernize-backend":
        proc.update(pid=28980, status="running; 5 agents initialized; EUS2 Cosmos data-plane blocked by network policy",
                    persistence="actual approved Azure clients, not recording/mock substitutes")
    if proc["shell_id"] == "modernize-frontend":
        proc.update(pid=34380, status="running; HTTP 200; original built React rendered in real Chromium")
result["usage"].update(
    native_model_requests=0,
    protocol_component_model_requests=4,
    remaining_requests=8,
    model_requests=4,
    raw_native_ledger="native-model-events.json",
    full_native_batch_processing_started=False,
)
for test in result["tests"]:
    if test["id"] == "upstream-failure-placeholder":
        test.update(scope="Actual imported-source conversion module pytest suite",
                    actual="11 passed in 11.70 seconds, none deselected; authorized 3-line source fix",
                    status="fixed_regression_pass")
    elif test["id"] == "multifile-upload-download":
        test.update(actual="Evaluator stopped at real native history preflight: HTTP500 / Cosmos403 due enforced network policy; no upload or processing click",
                    status="blocked")
    elif test["id"] == "original-five-agent-sdk-pipeline":
        test.update(scope="Original native application with actual approved Azure persistence clients",
                    expected="Full native SQL-agent batch processing within remaining 8 model requests",
                    actual="All 5 original agents initialized, but no native processing/model call before blocked persistence preflight",
                    status="not_run_blocked")
result["tests"].append({
    "id": "original-ui-browser-render", "scope": "Real Chromium against original built React",
    "expected": "App title, file input, and translation controls",
    "actual": "Modernize your code title, one file input, Browse files/Cancel/Start translating buttons",
    "status": "pass_startup_only",
})
result["tests"].extend(preflight["tests"])
result["alternatives_investigated"][0]["result"] = "Official native app built and running; approved Cosmos/Blob provisioned; network policy prevents local data-plane access"
result["alternatives_investigated"].extend(blocker["alternatives_investigated_not_executed"])
result["cost_assessment"] = {
    "persistence_planning_estimate_usd_per_hour": 0.01,
    "estimate_assumptions": "At most 10k Cosmos RU/hour, 1GB each storage service, 1000 Blob operations/hour",
    "verified_regional_quote": False,
    "retail_price_query": "Direct public regional Retail Prices API query timed out",
    "actual_invoice_or_ru_or_storage_consumption_verified": False,
    "fixed_new_hosting_or_ptu_purchases": False,
    "network_alternative_cost": "Unapproved/unprovisioned; scoped configuration and pricing require parent/governance decision",
}
result["reproduction"] = [
    "<venv>\\Scripts\\python.exe <bundle>\\scripts\\modernize_native.py (only if existing backend stopped)",
    "Original frontend: API_URL=http://127.0.0.1:8114 ENABLE_AUTH=false; python -m uvicorn frontend_server:app --host 127.0.0.1 --port 5114",
    "<venv>\\Scripts\\python.exe <bundle>\\scripts\\modernize_browser_eval.py (currently exits before upload at real persistence preflight)",
    "python <bundle>\\scripts\\modernize_sql_validation.py",
    "python <bundle>\\scripts\\modernize_validation_unit.py --after-fix",
    "PYTHONPATH=<repo>\\src; <venv>\\Scripts\\python.exe -m pytest <repo>\\src\\tests\\backend\\sql_agents\\convert_script_test.py -q",
    "Do not repeat processing if native-e2e.json processing_clicked=true; total guard remains 12 live requests",
    "modernize_configure_network.ps1 now refuses rerun after identifying the policy blocker; no bypass",
]
result["evidence_files"] = sorted(set(result["evidence_files"] + [
    "persistence.json", "storage-access.json", "network-configuration.json",
    "network-policy-events.json", "network-policy-blocker.json", "native-e2e.json",
    "native-model-events.json", "regression-tests.json",
]))
result["recommendation"] = "Investigate / external governance connectivity blocker; do not count as a full functional deployment"
result["limitations"] = [
    "No real upload/process/download batch completed; actual preflight blocked by management-group policy",
    "Four Migrator protocol runs are not native five-agent pipeline execution",
    "No Informix or SQL Server execution engine; SQLite rewrites do not establish target-engine equivalence",
    "Procedure calling/result-set semantic changes not adequately warned by model",
    "Small synthetic sample is not load, fairness or production-readiness certification",
    "Classic Agents documentation states retirement March 31, 2027; GPT5.1 support matrix must be resolved",
    "East US 2 data persistence approved only for synthetic MCAPS tests, not DND residency",
    "No PTU utilization, cost invoice, peak workload or provisioning-size benchmark",
]
network = read("network-configuration.json")
network.update(status="blocked_by_management_group_modify_policy",
               actualPublicNetworkAccess={"cosmos": "Disabled", "storage": "Disabled"},
               effectivePublicIngress="none; IP allowlist is ineffective while endpoints Disabled",
               governancePolicyBypassed=False)
(OUT/"network-configuration.json").write_text(json.dumps(network, indent=2), encoding="utf-8")
(OUT/"result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"status": result["status"], "full_deployment": False,
                  "model_requests": 4, "remaining": 8, "regression_tests_passed": 11}, indent=2))
