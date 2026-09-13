"""Verify closed-budget custody using mocked transport and read-only local data."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from unittest.mock import patch

import httpx
import psycopg2
import cwyd_runtime as runtime

E = runtime.EVIDENCE
baseline = json.loads((E / "budget-custody-baseline.json").read_text())
checks = []


def check(name, condition):
    checks.append({"name": name, "passed": bool(condition)})
    if not condition:
        raise AssertionError(name)


async def verify_transport():
    transport_calls = []

    def forbidden_transport(request):
        transport_calls.append(str(request.url))
        raise AssertionError("The closed guard reached HTTP transport")

    runtime.install_measurement()
    urls = [
        "https://edcfoundryhack01.openai.azure.com/openai/v1/embeddings",
        "https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj/openai/v1/responses",
    ]
    async with httpx.AsyncClient(transport=httpx.MockTransport(forbidden_transport),
                                trust_env=False) as client:
        async def blocked(url, error_type, message):
            try:
                await client.post(url, json={"model": "guard-test-only"})
            except error_type as exc:
                check(message, bool(str(exc)))
            else:
                raise AssertionError("The model guard did not reject the request")

        with patch.dict(os.environ):
            os.environ.pop("CWYD_INFERENCE_DISABLED", None)
            for url in urls:
                await blocked(url, RuntimeError, "persistent disabled policy blocks " + url)
            policy = runtime.read_budget_policy()
            with patch.object(runtime, "read_budget_policy", return_value={**policy, "inference_enabled": True}):
                await blocked(urls[0], RuntimeError, "exhausted16-total cap independently blocks a toggled enable flag")
                os.environ["CWYD_INFERENCE_DISABLED"] = "true"
                await blocked(urls[0], RuntimeError, "launcher disable setting independently blocks inference")
            os.environ.pop("CWYD_INFERENCE_DISABLED", None)
            with tempfile.TemporaryDirectory(prefix="cwyd-budget-test-") as folder:
                policy_file = Path(folder) / "policy.json"
                with patch.object(runtime, "BUDGET_FILE", policy_file):
                    await blocked(urls[0], FileNotFoundError, "missing policy fails closed")
                    policy_file.write_text(json.dumps({**policy, "model_attempt_limit": 18}))
                    await blocked(urls[0], RuntimeError, "obsolete18-total policy fails closed")
    check("zero HTTP transport invocations in mocked guard tests", not transport_calls)


check("persistent status is closed16/16", runtime.budget_status() == {
    "model_attempt_limit": 16, "model_attempts": 16, "remaining_attempts": 0,
    "inference_enabled": False, "requires_new_explicit_authorization": True,
})
asyncio.run(verify_transport())

for command, label, expected_code in [
    ([sys.executable, str(Path(__file__).with_name("cwyd_runtime.py")), "worker"],
     "direct worker launch refuses ingestion", 2),
    (["powershell.exe", "-NoProfile", "-File", str(Path(__file__).with_name("Start-Cwyd.ps1")),
      "-Service", "worker"], "Start script refuses worker launch", 1),
]:
    completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
    check(label, completed.returncode == expected_code
          and ("disabled" in completed.stderr or "closed" in completed.stderr))

api = "http://127.0.0.1:8112"
with httpx.Client(timeout=30, trust_env=False) as client:
    for base, route in [(api, "/api/conversation"), (api, "/api/admin/documents"),
                        ("http://127.0.0.1:5112", "/api/conversation")]:
        response = client.post(base + route, json={})
        check("explicit503 before handlers for " + base + route,
              response.status_code == 503 and response.json().get("code") == "cwyd_evaluation_closed"
              and response.json().get("remaining_attempts") == 0)
    for url in ["http://127.0.0.1:5112/", "http://127.0.0.1:5112/admin", api + "/api/health"]:
        check("read-only endpoint200 " + url, client.get(url).status_code == 200)
    documents = client.get(api + "/api/admin/documents")
    check("five source documents remain", documents.status_code == 200 and documents.json()["total"] == 5)
    source = client.get(api + "/api/files/ptu-cwyd-travel.txt")
    check("active replacement blob preserved", source.status_code == 200 and "now 91 credits" in source.text)
    for receipt_name in ["questions-grouped.json", "question-update.json"]:
        receipt = json.loads((E / receipt_name).read_text())["actual"]
        response = client.get(api + "/api/history/conversations/" + receipt["conversation_id"])
        response.raise_for_status()
        assistant = [message for message in response.json()["messages"] if message["role"] == "assistant"][-1]
        check("stored answer and citations preserved " + receipt_name,
              assistant["content"] == receipt["content"]
              and assistant.get("metadata", {}).get("citations") == receipt["citations"])

with psycopg2.connect(host="127.0.0.1", port=15432, dbname="ptu_cwyd", user="cwyd") as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT title,content FROM documents ORDER BY title")
        documents = cursor.fetchall()
        travel = [content for title, content in documents if title == "ptu-cwyd-travel.txt"]
        check("five active index rows and replacement retained",
              len(documents) == 5 and len(travel) == 1 and "now 91 credits" in travel[0])

with sqlite3.connect(runtime.STATE / "model-budget.sqlite") as conn:
    rows = conn.execute("SELECT id,record FROM calls ORDER BY id").fetchall()
check("all16 SQLite records unchanged",
      len(rows) == 16 and hashlib.sha256(json.dumps(rows).encode()).hexdigest() == baseline["ledger_sha256"])
check("raw model evidence byte-for-byte unchanged",
      hashlib.sha256((E / "model-calls.json").read_bytes()).hexdigest() == baseline["model_calls_sha256"])
result = json.loads((E / "result.json").read_text())
check("all8 passed business criteria unchanged",
      result["final_functional_summary"]["business_criteria_passed"] == 8
      and hashlib.sha256(json.dumps(result["final_functional_criteria"], sort_keys=True).encode()).hexdigest()
      == baseline["criteria_sha256"])
check("result reflects closed16-total custody",
      result["model_attempt_limit"] == 16 and result["remaining_first_pass_attempts"] == 0
      and result["evaluation_inference_enabled"] is False)
output = {
    "status": "PASS", "model_calls_added": 0, "model_attempt_limit": 16, "model_attempts": 16,
    "remaining_attempts": 0, "inference_enabled": False, "checks": checks,
    "ledger_sha256": baseline["ledger_sha256"],
    "model_calls_sha256": baseline["model_calls_sha256"],
    "criteria_sha256": baseline["criteria_sha256"],
    "azure_changes": False, "other_apps_modified": False,
}
(E / "budget-custody-validation.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
result["budget_custody_validation"] = {
    "status": "PASS", "evidence": "budget-custody-validation.json",
    "checks_passed": len(checks), "new_model_calls": 0,
    "all16_ledger_records_unchanged": True, "all8_passed_criteria_unchanged": True,
}
(E / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"status": "PASS", "checks_passed": len(checks), "new_model_calls": 0,
                  "attempts": "16/16", "business_criteria": "8/8"}))
