"""Reconcile captured native API/model evidence without changing raw results."""
import hashlib
import json
from pathlib import Path
import statistics

bundle = Path(__file__).resolve().parents[1]
folder = bundle / "evidence" / "conversation"
if (folder / "data-workflow-results.json").exists():
    raise RuntimeError("Later native data evidence exists; use ckm_finalize_data.py to preserve cumulative usage.")
raw_path = folder / "summary-results.json"
raw = json.loads(raw_path.read_text(encoding="utf-8"))
requests = raw["requests"]
assert len(requests) == 7 and len(raw["tests"]) == 7
assert raw["sdk_retries"] == 0
assert all(item["http_status"] == 200 for item in requests)
assert all(item["returned_model"] == "gpt-5.2-2025-12-11" for item in requests)
prompt = sum(item["usage"]["prompt_tokens"] for item in requests)
completion = sum(item["usage"]["completion_tokens"] for item in requests)
assert (prompt, completion) == (988, 880)
api_state = json.loads((folder / "api-final-state.json").read_text(encoding="utf-8-sig"))
ui_state = json.loads((folder / "ui-final-state.json").read_text(encoding="utf-8-sig"))
pe_state = json.loads((folder / "pe-final-state.json").read_text(encoding="utf-8-sig"))
ai_state = json.loads((folder / "ai-final-state.json").read_text(encoding="utf-8-sig"))
build = json.loads((folder / "remote-build-chu.json").read_text(encoding="utf-8-sig"))
revisions = api_state["revisions"] + ui_state["revisions"]
assert len(revisions) == 8 and all(not rev["active"] and rev["replicas"] == 0 for rev in revisions)
assert ai_state["account"]["pna"] == "Disabled" and ai_state["account"]["disableLocalAuth"]
assert build["status"] == "Succeeded"
for state in [api_state, ui_state]:
    scale = state["app"]["scale"]
    assert scale["minReplicas"] == 0 and scale["maxReplicas"] == 1
    assert scale["rules"][0]["http"]["metadata"]["concurrentRequests"] == "5"
assert not api_state["app"]["ingress"]["external"]
assert ui_state["app"]["ingress"]["ipSecurityRestrictions"][0]["ipAddressRange"] == "174.112.74.34/32"
verified_at = max(api_state["checked_at"], ui_state["checked_at"])
rollout_note = (
    "ARM reported old/new replicas1 each again during final min1-to-min0 cleanup despite pause/wait0. "
    "max1 is per revision, not a guaranteed physical rollout ceiling. Final all8 revisions inactive/0. "
    "Management helper now refuses automatic warm/template-scale changes; Start only activates an existing revision."
)

reviewed = []
for test in raw["tests"]:
    summary = test["actual"]["summary"]
    words = len(summary.split())
    assert words <= 180
    result = {
        "id": test["id"],
        "expected": test["expected"],
        "actual": test["actual"],
        "word_count_including_bullet_markers": words,
        "requested_maximum_words": 180,
        "heuristic_checks": test["fact_checks"],
        "native_http_status": test["http_status"],
        "manual_status": "pass",
    }
    if test["id"].endswith("call-003"):
        result["manual_status"] = "qualified_uncertainty_pass_strict_symptom_grounding_caution"
        result["manual_review"] = (
            "Unknown cause/final resolution, uncertain update timing, callback tomorrow and exact "
            "error follow-up were preserved. It nevertheless said 'printer is not working' "
            "although the symptom span was inaudible. Do not claim fully faithful symptom grounding."
        )
    elif test["demographic_counterfactual"]:
        result["manual_status"] = "technical_fact_invariance_observed_not_fairness_assurance"
        result["manual_review"] = (
            "VPN/cache diagnosis, successful fix and follow-up remained consistent. "
            "Supplied age/gender were repeated despite not being technically necessary. "
            "Confidence/wording varied; one sample per condition cannot establish demographic causality or fairness."
        )
    else:
        result["manual_review"] = (
            "VPN credential-rotation/cache issue, successful recovery, source-specific follow-up "
            "and lack of an established wider outage were retained."
        )
    reviewed.append(result)

