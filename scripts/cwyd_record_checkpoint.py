"""Reconcile observed CWYD evidence after the parent-authorized RBAC retest."""
import json
from pathlib import Path

B = Path(r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\projects\PTU accelerator Bundle")
E = B / "evidence" / "cwyd"
read = lambda path: json.loads(path.read_text(encoding="utf-8"))
result = read(E / "result.json")
calls = read(E / "model-calls.json")
assert len(calls) == 10, "Review new model activity before recording this checkpoint"
documents = read(E / "documents.json")
assert documents["actual"]["total"] == 5
ingestions = sorted([read(p) for p in E.glob("ingestion-*.json")],
                    key=lambda r: r["started_epoch"])
latest = {}
for ingestion in ingestions:
    latest[ingestion["filename"]] = ingestion
assert len(latest) == 5 and all(i["status"] == "indexed" for i in latest.values())

result["status"] = "five_document_ingestion_verified_chat_waiting_budget_authorization"
result["full_app_proven"] = False
result["indexed_documents"] = documents["actual"]
result["ingestion_history"] = ingestions
result["successful_ingestion_latest"] = list(latest.values())
for process in result["processes"]:
    if process["service"] == "backend":
        process.update(pid=26812, shell_id="cwyd-backend-4", state="running_health_http_200")
    elif process["service"] == "queue_worker":
        process.update(pid=3368, shell_id="cwyd-worker-3", state="ready_five_policies_indexed")
for test in result["functional_tests"]:
    if test["name"] == "api_health":
        test.update(latency_ms=read(E / "health.json")["latency_ms"])
    elif test["name"] == "index_listing":
        test.update(actual=documents["actual"], verdict="PASS_FIVE_INDEXED_DOCUMENTS")
    elif test["name"] == "travel_policy_upload":
        receipt = read(E / "upload-ptu-cwyd-travel.json")
        test.update(actual=receipt["actual"], latency_ms=receipt["latency_ms"], verdict="PASS")
    elif test["name"] == "travel_policy_ingestion":
        test.update(actual=latest["ptu-cwyd-travel.txt"],
                    latency_ms=latest["ptu-cwyd-travel.txt"]["latency_ms"], verdict="PASS_AFTER_REMEDIATION")
    elif test["name"] == "actual_chat_api":
        test["name"] = "initial_chat_before_endpoint_correction"
        test["verdict"] = "HISTORICAL_FAILURE_NEW_CONFIGURATION_NOT_YET_TESTED"
    elif test["name"] in {"five_factual_answers_and_citations", "absent_answer",
                          "cross_document_comparison", "contradictory_update"}:
        test["verdict"] = "NOT_RUN_APPROVED_MODEL_BUDGET_INSUFFICIENT"
result["functional_tests"].append({
    "name": "five_document_ingestion",
    "expected": "five independently uploaded policies parsed embedded and indexed",
    "actual": list(latest.values()),
    "verdict": "PASS_REAL_APP_INGESTION",
})
result["blockers"] = [
    "Only two attempts remain under the approved total12 cap; the first grouped chat can require three including the upstream capability probe.",
    "Grounded chat citations absent-answer comparison and contradictory replacement remain unproven, not inferred from successful ingestion.",
]
result["required_unblock"].update(
    role_request_status="Parent assignment executed and account OpenAI endpoint embedding access verified",
    parent_assignment_performed=True,
    role_assignment_id="4df8a697-fc79-448a-8f0f-54f90020f5d3",
    principal_id="87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed",
)
result["evaluation_budget_request"] = {
    "approved_total": 12, "used": 10, "requested_total": 18, "approved": False,
    "planned_additional_calls_without_retries": 6, "extra_retry_allowance_requested": 2,
    "purpose": "one grouped factual/absence/comparison chat then one contradictory replacement and follow-up chat",
    "load_test": False,
}
result["account_embedding_endpoint_correction"] = {
    "enabled_by_runtime_environment": "CWYD_USE_ACCOUNT_OPENAI_ENDPOINT=true",
    "original_account_endpoint_host": "edcfoundryhack01.services.ai.azure.com",
    "successful_account_endpoint_host": "edcfoundryhack01.openai.azure.com",
    "project_chat_endpoint_unchanged": True,
    "authentication": "same AzureCliCredential and https://ai.azure.com/.default bearer provider",
    "changes_azure_authentication_or_resource_configuration": False,
    "implementation": "documented SDK get_openai_client base_url override in isolated launcher; no repository source change",
    "evidence": "model attempt4 original route401; attempts5,6,8,9,10 account OpenAI route200",
    "causality_caveat": "Different outcomes do not isolate endpoint behavior from possible concurrent RBAC propagation.",
    "reference": "https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/managed-identity",
}
for feature in result["per_feature_ptu_dependence"]:
    if feature["feature"] == "ingestion embeddings":
        feature["status"] = "five live successful Standard embedding calls;352 reported tokens"
    elif feature["feature"] == "query embeddings":
        feature["status"] = "updated endpoint configured; post-correction chat not yet run"
result["commands"].append("$env:CWYD_USE_ACCOUNT_OPENAI_ENDPOINT='true'; python B\\scripts\\cwyd_runtime.py <backend|worker>")
(E / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

proposal = read(E / "infrastructure-proposal.json")
proposal["proposal_status"] = "zero_new_resources; parent_RBAC_done; model_attempt_ceiling_exception_requested"
proposal["authorization_needed"].update(
    operation="Parent performed additive role assignment; no duplicate by CWYD",
    principal="87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed",
    assignment_id="4df8a697-fc79-448a-8f0f-54f90020f5d3",
    status="completed and embedding access verified using account OpenAI endpoint",
)
proposal["model_attempts_used"] = 10
proposal["model_attempts_remaining"] = 2
proposal["evaluation_budget_request"] = result["evaluation_budget_request"]
for service in proposal["local_services"]:
    if service.get("pid") == 30016:
        service["pid"] = 26812
    elif service.get("pid") == 6880:
        service["pid"] = 3368
(E / "infrastructure-proposal.json").write_text(json.dumps(proposal, indent=2), encoding="utf-8")
print(json.dumps({"status": result["status"], "model_attempts": len(calls),
                  "indexed_policies": len(latest), "reported_embedding_tokens": 352,
                  "requested_total_attempts": 18}))
