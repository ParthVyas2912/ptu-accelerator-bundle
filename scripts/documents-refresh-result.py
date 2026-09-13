"""Merge current, nonsecret DKM cloud evidence into the required summary."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
folder = root / "evidence/documents"
if (folder / "retry-evaluation-final.json").exists():
    raise SystemExit("This helper is historical. Use documents-finalize.py; refusing to overwrite newer verified evidence.")
path = folder / "result.json"
r = json.loads(path.read_text(encoding="utf-8-sig"))
c = json.loads((folder / "cloud-functional-result.json").read_text(encoding="utf-8"))
for key in ("approved_short_test", "shared_preflight_update"):
    if key in r:
        r.setdefault("historical_" + key, r.pop(key))
r.setdefault("historical_tests", r.get("tests", []))
r.setdefault("historical_cost_details", r.get("cost", {}))
r["status"] = "CORE_INGESTION_VERIFIED_PAUSED_FULL_UI_AND_RETRY_CONTROL_GATED"
r["finalized"] = False
r["current_phase_evidence"] = "evidence/documents/cloud-functional-result.json"
r["repository"]["tracked_source_modified"] = True
r["repository"]["source_deviation"] = (
    "Approved AKS worker-SKU parameterization plus narrow Docker-context exclusions "
    "for dotenv/Azure credentials. Original Dockerfiles and application business logic unchanged. "
    "Approved ACA hosting adapter lives in the bundle."
)
prefix = "/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/"
current = [
    {"id": prefix + "accel-dkm-20260911/providers/Microsoft.App/containerApps/" + s["name"],
     "name": s["name"], "type": "Microsoft.App/containerApps", "location": "eastus2"}
    for s in c["hosting"]["services"]
] + [
    {"id": prefix + "rg-ptu-bundle-platform/providers/Microsoft.Network/privateEndpoints/" + p["pe"],
     "name": p["pe"], "type": "Microsoft.Network/privateEndpoints", "location": "eastus2",
     "creation": "Parent-approved guarded PE helper"}
    for p in c["private_dns_verified_from_original_backend_container"]
]
existing_names = {x.get("name") for x in r["azure"]["created"]}
r["azure"]["created"] += [x for x in current if x["name"] not in existing_names]
r["azure"]["reused"] = [
    {"id": c["hosting"]["shared_environment_id"], "purpose": "Approved shared Consumption ACA host"},
    {"id": prefix + "rg-ptu-bundle-platform/providers/Microsoft.ContainerRegistry/registries/acrptubundle7d804f70",
     "purpose": "Approved isolated dkm/* image repositories in shared Basic ACR"},
    {"id": prefix + "rg-ptu-bundle-platform/providers/Microsoft.Network/virtualNetworks/vnet-ptu-bundle",
     "purpose": "Approved shared private-endpoint subnet and linked private DNS"}
]
r["azure"]["reuse_decision"] = "No Foundry/Search/PaaS retrofit. Parent-approved shared hosting/networking reuse only."
r["azure"]["app_created_cosmos"] = {"database": "DPS", "collection": "Documents", "throughput": 400}
for item in r["azure"]["required"]:
    if item["service"] == "Cosmos DB":
        item["throughput"] = "Observed default database400RU/s plus app-created DPS/Documents400RU/s:800 total manual."
r["cost"] = c["cost_usd_hour"] | {
    "currency": "USD", "actual_invoice_cost": None,
    "invoice_caveat": "No invoice queried; resource-based retail estimates only."
}
r["runtime"].update({
    "running_full_app": False,
    "core_ingestion_verified": True,
    "full_browser_e2e_verified": False,
    "cloud_services": c["hosting"]["services"],
    "pause_runbook": "reports/documents-cloud-runbook.md",
    "controller": "scripts/Set-DocumentsRuntime.ps1",
    "status": c["current_runtime_action"],
    "restart_verification": c["restart_verification"]
})
r["tests"] = c["tests"]
r["inference_telemetry"].update({
    "live_model_requests": 4, "retries": 0,
    "search_data_plane_requests": None,
    "search_caveat": "Real ingestion/search persistence occurred; exact Search request count was not instrumented.",
    "input_tokens": 492, "output_tokens": 1513, "total_tokens": 2005,
    "model_latency_ms": c["model_telemetry"]["operation_average_latency_ms"],
    "model_latency_caveat": "Provider aggregate operation averages, not individual request timings.",
    "model_http_statuses": [200, 200, 200, 200],
    "per_deployment": c["model_telemetry"]["by_deployment"],
    "model_errors": [],
    "ptu_claim": "GlobalStandard traffic only; PTU utilization/capacity not measured or purchased."
})
r["synthetic_corpus"]["uploaded"] = 1
r["synthetic_corpus"]["indexed"] = 1
r["functional_summary"] = {
    "requested_mixed_documents": 10, "completed_ingestions": 1,
    "verified": ["private DNS", "Kernel Memory health", "Mongo-backed API", "genuine ingestion pipeline",
                 "person/place/type metadata", "positive/negative place filters"],
    "quality_failure": "Summary contains unsupported greeting preface.",
    "full_app_e2e_passed": False,
    "blocked_or_not_run": ["public browser path", "document-vs-corpus QA", "two-document comparison",
                           "chart/table/handwriting-style cases", "matched fairness fixtures"],
    "accuracy": None
}
r["local_execution"].update({
    "isolated_builder": "dkm-eval;4GiB/two CPUs; stopped after builds",
    "browser_tooling": "Isolated Playwright1.62 with installed Edge",
    "application_business_logic_modified": False,
    "service_keys_fetched_or_saved": False,
    "identity_only_access": True
})
r["recommendation"] = (
    "Preserve all resources. Parent review needed for unexpected frontend403 with matching client allowlist, "
    "and a narrow SDK retry-control change before further paid tests. Four of twelve model attempts used; "
    "stock next-ingestion bound13 and full-backend-chat bound9 exceed the remaining8. "
    "Core ingestion is proven, full application/browser E2E is not."
)
path.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
manifest_path = root / "test-data/documents/manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for record in manifest["records"]:
    if record["filename"] == c["ingestion"]["file"]:
        record.update(uploaded=True, indexed=True, document_id=c["ingestion"]["document_id"],
                      imported_time_utc=c["ingestion"]["imported_time_utc"])
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print("Updated DKM summary and first synthetic corpus record; no credentials read or written.")