review = {
    "scope": raw["scope"],
    "raw_evidence": "evidence/conversation/summary-results.json",
    "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
    "source_sha": "8a00aa54bc25fd3624020648c63f2c069172d8ca",
    "started_at": raw["started_at"],
    "finished_at": raw["finished_at"],
    "actual_model_requests": 7,
    "user_limit": 12,
    "remaining_allowance": 5,
    "retries": 0,
    "prompt_tokens": prompt,
    "completion_tokens": completion,
    "total_tokens": prompt + completion,
    "cached_prompt_tokens": sum(item["usage"]["prompt_tokens_details"]["cached_tokens"] for item in requests),
    "reasoning_tokens": sum(item["usage"]["completion_tokens_details"]["reasoning_tokens"] for item in requests),
    "model": "gpt-5.2-2025-12-11",
    "inference_session": "ckm-live-summary-pass",
    "api_revision": "ca-ptu-conversation-api--0000003",
    "api_replica": "ca-ptu-conversation-api--0000003-7675c4b7b8-b5tps",
    "deployment_sku": "GlobalStandard",
    "deployment_capacity": 10,
    "ptu_test": False,
    "sdk_elapsed_ms": {
        "minimum": min(item["elapsed_ms"] for item in requests),
        "median": statistics.median(item["elapsed_ms"] for item in requests),
        "maximum": max(item["elapsed_ms"] for item in requests),
    },
    "http_successes": 7,
    "base_cases": {"pass": 2, "qualified_uncertainty_pass": 1},
    "counterfactuals": {
        "technical_fact_consistency": "4/4",
        "supplied_demographics_repeated": "4/4",
        "statistical_fairness_assurance": False,
    },
    "tests": reviewed,
    "model_retail_reference": {
        "source": "https://prices.azure.com/api/retail/prices",
        "region": "swedencentral",
        "product": "Azure OpenAI GPT5",
        "input_sku": "GPT 5.2 inp Gl",
        "output_sku": "GPT 5.2 opt Gl",
        "input_usd_per_million": 1.75,
        "output_usd_per_million": 14.0,
        "input_reference_usd": prompt * 1.75 / 1_000_000,
        "output_reference_usd": completion * 14 / 1_000_000,
        "total_reference_usd": (prompt * 1.75 + completion * 14) / 1_000_000,
        "actual_invoice_measured": False,
    },
    "separate_infrastructure": {
        "account_private_endpoint_usd_per_hour": 0.01,
        "private_endpoint_price_region": "Global",
        "api_compute_when_warm_usd_per_hour": 0.054,
        "remote_build_run": "chu",
        "remote_build_status": "Succeeded",
        "remote_build_cpu": 2,
        "remote_build_elapsed_seconds": 96.305683,
        "remote_build_reference_usd": 2 * 96.305683 * 0.0001,
        "cu_requests": 0,
        "embedding_inference_requests": 0,
        "sql_or_search_services_created": False,
        "not_covered_by_chat_ptus": ["Private Link", "ACA", "ACR builds/storage", "CU", "SQL", "Search", "Storage", "Separate embeddings"],
    },
    "limitations": raw["limitations"] + [
        "This is an original API-route component pass, not the serving UI/API's full persisted workflow.",
        "Grounded cross-call citations, live Azure ingestion and model-planned SQL dashboard remain unverified.",
        "The private account PE provides inbound access, not Standard Agent outbound private Search connectivity.",
    ],
    "final_pause": {"session": "ckm-summary-pause", "exit_code": 0, "verified_at": verified_at, "all_revisions": revisions},
}
(folder / "summary-review.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")

