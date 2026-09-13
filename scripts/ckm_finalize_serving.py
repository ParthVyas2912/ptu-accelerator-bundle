"""Reconcile the zero-inference durable serving deployment without touching raw results."""
from datetime import datetime
import hashlib
import json
from pathlib import Path

folder = Path(__file__).resolve().parents[1] / "evidence" / "conversation"


def load(name):
    return json.loads((folder / name).read_text(encoding="utf-8-sig"))


def save(name, value):
    (folder / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


http = load("serving-http-attempt-1.json")
api = load("serving-api-final-state.json")
ui = load("serving-ui-final-state.json")
sql = load("serving-sql-final-state.json")
config = load("serving-native-config.json")
build = load("serving-build.json")
budget = load("budget-handoff.json")
revisions = api["revisions"] + ui["revisions"]
assert http["status"] == "passed" and len(http["tests"]) == 15
assert all(test["status"] == "passed" for test in http["tests"])
assert http["model_requests"] == 0 and http["serving_pid"] == 1 and http["probe_pid"] != 1
assert http["last_response_guard_headers"]["x-ckm-outbound-denied"] == "0"
assert len(revisions) == 14 and all(not revision["active"] and revision["replicas"] == 0 for revision in revisions)
assert api["native_configuration"] == config
assert not api["app"]["ingress"]["external"] and api["app"]["scale"]["minReplicas"] == 0
assert api["app"]["scale"]["maxReplicas"] == 1
assert ui["app"]["ingress"]["ipSecurityRestrictions"][0]["ipAddressRange"] == "174.112.74.34/32"
assert api["app"]["image"].endswith(build["images"][0]["digest"])
assert budget["current_model_request_cap"] == budget["actual_model_attempts_used"] == 9
assert budget["remaining_ckm_model_request_allowance"] == budget["reserved_model_requests"] == 0
seconds = (datetime.fromisoformat(build["finish"]) - datetime.fromisoformat(build["start"])).total_seconds()
build_cost = seconds * build["cpu"] * 0.0001
verified = max(api["checked_at"], ui["checked_at"], sql["checked_at"])
raw_hashes = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
              for name in ["summary-results.json", "data-workflow-results.json", "serving-http-attempt-1.json"]}
review = {
    "status": "durable_native_read_only_serving_verified_paused",
    "configure_read_attempts_used": 1, "configure_read_attempt_limit": 2,
    "additional_model_attempts": 0, "cumulative_model_attempts": 9, "closed_model_cap": 9,
    "native_http_tests": http["tests"], "native_http_test_count": 15,
    "verification_transport": http["transport"], "verified_serving_pid": http["serving_pid"],
    "verification_probe_pid": http["probe_pid"], "http_started_at": http["started_at"],
    "http_finished_at": http["finished_at"], "native_configuration": config,
    "durable_configuration_read_back_after_scale_update": True,
    "serving_api_model_and_data_endpoints_remain_unset": False,
    "inference_armed": False, "automatic_processing_enabled": False, "queue_workers_enabled": False,
    "explicit_http_disarm": "All model/mutation routes503 before native execution; no heuristic AI success fallback.",
    "transport_disarm": "Sync/async httpx, requests and aiohttp can only dispatch read operations to owned Blob/Search or use the managed identity token endpoint. Other outbound HTTP is blocked.",
    "adaptation": "Original native FastAPI app/routes; dedicated serving entrypoint replaces queue-only lifespan and adds immutable read-only/transport gates. No generic data/Q&A handlers.",
    "image": api["app"]["image"], "original_api_base_digest": "sha256:baa11a820f821532ade2129fe5dd628764b9053778b3ef6d35e89fa2345ee8f8",
    "legacy_live_evaluators_in_current_image": False,
    "build": build, "build_elapsed_seconds": seconds, "build_retail_reference_usd": build_cost,
    "build_submission_note": "One local submission could not locate relative Dockerfile and created no run; corrected context produced successful remote runch10.",
    "new_paas_resources_models_roles_or_network_changes": False,
    "all_cloud_revisions_inactive": True, "cloud_replicas": 0, "retained_revisions": revisions,
    "pause_session": "ckm-serving-final-pause", "pause_exit_code": 0,
    "configure_session": "ckm-serving-config1", "http_session": "ckm-serving-http1",
    "sql": sql, "last_possible_sql_access_upper_bound": verified,
    "sql_access_caveat": "Last observed connection is from the measured serving PID. The replacement min0 revision may initialize before shutdown; final all-zero snapshot bounds any later own-process activity. No claim of observed SQL pause.",
    "full_application_deployed": False,
    "remaining_limitations": ["Hosted Explore/private Basic Agent incompatibility", "Original KPI/anonymization/file-insights quality defects", "Public browser403 not retested", "Blob/Search bindings persisted; this new pass reads SQL, not fresh Blob/Search authorization"],
    "raw_evidence_sha256": raw_hashes, "verified_at": verified,
}
save("serving-results.json", review)

