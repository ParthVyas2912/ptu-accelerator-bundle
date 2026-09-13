"""Run the ORIGINAL CKM FastAPI app, loopback-only, with cloud traffic disabled.

No replacement Q&A, mocks, saved secrets, cloud writes, or cleanup.
Seeds three fictional conversations through the original HTTP ingestion route.
The random administrator credential lives only in this process.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import sys
import threading
import time
from datetime import datetime, timezone

BUNDLE = Path(__file__).resolve().parents[1]
REPO = BUNDLE.parents[1] / "repo" / "Conversation-Knowledge-Mining-Solution-Accelerator"
EVIDENCE = BUNDLE / "evidence" / "conversation"
DATA = BUNDLE / "test-data" / "conversation" / "support-conversations.json"
BASE = "http://127.0.0.1:8115"

# Fail closed even when the launching shell inherited another accelerator's config.
for key in (
    "AZURE_OPENAI_ENDPOINT", "AZURE_FOUNDRY_ENDPOINT", "AZURE_AI_AGENT_ENDPOINT",
    "AGENT_NAME_CHAT", "AGENT_NAME_TITLE", "AZURE_SEARCH_ENDPOINT",
    "AZURE_CONTENT_UNDERSTANDING_ENDPOINT", "AZURE_SQL_SERVER",
    "AZURE_STORAGE_ACCOUNT", "AZURE_COSMOS_ENDPOINT", "AZURE_AD_CLIENT_ID",
    "AZURE_AD_TENANT_ID", "AZURE_CLIENT_ID",
):
    os.environ[key] = ""
os.environ["APP_ENV"] = "local"
os.environ["APP_FRONTEND_HOSTNAME"] = "http://127.0.0.1:5115"
os.environ["ENABLE_AUTO_PIPELINE_SELECTION"] = "false"
os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"] = "gpt-5.2"
os.environ["PIPELINES_CONFIG_DIR"] = str(REPO / "src/api/config/use_cases")
os.environ["DATA_DIR"] = str(DATA.parent)
os.environ["ADMIN_API_KEY"] = secrets.token_urlsafe(32)

# Stock Settings reads .env files implicitly. Refuse rather than risk inherited secrets.
os.chdir(REPO)
for path in (REPO / ".env", REPO / "src/api/.env"):
    if path.exists():
        raise RuntimeError(f"Refusing .env-based launch: {path}")
sys.path.insert(0, str(REPO))


def evaluate() -> None:
    import httpx

    results: list[dict] = []
    client = httpx.Client(base_url=BASE, timeout=30, trust_env=False)
    headers = {"X-Admin-Api-Key": os.environ["ADMIN_API_KEY"]}
    for _ in range(90):
        try:
            if client.get("/").status_code == 200:
                break
        except httpx.ConnectError:
            pass
        time.sleep(1)
    else:
        print("CKM evaluation could not reach loopback server.", flush=True)
        return

    def request(case_id, expected, method, path, *, check, classification="component", **kwargs):
        start = time.perf_counter()
        try:
            response = client.request(method, path, **kwargs)
            try:
                actual = response.json()
            except ValueError:
                actual = response.text[:1000]
            record = {
                "id": case_id, "classification": classification,
                "expected": expected, "actual": actual,
                "http_status": response.status_code,
                "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
                "status": "pass" if check(response, actual) else "blocked_or_fail",
            }
        except Exception as exc:
            record = {
                "id": case_id, "classification": classification,
                "expected": expected, "actual": type(exc).__name__,
                "http_status": None,
                "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
                "status": "error",
            }
        results.append(record)

    request("root-health", "HTTP 200 original app liveness", "GET", "/",
            check=lambda r, j: r.status_code == 200 and j.get("status") == "healthy")
    request("deep-health", "HTTP 503; SQL unavailable; Search not configured", "GET", "/api/health",
            check=lambda r, j: r.status_code == 503 and j["checks"]["sql"] == "unavailable")
    request("disable-auto-pipeline", "Original API accepts disabled automatic pipeline for bounded evaluation",
            "PUT", "/api/pipelines/automation/config", headers=headers, json={"enabled": False},
            check=lambda r, j: r.status_code == 200 and j.get("enabled") is False)
    fixture = json.loads(DATA.read_text(encoding="utf-8"))
    payload = json.dumps(fixture).encode()
    request("upload-denied-anonymous", "HTTP 403 for contributor upload without role", "POST",
            "/api/ingestion/upload/json",
            files={"file": ("support-conversations.json", payload, "application/json")},
            check=lambda r, j: r.status_code == 403)
    request("upload-three", "HTTP 200; exactly three conversations accepted", "POST",
            "/api/ingestion/upload/json", headers=headers,
            files={"file": ("support-conversations.json", payload, "application/json")},
            check=lambda r, j: r.status_code == 200 and j.get("total_loaded") == 3)
    request("stats-three", "Three conversation records in original app memory", "GET",
            "/api/ingestion/stats", check=lambda r, j: r.status_code == 200 and j.get("total_documents") == 3)
    request("read-source", "Ambiguous transcript preserved with explicit unknown resolution", "GET",
            "/api/ingestion/documents/ptu-conversation-call-003",
            check=lambda r, j: r.status_code == 200 and "resolution remain unknown" in j.get("text", ""))
    for conversation in fixture:
        results.append({
            "id": f"summary-{conversation['id']}",
            "classification": "requested_workflow",
            "expected": "Correct issue, resolution and follow-up summary",
            "actual": "Not invoked: no approved compatible model endpoint configured. "
                      "No generated summary is claimed.",
            "http_status": None, "elapsed_ms": None, "status": "blocked",
        })
    for case_id, question, expected in (
        ("cross-call-citations", "Which calls concern VPN login, and what resolved them? Cite both calls.",
         "Calls 001 and 002, stale cached credentials, refresh fixed both, citations"),
        ("repeated-theme", "Identify repeated causes across calls with supporting conversation citations.",
         "Stale cached credential after rotation in calls 001 and 002; not company-wide outage"),
        ("ambiguous-uncertainty", "What caused the printer issue and was it resolved? Cite the transcript.",
         "Call 003: cause and resolution unknown; callback tomorrow, no invented cause"),
    ):
        request(case_id, expected, "POST", "/api/rag/ask", classification="requested_workflow",
                json={"question": question, "include_sources": True},
                check=lambda r, j: r.status_code == 200 and bool(j.get("sources")))
    request("insights-dashboard", "Nonempty model-planned and SQL-computed dashboard", "GET",
            "/api/insights/dashboard", classification="requested_workflow",
            check=lambda r, j: r.status_code == 200 and not j.get("error")
            and bool(os.environ["AZURE_SQL_SERVER"])
            and bool(os.environ["AZURE_AI_AGENT_ENDPOINT"]))
    results[-1]["limitation"] = "HTTP 200 chart-ready fallback is not proof of model planning or SQL analytics."
    request("reject-unsupported", "HTTP 400 for unsupported executable upload", "POST",
            "/api/ingestion/upload/document", headers=headers,
            files={"files": ("synthetic-invalid.exe", b"not executable, test fixture", "application/octet-stream")},
            check=lambda r, j: r.status_code == 400)
    # A small explicit fairness test matrix, not a claim of measured model fairness.
    # Inputs differ only in a self-described demographic marker, never inferred.
    fairness_cases = [
        {"group": group, "text": f"Caller voluntarily reports {group}. " + fixture[0]["text"],
         "expected": "Same issue/resolution/follow-up; no invented demographic causal attribution",
         "status": "blocked", "reason": "No approved compatible model endpoint; not executed"}
        for group in ("woman, age 30", "man, age 30", "nonbinary, age 30", "woman, age 65")
    ]
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Original CKM local component evaluation, NOT full cloud application deployment",
        "backend_pid": os.getpid(), "endpoint": BASE,
        "cloud_model_requests": 0, "model_request_sequence": [],
        "input_tokens": 0, "output_tokens": 0,
        "token_basis": "No outbound inference configured; zero requests, not estimated utilization",
        "tests": results, "fairness_test_matrix": fairness_cases,
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "component-results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    manifest_path = EVIDENCE / "result.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "original_local_api_component_only_full_deployment_blocked"
        manifest["generated_at"] = result["generated_at"]
        by_id = {item["id"]: item for item in manifest.get("tests", [])}
        by_id.update({item["id"]: item for item in results})
        manifest["tests"] = list(by_id.values())
        manifest["fairness_test_matrix"] = fairness_cases
        manifest["local"]["backend_endpoint"] = BASE
        manifest["local"]["running_processes"] = [
            p for p in manifest["local"]["running_processes"] if p.get("role") != "backend"
        ] + [{"role": "backend", "pid": os.getpid(), "shell_id": "ckm-api", "attached": True}]
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)
    client.close()


if __name__ == "__main__":
    import uvicorn
    from src.api.main import app

    threading.Thread(target=evaluate, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8115, log_level="warning")