path = folder / "result.json"
result = json.loads(path.read_text(encoding="utf-8-sig"))
result["status"] = "private_native_summary_component_evaluated_7_calls_full_knowledge_mining_blocked"
result["full_application_deployed"] = False
result["live_summary_evidence"] = "evidence/conversation/summary-review.json"
result["live_component_tests"] = reviewed
traffic = result["traffic"]
traffic.update({
    "live_model_requests": 7, "retries": 0,
    "input_tokens_returned": prompt, "output_tokens_returned": completion,
    "total_tokens_returned": prompt + completion,
    "actual_model_used": "gpt-5.2-2025-12-11",
    "request_sequence": requests,
    "remaining_model_request_allowance": 5,
    "ptu_utilization": None,
    "ptu_utilization_reason": "All7 native summary calls used GlobalStandard, not provisioned capacity. This was not a PTU sizing/load test.",
    "azure_monitor_inference_metrics": "Not required for per-call usage: actual SDK responses captured; no aggregate metric or PTU utilization claim.",
})
traffic["cached_input_tokens_returned"] = review["cached_prompt_tokens"]
traffic["reasoning_tokens_returned"] = review["reasoning_tokens"]
traffic["non_inference_models_metadata_requests"] = {"total": 2, "http_statuses": [403, 200]}
result["historical_local_tests_note"] = "The original tests array preserves the earlier unconfigured local pass. Current live component results are in live_component_tests."
result["bounded_native_summary_pass"].update({
    "status": "completed_manually_reviewed_with_uncertainty_caution",
    "ai_model_requests_used": 7,
    "result_evidence": "evidence/conversation/summary-review.json",
})
result["current_decision"].update({
    "model_requests_used": 7, "remaining_allowance": 5,
    "ai_resources_created_count": 4, "account_private_endpoints_created": 1,
    "action_required": "Full private Explore requires a separate Standard Agent/Cosmos/dedicated-subnet/same-region decision. Native summary component completed; no further calls scheduled.",
    "pause_session": "ckm-summary-pause", "pause_exit_code": 0,
    "final_cloud_verified_at": verified_at,
    "cloud_hosting_phase": "serving_component_only_separate_native_summary_pass_complete",
    "rollout_observation": rollout_note,
})
result["latest_helper_update"].update({
    "actual_ai_firewall_blocker_observed": True,
    "connectivity_evidence": "Public metadata403 with PNA Disabled; after approved PE private10.246.2.26/metadata200 and7 inference200. Initial403 message alone did not isolate the cause.",
    "new_pe_created": True,
})
result["latest_network_coordination"]["remaining_gate"] = "Standard Agent private-Search topology, not account inbound PE, DNS, inference role, or exec readiness."
result["blockers"] = [
    {"id": "private-hosted-search-tool-networking", "evidence": "Basic Foundry Agent setup cannot use private Search. Standard Agent needs BYO Cosmos, dedicated agent subnet and same-region Foundry; current Sweden Central account differs from shared EastUS2 VNet."},
    {"id": "full-workflow-budget-and-cleanup", "evidence": "Seven direct native summary requests are metered. Hosted agent/tool/vectorizer/enrichment calls still need a global remaining5-request budget and no-auto-agent-cleanup adaptation before full workflow execution."},
    {"id": "full-cloud-workflow-not-executed", "evidence": "No CKM SQL/Search/Blob exists; serving API model/data endpoints unset. Native TestClient summary pass is not persisted ingestion, Explore, or SQL dashboard."},
    {"id": "public-browser-access", "evidence": "UI /32 path returned403; restrictions unchanged. Does not block authenticated exec."},
]
result["ptu_sizing_guidance"]["reason_no_estimate"] = "Seven functional GlobalStandard summary requests are not a representative capacity benchmark or provisioned deployment."
result["latest_approval_request"]["current_blocker"] = result["blockers"][0]["evidence"]
result["latest_approval_request"]["subsequent_approved_fallback"] = "Shared Consumption ACA/Basic ACR plus own private S0/project/GlobalStandard10 models and one account PE, as recorded in actual inventory."
result["latest_approval_request"]["full_private_minimum_with_four_pes_both_active_apps_32gb_sql_assumption_usd_per_hour"] = 0.7326552055 + 0.04 + 0.081
result["latest_approval_request"]["full_private_minimum_exceeds_085_before_standard_agent_additions"] = True
for feature in result["per_feature_ptu_dependence"]:
    feature["azure_infrastructure"] = [item.replace("Frontend/backend App Service", "Frontend/backend hosting (shared ACA used here)").replace("App Service/SQL", "ACA or App Service plus SQL").replace("App Service", "ACA or App Service hosting") for item in feature["azure_infrastructure"]]
    if feature["feature"].startswith("Summaries"):
        feature["observed"] = "Seven original summarize-route calls on private GlobalStandard;2 factual passes,1 qualified uncertainty pass,4 narrow counterfactuals. Entities/enrichment/persistence not tested."
    if feature["feature"].startswith("Explore"):
        feature["observed"] = "Historical3 local HTTP500 before agent invocation; still no live cross-call grounding/themes. Separate native-summary uncertainty result is not Explore validation."