budget["current_cloud_state"].update({
    "control_plane_read_sessions": ["1033", "1031", "1032"],
    "checked_at": verified, "api_retained_revisions": len(api["revisions"]),
    "ui_retained_revisions": len(ui["revisions"]), "active_revisions": 0, "replicas": 0,
    "sql_status": sql["database"]["status"], "sql_pause_observed": sql["sql_pause_observed"],
    "durable_native_serving_verified": True, "serving_evidence": "evidence/conversation/serving-results.json",
})
budget["additional_acceptance_limitations"] = [
    limitation for limitation in budget["additional_acceptance_limitations"]
    if not limitation.startswith("Serving API model/data endpoints remain unset")
]
save("budget-handoff.json", budget)

r = load("result.json")
assert r["traffic"]["live_model_requests"] == 9 and r["traffic"]["total_tokens_returned"] == 8247
assert len(r["native_data_workflow_quality_tests"]) == 6
r.update({"status": review["status"], "generated_at": verified, "native_serving": review,
          "native_serving_evidence": "evidence/conversation/serving-results.json", "budget_handoff": budget})
r["current_decision"].update({
    "controlling_parent_update": "2026-09-12T05:10:48.032Z",
    "cloud_hosting_phase": review["status"], "pause_session": review["pause_session"],
    "pause_exit_code": 0, "model_request_cap": 9, "remaining_allowance": 0,
    "final_cloud_verified_at": verified, "cloud_reported_replicas": 0,
    "rollout_observation": "One serving configure/read attempt;15 native HTTP checks passed. Scale restored min0/max1; all14 retained revisions inactive/0.",
})
r["bounded_native_summary_pass"]["historical_phase_note"] = "Serving endpoints were unset during that earlier phase; current durable serving state is in native_serving."
if "serving_api_model_endpoints_still_unset" in r["bounded_native_summary_pass"]:
    r["bounded_native_summary_pass"]["serving_api_model_endpoints_unset_during_summary_phase"] = r["bounded_native_summary_pass"].pop("serving_api_model_endpoints_still_unset")
r["azure"]["final_configuration_evidence"] = list(dict.fromkeys(r["azure"]["final_configuration_evidence"] + [
    "evidence/conversation/serving-api-final-state.json", "evidence/conversation/serving-ui-final-state.json",
    "evidence/conversation/serving-sql-final-state.json",
]))
for resource in r["azure"]["created_resources"]:
    if resource["id"].lower().endswith("/containerapps/ca-ptu-conversation-api"):
        resource.update({"image": api["app"]["image"], "serving_phase": review["status"], "replicas": 0})
cost = r["current_cost"]
cost.update({
    "all_remote_builds_reference_usd": load("data-workflow-review.json")["cost"]["all_remote_builds_reference_usd"] + build_cost,
    "serving_remote_build_reference_usd": build_cost,
    "actual_sql_state": sql["database"]["status"], "sql_pause_observed": sql["sql_pause_observed"],
    "last_data_connection_check": sql["last_observed_serving_sql_connection_at"],
    "last_possible_sql_access_upper_bound": verified,
})
save("result.json", r)

cloud = load("cloud-hosting.json")
cloud.update({
    "phase": review["status"], "container_apps_state": review["status"], "final_verified_at": verified,
    "current_api_image": api["app"]["image"], "final_revisions": revisions,
    "rollout_observation": r["current_decision"]["rollout_observation"],
    "serving_app_model_endpoints_still_unset": False, "serving_inference_armed": False,
    "serving_native_configuration": config, "serving_http_tests": http["tests"],
    "native_serving_evidence": "evidence/conversation/serving-results.json",
    "pause_session": review["pause_session"], "pause_exit_code": 0,
    "model_attempt_cap": 9, "model_attempts": 9, "current_cost": cost,
    "historical_component_tests_note": "The tests array retains initial component-only checks. Current health/data/read-only checks are in serving_http_tests.",
})
cloud["registry_manifests"] = [item for item in cloud["registry_manifests"] if item.get("build_run") != "ch10"] + [
    {"image": "conversation/api:8a00aa5-serving-ro1", "digest": build["images"][0]["digest"], "build_run": "ch10"}
]
cloud["hosting_budget"]["not_included"] = [
    "Requests/shared registry/logging/egress", "Four retained PEs and their data processing",
    "Retained SQL/Search/Blob charges", "Unimplemented Standard Agent topology",
]
save("cloud-hosting.json", cloud)
private = load("private-fallback.json")
private.update({"model_attempt_cap": 9, "current_cost": cost,
                "native_serving_evidence": "evidence/conversation/serving-results.json"})
private["proposed_runtime"]["configuration_status"] = "Now durably bound in the serving API and verified over real HTTP; inference/automatic/queue processing disarmed. Not full hosted Explore/browser deployment."
save("private-fallback.json", private)
pricing = load("pricing.json")
pricing["current_serving_cost"] = cost
save("pricing.json", pricing)
validation = load("final-validation.json")
validation.update({
    "paused_revisions": len(revisions), "native_serving_http_checks": 15,
    "durable_native_configuration_verified": True, "additional_model_requests": 0,
    "closed_model_request_cap": 9, "serving_verified_at": verified,
})
save("final-validation.json", validation)
print(json.dumps({"native_http_checks": 15, "additional_model_attempts": 0, "cumulative_attempts": 9,
                  "closed_cap": 9, "retained_paused_revisions": len(revisions),
                  "sql_status": sql["database"]["status"], "build_reference_usd": build_cost}))
