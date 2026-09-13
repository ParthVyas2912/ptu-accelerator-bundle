"""Reconcile immutable native workflow results and final resource snapshots."""
from datetime import datetime
import hashlib
import json
from pathlib import Path

folder = Path(__file__).resolve().parents[1] / "evidence" / "conversation"
if (folder / "serving-results.json").exists():
    raise RuntimeError("Durable serving evidence exists; use ckm_finalize_serving.py, not this historical phase finalizer.")


def load(name):
    return json.loads((folder / name).read_text(encoding="utf-8-sig"))


def save(name, value):
    (folder / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


summary = load("summary-results.json")
raw = load("data-workflow-results.json")
sql_identity = load("sql-identity-verify.json")
api = load("api-final-state.json")
ui = load("ui-final-state.json")
sql = load("sql-final-state.json")
storage = load("storage-and-roles-final.json")
search = load("search-provisioning-state.json")
pes = load("all-private-endpoints.json")
revisions = api["revisions"] + ui["revisions"]
requests = summary["requests"] + raw["requests"]
assert len(requests) == 9 and [item["sequence"] for item in requests] == list(range(1, 10))
assert len(raw["tests"]) == 14 and all(item["status"] == "passed" for item in raw["tests"])
assert all(item["http_status"] == 200 for item in requests)
assert len(revisions) == 12 and all(not item["active"] and item["replicas"] == 0 for item in revisions)
assert len(pes) == 4 and all(item["state"] == "Succeeded" for item in pes)
assert sql_identity["current_user"] == "id-ptu-conversation-runtime" and sql_identity["db_owner"] == 0
assert sql_identity["native_sql_initialized_and_reloaded"]
assert sql["server"]["admin"]["sid"] == "87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed"
assert sql["server"]["admin"]["azureAdOnlyAuthentication"]
assert sql["server"]["pna"] == storage["storage"]["pna"] == search["pna"] == "Disabled"
assert sql["database"]["minCapacity"] == 0.5 and sql["database"]["sku"]["capacity"] == 2
assert sql["database"]["autoPauseDelay"] == 60
assert storage["storage"]["sharedKey"] is False
assert search["sku"] == "basic" and search["disableLocalAuth"]
prompt = sum(item["usage"]["prompt_tokens"] for item in requests)
completion = sum(item["usage"]["completion_tokens"] for item in requests)
assert (prompt, completion, prompt + completion) == (4547, 3700, 8247)
verified_at = max(api["checked_at"], ui["checked_at"], sql["checked_at"])

dashboard = next(item["actual"] for item in raw["tests"] if item["id"] == "native-model-planned-sql-dashboard")
kpis = {item["metric"]: item["value"] for item in dashboard["kpis"]}
category_chart = next(chart for section in dashboard["sections"] for chart in section["charts"] if chart.get("field") == "category")
category_values = {row["label"]: row["value"] for row in category_chart["data"]}
assert category_values == {"VPN": 2, "Printer": 1}
quality = [
    {"id": "sql-total-records", "expected": 3, "actual": kpis["total_records"], "status": "passed"},
    {"id": "distinct-category-kpi", "expected": 2, "actual": kpis["unique_issue_categories"], "status": "failed"},
    {"id": "distinct-source-type-kpi", "expected": 1, "actual": kpis["unique_source_types"], "status": "failed"},
    {"id": "category-chart", "expected": {"VPN": 2, "Printer": 1}, "actual": category_values, "status": "passed", "evidence": "Native SQL chart and direct SQL ground truth agree"},
    {"id": "dashboard-prose", "expected": "No anonymization of ordinary connecting/action words", "actual": "Returned phrases include 'credential rotation users were resolved by users cached credentials'", "status": "failed"},
    {"id": "file-insight-cross-call-coverage", "expected": "All three records support cross-call conclusions", "actual": "Native file summary concatenates collection count with only first prior summary; insight describes one incident and makes unsupported durability/repeatability implications", "status": "failed_input_scope_and_generalization"},
]
builds = [load("remote-build-chu.json"), *load("data-build-runs.json"), load("sql-tools-build.json")]
for run in builds:
    run["elapsed_seconds"] = (datetime.fromisoformat(run["finish"]) - datetime.fromisoformat(run["start"])).total_seconds()
    run["retail_reference_usd"] = run["cpu"] * run["elapsed_seconds"] * 0.0001
cost = {
    "currency": "USD", "invoice_measured": False,
    "fixed_active_review_limit_per_hour": 1.5,
    "full_max2_sql_basic_four_pes_both_apps_32gb_reference_per_hour": 1.4797652055,
    "api_only_during_workflow_max_reference_per_hour": 1.4527652055,
    "model_input_rate_per_million": 1.75, "model_output_rate_per_million": 14,
    "cumulative_model_token_reference_usd": (prompt * 1.75 + completion * 14) / 1_000_000,
    "additional_data_workflow_token_reference_usd": (3559 * 1.75 + 2820 * 14) / 1_000_000,
    "all_remote_builds_reference_usd": sum(run["retail_reference_usd"] for run in builds),
    "search_basic_per_hour": 0.101, "four_private_endpoints_per_hour": 0.04,
    "sql_per_billed_vcore_hour": 0.62611,
    "sql_32gb_data_hourly_allowance": 0.0055452055,
    "baseline_after_sql_actually_pauses_per_hour": 0.1465452055,
    "baseline_if_sql_billed_at_min05_per_hour": 0.4596002055,
    "actual_sql_state": sql["database"]["status"],
    "sql_pause_observed": sql["database"]["status"] == "Paused",
    "last_data_connection_check": sql_identity["checked_at"],
    "auto_pause_minutes": 60,
    "aca_reported_replicas": 0,
    "excluded": ["Shared registry/DNS allocation", "Blob capacity/operations", "Network/data processing/egress", "Logs", "SQL backup overage", "Taxes/discount differences"],
    "not_ptu_charges": ["SQL", "Search", "Blob", "Private Link", "ACA", "ACR", "CU", "Separate embeddings"],
}
review = {
    "status": "native_persistence_and_model_sql_workflow_executed_with_semantic_quality_failures",
    "raw_evidence_sha256": hashlib.sha256((folder / "data-workflow-results.json").read_bytes()).hexdigest(),
    "operational_checks_passed": 14, "quality_checks": quality,
    "additional_model_requests": 2, "cumulative_model_requests": 9, "remaining_allowance": 3,
    "additional_input_tokens": 3559, "additional_output_tokens": 2820,
    "cumulative_input_tokens": prompt, "cumulative_output_tokens": completion, "cumulative_total_tokens": prompt + completion,
    "requests": requests,
    "latency_scope": "Sequences1-7 measured SDK RawResponse call;8-9 measured httpx.Client.send. Do not combine into one like-for-like latency statistic.",
    "blocked_before_dispatch_during_persistence": 6,
    "blocked_calls_are_not_dispatched_inference": True,
    "ground_truth": sql_identity["ground_truth"],
    "source_findings": {
        "kpi": "src/api/modules/insights/service.py:597 onward: query_type=count executes COUNT(*), not distinct count; labels are not checked against metric semantics.",
        "anonymization": "src/api/modules/insights/service.py:350-425: broad token extraction and replacement with users can damage ordinary prose.",
        "file_context": "src/api/modules/ingestion/service.py:372 onward: pre-enriched multi-document file summary retains collection count plus first summary; processing insights consumes file summaries, not all transcripts.",
    },
    "sql_identity_correction": {
        "initial_error": "Used principal/object ID rather than client/application ID for a TYPE=E service-principal contained user; fresh post-handoff SQL initialization failed.",
        "corrected_user": "id-ptu-conversation-runtime",
        "client_id_used_for_sql_sid": "1b458b7e-1768-45a9-b676-9a3245a4dfbe",
        "azure_rbac_still_uses_principal_id": "b0c36c36-5b9f-4efa-9f01-0e19fb97aa25",
        "roles": ["db_datareader", "db_datawriter", "db_ddladmin"],
        "db_owner": False, "app_is_server_admin": False,
        "incorrect_user_roles_removed": True, "users_or_data_deleted": False,
        "final_verified": sql_identity,
        "source": "https://learn.microsoft.com/en-us/sql/t-sql/statements/create-user-transact-sql?view=azuresqldb-current#k-create-a-contained-database-user-from-a-microsoft-entra-principal-without-validation",
    },
    "cost": cost, "builds": builds,
    "full_application_deployed": False,
    "serving_api_model_and_data_endpoints_remain_unset": True,
    "evaluation_shape": "Original native routes via in-container TestClient using real private Azure dependencies, not public browser end-to-end deployment",
    "last_verified_at": verified_at, "final_revisions": revisions,
    "final_pause_session": "ckm-final-identity-pause", "final_pause_exit_code": 0,
    "prior_failed_handoff_pause_session": "ckm-data-final-pause (exit1 from auth probe; compute pause succeeded)",
}
save("data-workflow-review.json", review)

r = load("result.json")
r.update({
    "status": review["status"], "full_application_deployed": False,
    "native_data_workflow_evidence": "evidence/conversation/data-workflow-review.json",
    "native_data_workflow_operational_tests": raw["tests"],
    "native_data_workflow_quality_tests": quality,
    "current_cost": cost, "generated_at": verified_at,
})
r["approval"].update({
    "approved_topology": "Deployed isolated S0/project/models, Basic Search, LRS Blob and serverless SQL plus shared Consumption ACA/Basic ACR/private networking. Standard Agent Cosmos/subnet/region additions are outside the listed envelope.",
    "conditional_fixed_active_limit_usd_per_hour": 1.5,
    "pre_creation_gate": "None for the deployed listed dependencies. Hosted private Explore has a separate architecture compatibility blocker.",
})
r["required_infrastructure"].update({
    "state": "created_native_private_persistence_verified_hosted_explore_blocked",
    "hosting_location": "eastus2",
})
for resource in r["required_infrastructure"]["resources"]:
    if resource["type"] == "SQL logical server/database":
        resource["min_vcores"] = 0.5
        resource["authentication"] = "Entra-only; contained managed-identity user with reader/writer/DDL roles"
r["required_infrastructure"]["excluded"] = [
    "Cosmos/dedicated agent subnet/region alignment outside the listed envelope"
    if item == "Cosmos not yet approved for Standard Agent requirement" else item
    for item in r["required_infrastructure"]["excluded"]
]
r["traffic"].update({
    "live_model_requests": 9, "request_sequence": requests,
    "input_tokens_returned": prompt, "output_tokens_returned": completion, "total_tokens_returned": prompt + completion,
    "remaining_model_request_allowance": 3,
    "retries": 0, "ptu_utilization": None,
    "ptu_utilization_reason": "Nine functional GlobalStandard requests, no provisioned deployment or load/capacity test.",
    "undispatched_ingestion_ai_calls_blocked": 6,
    "latency_scope": review["latency_scope"],
})
r["current_decision"].update({
    "action_required": "No listed-dependency approval gate remains. Private hosted Explore is incompatible with Basic Agent networking; current native quality defects are documented separately.",
    "blocking_prerequisite": "Hosted Search tool needs Standard Agent private networking/BYO Cosmos/dedicated subnet/region alignment, not another approval for deployed SQL/Search/Blob.",
    "model_requests_used": 9, "remaining_allowance": 3,
    "data_paas_resources_created": 4, "account_private_endpoints_created": 1,
    "total_private_endpoints_created": 4,
    "pause_session": "ckm-final-identity-pause", "pause_exit_code": 0,
    "final_cloud_verified_at": verified_at, "all_cloud_revisions_inactive": True,
    "cloud_reported_replicas": 0,
    "cloud_hosting_phase": "native_private_data_workflow_evaluated_serving_endpoints_unset",
    "rollout_observation": "Multiple revision bookkeeping with explicit deactivate/wait0 and max1 checks reported at most one active/replica during controlled updates; final all12 retained revisions0.",
})
if (folder / "budget-handoff.json").exists():
    handoff = load("budget-handoff.json")
    assert handoff["actual_model_attempts_used"] == len(requests)
    r["budget_handoff"] = handoff
    r["traffic"].update({
        "current_model_request_cap": handoff.get("current_model_request_cap", handoff["original_model_request_cap"]),
        "remaining_model_request_allowance": handoff["remaining_ckm_model_request_allowance"],
        "reserved_model_requests": handoff["reserved_model_requests"],
        "unused_original_allowance_released_to_coordinator": handoff["unused_allowance_released_to_coordinator"],
    })
    r["current_decision"]["remaining_allowance"] = handoff["remaining_ckm_model_request_allowance"]
r["blockers"] = [
    {"id": "hosted-private-search-compatibility", "evidence": "Basic Foundry Agent does not support private Search; own account Sweden Central differs from shared EastUS2 VNet. Standard setup requires Cosmos/dedicated agent subnet/region alignment not present in the listed envelope."},
    {"id": "native-dashboard-kpi-semantics", "evidence": "Actual native dashboard: unique categories3 versus SQL ground truth2; source types3 versus1. COUNT(*) cannot validate a distinct-count label."},
    {"id": "native-narrative-quality", "evidence": "Overbroad anonymization damages prose; file-level processing insights sees first-summary context and overgeneralizes. See manual expected/actual checks."},
    {"id": "public-browser-unverified", "evidence": "Existing /32 public path returned403; preserved unchanged. Control-plane exec works."},
]
r["latest_approval_request"].update({
    "approved": True, "fixed_active_baseline_limit_usd_per_hour": 1.5,
    "full_private_minimum_with_four_pes_both_active_apps_32gb_sql_assumption_usd_per_hour": 1.4797652055 - 1.5 * 0.62611,
    "current_blocker": r["blockers"][0]["evidence"],
    "full_private_minimum_exceeds_085_before_standard_agent_additions": "Historical0.85 comparison superseded; current deployed envelope reference1.479765/hour at SQLmax2 is below1.50.",
    "topology": "Approved isolated data/AI services plus shared Consumption ACA/private networking/Basic ACR",
})
r["ptu_sizing_guidance"]["reason_no_estimate"] = r["traffic"]["ptu_utilization_reason"]
r["azure"]["final_own_identity_roles"] = storage["own_identity_roles"]
r["azure"]["sql_identity"] = review["sql_identity_correction"]
inventory = {item["id"].lower(): item for item in r["azure"]["created_resources"]}
for item in load("own-resource-inventory.json"):
    inventory.setdefault(item["id"].lower(), item)
for endpoint in pes:
    inventory[endpoint["id"].lower()] = {"id": endpoint["id"], "type": "Microsoft.Network/privateEndpoints", "location": "eastus2", "state": endpoint["state"], "connections": endpoint["connections"]}
    for nic in endpoint["nics"]:
        inventory[nic["id"].lower()] = {"id": nic["id"], "type": "Microsoft.Network/networkInterfaces", "location": "eastus2", "purpose": "Implicit own PE NIC"}
inventory[sql["database"]["id"].lower()].update({
    "sku": "GP_S_Gen5", "min_vcores": 0.5, "max_vcores": 2,
    "auto_pause_minutes": 60, "max_data_bytes": 34359738368,
    "backup": "Local", "state": sql["database"]["status"],
})
inventory[sql["server"]["id"].lower()].update({"public_network_access": "Disabled", "entra_only": True, "administrator": sql["server"]["admin"]})
inventory[storage["storage"]["id"].lower()].update({"sku": "Standard_LRS", "public_network_access": "Disabled", "allow_shared_key": False})
inventory[search["id"].lower()].update({"sku": "Basic", "replicas": 1, "partitions": 1, "public_network_access": "Disabled", "disable_local_auth": True})
r["azure"]["created_resources"] = list(inventory.values())
r["azure"]["final_configuration_evidence"] = list(dict.fromkeys(r["azure"]["final_configuration_evidence"] + ["evidence/conversation/sql-final-state.json", "evidence/conversation/storage-and-roles-final.json", "evidence/conversation/all-private-endpoints.json"]))
observed = {
    "Upload": "Three pre-enriched records persisted through original JSON route to SQL/Blob/Search; fresh native reload passed.",
    "Indexing": "Basic accepted native14-field HNSW/semantic schema without unused remote vectorizer; literal Search returned exact two VPN calls. No vector or semantic query test.",
    "Explore": "Native Search retrieval worked; hosted-agent cross-call answer/citations still blocked by private-tool architecture.",
    "Structured SQL": "Native SQL queries executed; direct ground truth3 records/2 categories/1 source type.",
    "Model-planned": "One actual model-planned SQL dashboard call; record count and category chart correct, distinct-count KPI labels and narrative quality failed.",
    "Authentication": "Private Entra data access verified; corrected contained MI user has reader/writer/ddl_admin, not db_owner/server-admin. /32 browser path remains403.",
}
for feature in r["per_feature_ptu_dependence"]:
    for prefix, value in observed.items():
        if feature["feature"].startswith(prefix):
            feature["observed"] = value
save("result.json", r)

host = load("cloud-hosting.json")
host.update({
    "phase": "serving_endpoints_unset_native_private_data_workflow_evaluated",
    "model_attempts": 9, "native_data_workflow_evidence": "evidence/conversation/data-workflow-review.json",
    "final_verified_at": verified_at, "final_revisions": revisions,
    "pause_session": "ckm-final-identity-pause", "pause_exit_code": 0,
    "current_api_image": api["app"]["image"], "private_endpoints_created": [item["id"] for item in pes],
    "data_paas_created": [output["value"] for output in load("data-deployment.json")["outputs"].values()],
    "rollout_observation": r["current_decision"]["rollout_observation"],
    "current_sql_state": sql["database"]["status"],
    "current_cost": cost,
    "remaining_full_workflow_blockers": [item["evidence"] for item in r["blockers"]],
})
host["created"]["other_identity_grants"] = storage["own_identity_roles"]
for run in builds:
    for image in run["images"]:
        if not any(item["digest"] == image["digest"] for item in host["registry_manifests"]):
            host["registry_manifests"].append({"image": image["repository"] + ":" + image["tag"], "digest": image["digest"], "build_run": run["runId"]})
save("cloud-hosting.json", host)

private = load("private-fallback.json")
private.update({
    "state": review["status"], "actual_model_requests": 9,
    "actual_ckm_azure_resources_created": [item["id"] for item in r["azure"]["created_resources"]],
    "actual_private_endpoints_created": [item["id"] for item in pes],
    "actual_data_paas_created": [output["value"] for output in load("data-deployment.json")["outputs"].values()],
    "current_cost": cost,
    "cost_status": "Current approved1.50/hour limit; deployed worst-case reference1.479765 before separate consumption/shared allocation, not a historical0.85 approval gate.",
})
for target in private["private_endpoint_targets"]:
    if target["group_ids"] != ["queue"]:
        target["state"] = "CREATED_APPROVED_PRIVATE_DATA_ACCESS_VERIFIED"
private["target_notes"][0] = "All four core targets and PEs now exist; Queue is still deferred. Exact current inventory is in result.json."
private["proposed_runtime"]["remaining_gates"] = [item["evidence"] for item in r["blockers"]]
private["proposed_runtime"]["identity"] = "Own id-ptu-conversation: AcrPull, OpenAI User, Storage Blob Data Contributor, Search Service Contributor and Search Index Data Contributor on approved scopes; contained SQL reader/writer/ddl_admin, no server-admin."
private["proposed_runtime"]["configuration_status"] = "Original routes were evaluated with private endpoints in a short-lived process. Serving API still has endpoints unset; this is not full live browser deployment."
save("private-fallback.json", private)

pricing = load("pricing.json")
pricing["current_cost"] = cost
pricing["current_cloud_component_cost"].update({"phase": "native_private_workflow_evaluated_apps_paused_sql_online_autopause60", "actual_reported_replicas_at_final_check": 0, "evidence": "evidence/conversation/data-workflow-review.json"})
pricing["current_cloud_component_cost"]["caveat"] = "Current four-PE/Basic Search/serverless SQL costs are in current_cost. SQL still Online at final readback; the old0.85 review limit is superseded by1.50."
pricing["actual_separate_infrastructure_reference"]["scope"] = "Historical summary-only phase before SQL/Search/Blob creation; use current_cost for final footprint."
pricing["actual_native_summary_model_reference"]["scope"] = "Requests1-7 only; cumulative9-request reference is in current_cost."
pricing["full_private_lower_bound_review"].update({"usd_per_hour": 1.4797652055, "fixed_active_review_limit": 1.5, "within_limit": True, "assumption": "Actual approved max2 SQL, Basic Search,32GB allowance,4PEs,both ACA replicas; separate consumption/shared allocation excluded", "additional_approval_and_cost_review_needed": "Not for this deployed envelope. A different Standard Agent topology is separate."})
save("pricing.json", pricing)
plan = load("data-workflow-plan.json")
plan.update({"status": review["status"], "actual_model_requests_cumulative": 9, "actual_additional_model_requests": 2, "remaining_hard_budget": 3, "result": "evidence/conversation/data-workflow-review.json", "sql_identity_correction": review["sql_identity_correction"]})
save("data-workflow-plan.json", plan)
print(json.dumps({"requests": 9, "input_tokens": prompt, "output_tokens": completion, "total_tokens": prompt + completion, "model_retail_reference_usd": cost["cumulative_model_token_reference_usd"], "remote_build_reference_usd": cost["all_remote_builds_reference_usd"], "all12_revisions_paused": True, "sql_state": sql["database"]["status"], "quality_failures": 4}))