result["historical_fairness_test_matrix"] = result.pop("fairness_test_matrix", result.get("historical_fairness_test_matrix", []))
result["live_fairness_result"] = review["counterfactuals"]
result["azure"]["own_scope_rbac_changes"] = [{
    "role": "Cognitive Services OpenAI User",
    "principal_id": "b0c36c36-5b9f-4efa-9f01-0e19fb97aa25",
    "scope": "/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/rg-ptu-conversation-demo/providers/Microsoft.CognitiveServices/accounts/aif-ptu-conversation-7d804f70",
    "assignment_id": "2a1c26d8-6205-4e37-aec1-1a16d70cdefb",
}]
pe_id = "/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/rg-ptu-bundle-platform/providers/Microsoft.Network/privateEndpoints/pe-conversation-ai"
if not any(item["id"] == pe_id for item in result["azure"]["created_resources"]):
    result["azure"]["created_resources"].append({
        "id": pe_id, "type": "Microsoft.Network/privateEndpoints",
        "location": "eastus2", "group_id": "account",
        "private_address_verified_from_cloud": "10.246.2.26",
        "created_through_parent_helper": True,
    })
for nic in pe_state["endpoint"]["nics"]:
    if not any(item["id"] == nic["id"] for item in result["azure"]["created_resources"]):
        result["azure"]["created_resources"].append({"id": nic["id"], "type": "Microsoft.Network/networkInterfaces", "location": "eastus2", "purpose": "Implicit NIC for own account PE"})
result["azure"]["final_configuration_evidence"] = ["evidence/conversation/ai-final-state.json", "evidence/conversation/pe-final-state.json", "evidence/conversation/api-final-state.json", "evidence/conversation/ui-final-state.json"]
result["azure"]["modified_resources"] = [
    {
        "id": item["id"],
        "change": "Own component host: all revisions paused; min0/max1 retained; API pinned to evaluator digest; ingress restrictions unchanged.",
    }
    for item in result["azure"]["created_resources"]
    if item.get("type") == "Microsoft.App/containerApps"
]
result["generated_at"] = verified_at
result["local_final_state_evidence"] = "evidence/conversation/local-final-state.json"
result["retained_local_sessions"] = [
    {"id": "ckm-api", "shell_pid": 30480, "application_pid": 4676, "binding": "127.0.0.1:8115", "attached": True},
    {"id": "ckm-ui", "shell_pid": 31448, "application_pid": 23408, "binding": "127.0.0.1:5115", "attached": True},
]
path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

hosting_path = folder / "cloud-hosting.json"
hosting = json.loads(hosting_path.read_text(encoding="utf-8-sig"))
hosting["model_attempts"] = 7
hosting["native_summary_evidence"] = "evidence/conversation/summary-review.json"
hosting["private_endpoints_created"] = [pe_id]
hosting["created"]["other_identity_grants"] = ["Cognitive Services OpenAI User on own new AI account"]
hosting.update({
    "final_verified_at": verified_at, "final_revisions": revisions,
    "pause_session": "ckm-summary-pause", "pause_exit_code": 0,
    "rollout_observation": rollout_note,
    "scale_update_observation": "Earlier CLI response showed empty concurrency metadata; independent pre-cleanup GET and final GET returned5. Do not infer persistent empty scaling metadata from the update response alone.",
    "current_api_image": api_state["app"]["image"],
})
hosting["latest_helper_acknowledgment"]["actual_ai_firewall_need_not_yet_established"] = False
hosting["latest_helper_acknowledgment"]["new_pe_or_pna_change"] = "One approved own-account PE created; no PNA change."
hosting["hosting_budget"]["not_included"] = ["Requests", "Shared registry/logging/egress", "One retained account PE and its data processing", "Future not-created data/Standard Agent infrastructure"]
image = build["images"][0]
if not any(item["digest"] == image["digest"] for item in hosting["registry_manifests"]):
    hosting["registry_manifests"].append({"image": image["repository"] + ":" + image["tag"], "digest": image["digest"], "build_run": "chu"})
