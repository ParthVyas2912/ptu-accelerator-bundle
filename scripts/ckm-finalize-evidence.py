"""Reconcile observed component evidence with source-verified fallback behavior."""
import importlib.metadata
import hashlib
import json
from pathlib import Path
import sys
import time
from datetime import datetime, timezone

bundle = Path(__file__).resolve().parents[1]
directory = bundle / "evidence/conversation"
component_path = directory / "component-results.json"
component = json.loads(component_path.read_text(encoding="utf-8"))
for case in component["tests"]:
    if case["id"] in ("cross-call-citations", "repeated-theme", "ambiguous-uncertainty"):
        case["status"] = "blocked"
        case["root_cause"] = "Original API log: AGENT_NAME_CHAT is not configured; Foundry invocation never started."
    if case["id"] == "insights-dashboard":
        # Preserve the observed HTTP response and timing; correct the overly broad
        # initial predicate after confirming no configured model/SQL and the
        # original analytics-engine fallback.
        case["status"] = "blocked"
        case["limitation"] = (
            "HTTP 200 returns native fallback analytics: 3 sampled records / 1 source. "
            "No configured model or SQL; model-planned SQL workflow is not established."
        )
    if case["id"] == "upload-denied-anonymous":
        case["limitation"] = (
            "Original local sample-user fallback and User.best_role confer contributor "
            "when roles are absent. This probe's 403 expectation failed: actual 200. "
            "Not a public authenticated deployment; loopback-only is mandatory."
        )
component["assessment_note"] = "HTTP outcomes/timings preserved; fallback dashboard is not counted as full model/SQL success."
component_path.write_text(json.dumps(component, indent=2), encoding="utf-8")
manifest_path = directory / "result.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
tests = {test["id"]: test for test in manifest["tests"]}
tests.update({test["id"]: test for test in component["tests"]})
tests["python-dependency-check"] = {
    "id": "python-dependency-check", "classification": "build",
    "expected": "Pinned backend requirements install and pip check reports no conflicts",
    "actual": "Exact requirements installed; No broken requirements found.", "status": "pass",
}
tests["stock-frontend-install"] = {
    "id": "stock-frontend-install", "classification": "build",
    "expected": "npm ci using original lockfile/mirror completes",
    "actual": "Exit 1: mirror package download 403 after signed redirect expired; OneDrive EPERM cleanup warnings. Raw signed URL not retained in report.",
    "status": "fail",
}
tests["isolated-frontend-initial-install"] = {
    "id": "isolated-frontend-initial-install", "classification": "build",
    "expected": "Same locked dependencies install outside OneDrive from public npm",
    "actual": "Exit 1: ERR_SSL_SSL/TLS_ALERT_HANDSHAKE_FAILURE for public he@1.2.0 tarball; TLS verification was not disabled",
    "status": "fail",
}
tests["isolated-frontend-tls12-install"] = {
    "id": "isolated-frontend-tls12-install", "classification": "build",
    "expected": "Bounded TLS 1.2 retry with normal certificate verification installs same locked packages",
    "actual": "Added 1437 packages in 6m; original react-scripts build then started",
    "status": "pass",
}
tests["native-fallback-analytics"] = {
    "id": "native-fallback-analytics", "classification": "component",
    "expected": "Deterministic local chart data counts three records and one source",
    "actual": {"sampled_records": 3, "source_count": 1, "headline": "Unified Knowledge Insights"},
    "status": "pass", "observation_from": "insights-dashboard",
}
manifest["tests"] = list(tests.values())
manifest["local"]["isolated_frontend"] = str(Path.home() / "AppData/Local/ptu-eval/conversation/frontend")
manifest["local"]["frontend_adapter"] = {
    "source_copy": "git archive HEAD:src/app",
    "changed": "1438 public tarball URLs and registry mirror in isolated build copy only",
    "unchanged": "All locked package versions, integrity hashes and application source logic",
}
manifest["python_environment"] = {
    "selected_versions": {
        name: importlib.metadata.version(name)
        for name in ["fastapi", "uvicorn", "openai", "azure-ai-projects", "azure-ai-agents",
                     "agent-framework-core", "agent-framework-foundry", "agent-framework-openai",
                     "azure-identity", "azure-search-documents", "pyodbc"]
    },
    "tls_workaround": "pip --use-deprecated=legacy-certs; certificate verification retained; no --trusted-host/verify=false",
}
for resource in manifest["required_infrastructure"]["resources"]:
    if resource["type"] == "Azure OpenAI embeddings":
        resource["dimensions"] = 1536