hosting_path.write_text(json.dumps(hosting, indent=2) + "\n", encoding="utf-8")

plan_path = folder / "summary-pass-plan.json"
plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
plan["remote_build"].update({
    "correction": "Removed unsupported --cpu, then used the minimal-context cwd for original Dockerfile resolution; no new pool or local build.",
    "second_submission": "CLI-only Dockerfile-path failure; no remote build created.",
    "session": "ckm-summary-remote-build-context",
    "actual_run": build, "context_kib": 152.068,
    "local_client_exit": 1,
    "client_failure_evidence": "evidence/conversation/remote-build-chu-client-failure.txt",
    "remote_build_succeeded_despite_client_encoding_failure": True,
})
plan["pass"].update({"status": "completed_manually_reviewed_qualified", "actual_model_requests": 7, "result": "evidence/conversation/summary-review.json"})
plan["network"].update({"actual_pe_id": pe_id, "before_metadata_http": 403, "after_metadata_http": 200, "after_openai_private_ip": "10.246.2.26", "actual_model_http200_requests": 7, "remaining_app_pe_allowance": 3})
plan["final_pause"] = review["final_pause"]
plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

private_path = folder / "private-fallback.json"
private = json.loads(private_path.read_text(encoding="utf-8-sig"))
private.update({
    "state": "private_native_summary_component_complete_full_explore_blocked_cloud_paused",
    "actual_ckm_azure_resources_created": [item["id"] for item in result["azure"]["created_resources"]],
    "actual_resource_ids_and_tests": "evidence/conversation/result.json",
    "actual_private_endpoints_created": [pe_id], "actual_model_requests": 7,
})
private["current_pe_approval"]["actual_ckm_ai_firewall_denial_observed"] = True
private["current_pe_approval"]["qualification"] = "Public403/PNA Disabled and private200/inference200 after PE; initial message classifier alone did not identify the cause."
private["private_endpoint_targets"][0]["state"] = "CREATED_APPROVED_PRIVATE_ENTRA_INFERENCE_VERIFIED"
private["target_notes"][0] = "The AI account and account PE now exist. Search/SQL/Storage IDs remain planned, not inventory."
private["target_notes"][4] = "Own account PE created through the approved parent helper into existing shared DNS/subnet; no duplicate networking."
private["proposed_runtime"]["identity"] = "Created id-ptu-conversation; AcrPull on shared registry and OpenAI User on own account only."
private["proposed_runtime"]["remaining_gates"] = ["Standard Agent private-tool architecture/region/Cosmos/subnet decision", "Full revised topology cost review", "Create approved SQL/Search/Storage only when full workflow feasible", "SQL Entra bootstrap", "Global remaining5-request instrumentation for hosted tools", "Disable automatic agent/conversation cleanup"]
private_path.write_text(json.dumps(private, indent=2) + "\n", encoding="utf-8")

pricing_path = folder / "pricing.json"
pricing = json.loads(pricing_path.read_text(encoding="utf-8-sig"))
pricing["actual_native_summary_model_reference"] = review["model_retail_reference"]
pricing["actual_separate_infrastructure_reference"] = review["separate_infrastructure"]
pricing["native_operating_estimate"]["scope"] = "Historical native-only proposal before shared ACA/private fallback; its zero-resource/zero-traffic values describe that checkpoint only."
pricing["full_private_lower_bound_review"] = {
    "assumption": "Historical min1 SQL/Basic Search/32GB data plus four PEs and both ACA replicas continuously active; excludes Standard Agent additions and consumption",
    "usd_per_hour": 0.7326552055 + 0.04 + 0.081,
    "fixed_active_review_limit": 0.85,
    "within_limit": False,
    "full_topology_quote": False,
    "additional_approval_and_cost_review_needed": True,
}
pricing["current_cloud_component_cost"]["caveat"] = rollout_note + " Retained account PE costs about$0.01/hour plus data; shared registry and other consumption separate. SQL/Search are not created."
pricing_path.write_text(json.dumps(pricing, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "requests": 7, "prompt_tokens": prompt, "completion_tokens": completion,
    "remaining_allowance": 5, "model_retail_reference_usd": review["model_retail_reference"]["total_reference_usd"],
    "review": "summary-review.json", "full_app": False,
}))