manifest["local"]["source_integrity_verification"] = {
    "original_frontend_source_public_files_compared": 38,
    "source_changes": [],
    "locked_versions_and_integrities_identical": True,
}
manifest["traffic"]["instrumented_local_http_requests"] = [
    {"sequence": index + 1, "test": case["id"], "status": case["http_status"], "elapsed_ms": case["elapsed_ms"]}
    for index, case in enumerate(case for case in component["tests"] if case.get("http_status") is not None)
]
manifest["traffic"]["local_http_scope"] = "Instrumented component tests only; excludes readiness, later health verification and browser/static requests."
if len(sys.argv) == 2:
    import httpx

    frontend_pid = int(sys.argv[1])
    with httpx.Client(timeout=10, trust_env=False) as client:
        started = time.perf_counter()
        response = client.get("http://127.0.0.1:5115/")
        elapsed = round((time.perf_counter() - started) * 1000, 3)
        preflight = client.options("http://127.0.0.1:8115/api/ingestion/upload/json", headers={
            "Origin": "http://127.0.0.1:5115",
            "Access-Control-Request-Method": "POST",
        })
    frontend = Path.home() / "AppData/Local/ptu-eval/conversation/frontend"
    index_hash = hashlib.sha256((frontend / "build/index.html").read_bytes()).hexdigest()
    tests["frontend-production-build"] = {
        "id": "frontend-production-build", "classification": "build", "status": "pass",
        "expected": "Original react-scripts optimized production build succeeds",
        "actual": "Compiled successfully; exit 0",
        "index_sha256": index_hash,
    }
    tests["frontend-http"] = {
        "id": "frontend-http", "classification": "ui_only_health",
        "expected": "HTTP 200 from original compiled React app on loopback port 5115",
        "actual": {"http_status": response.status_code, "root_mount": 'id="root"' in response.text},
        "elapsed_ms": elapsed,
        "status": "pass" if response.status_code == 200 and 'id="root"' in response.text else "fail",
        "limitation": "Not a browser interaction or model workflow test",
    }
    tests["loopback-cors"] = {
        "id": "loopback-cors", "classification": "component",
        "expected": "Backend CORS permits the configured local frontend origin",
        "actual": {"http_status": preflight.status_code,
                   "allow_origin": preflight.headers.get("access-control-allow-origin")},
        "status": "pass" if preflight.headers.get("access-control-allow-origin") == "http://127.0.0.1:5115" else "fail",
    }
    manifest["tests"] = list(tests.values())
    manifest["status"] = "original_local_ui_and_api_running_component_only_full_cloud_deployment_blocked"
    manifest["local"]["frontend_endpoint"] = "http://127.0.0.1:5115"
    manifest["local"]["running_processes"] = [
        p for p in manifest["local"]["running_processes"] if p.get("role") != "frontend"
    ] + [{"role": "frontend", "pid": frontend_pid, "shell_id": "ckm-ui", "attached": True}]
    manifest["local"]["listeners_verified"] = {
        "127.0.0.1:8115": component["backend_pid"],
        "127.0.0.1:5115": frontend_pid,
    }
manifest["generated_at"] = datetime.now(timezone.utc).isoformat()
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"status": manifest["status"], "test_count": len(tests), "model_requests": 0, "backend_pid": component["backend_pid"]}))
