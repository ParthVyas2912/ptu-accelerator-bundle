"""Narrow protocol reproduction of the ORIGINAL repository Migrator agent.

Fallback while official dependency installation is pending. This is not the
full application, not the five-agent pipeline, and not an app replacement.
Uses the repository prompt, its three-candidate setting and response schema,
the Foundry Agents API, and the same model/temperature configuration.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import time

import requests

B = Path(__file__).resolve().parents[1]
R = B.parent.parent / "repo" / "Modernize-your-code-solution-accelerator"
OUT = B / "evidence/modernize/migrator-protocol.json"
API = "https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj"
VERSION = "2025-05-01"
if OUT.exists() and json.loads(OUT.read_text()).get("calls"):
    raise SystemExit("Prior model-call evidence exists; refusing duplicate run.")
prompt_bytes = (R/"src/backend/sql_agents/agents/migrator/prompt.txt").read_bytes()
prompt = prompt_bytes.decode("utf-8-sig")
for key, value in {"source": "informix", "target": "tsql", "numCandidates": "3"}.items():
    prompt = prompt.replace("{{$"+key+"}}", value)

state = {
    "scope": "repository Migrator protocol reproduction only; not full app or SDK pipeline",
    "prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
    "original_prompt": "src/backend/sql_agents/agents/migrator/prompt.txt",
    "model": "gpt-5.1", "sku": "GlobalStandard", "model_version": "2025-11-13",
    "endpoint": API, "api_version": VERSION, "calls": [], "tests": [],
    "created_agent_ids": [], "created_thread_ids": [], "deleted_objects": [],
    "initial_cap_all_evaluation": 12,
    "adaptations": ["Native HTTP protocol reproduction because official dependency install is pending",
                    "Agent name prefixed for evaluation isolation", "No automatic deletion"],
}


def save():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(state, indent=2), encoding="utf-8")


def api(method, route, data=None):
    r = requests.request(method, API+route, params={"api-version": VERSION},
                         headers=headers, json=data, timeout=80)
    try:
        body = r.json()
    except ValueError:
        body = {"error": {"message": "non-JSON response"}}
    if r.status_code >= 400:
        raise RuntimeError(json.dumps({"http_status": r.status_code, "error": body.get("error")}))
    return r.status_code, body


save()
p = subprocess.run(
    ["az.cmd", "account", "get-access-token", "--subscription",
     "1feb53b2-854a-4ea7-b5a6-709b7d804f70", "--resource", "https://ai.azure.com", "-o", "json"],
    capture_output=True, text=True, timeout=180)
if p.returncode:
    state["blocked"] = "Azure CLI identity failed; output suppressed"
    save()
    raise SystemExit(state["blocked"])
headers = {"Authorization": "Bearer "+json.loads(p.stdout)["accessToken"]}

schema = {
    "type": "object", "properties": {
        "input_summary": {"type": "string"},
        "candidates": {"type": "array", "items": {"type": "object", "properties": {
            "plan": {"type": "string"}, "candidate_query": {"type": "string"}},
            "required": ["plan", "candidate_query"]}},
        "input_error": {"type": ["string", "null"]},
        "summary": {"type": ["string", "null"]},
        "rai_error": {"type": ["string", "null"]},
    }, "required": ["input_summary", "candidates"],
}
try:
    status, assistant = api("POST", "/assistants", {
        "name": "ptu-modernize-migrator-eval", "model": "gpt-5.1", "instructions": prompt,
        "temperature": 0.0,
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "MigratorResponse", "description": "respond with migratorresponse", "schema": schema}},
    })
    state["created_agent_ids"].append(assistant["id"])
    state["agent_creation_http_status"] = status
    save()
    cases = [
        ("malformed", "SELEC customer_id FROM WHERE;", "Actionable input_error; no invented repair"),
        ("repo-nvl", (R/"data/informix/simple/q3_informix.sql").read_text(encoding="utf-8-sig"),
         "T-SQL candidates for correlated NVL query; target syntax and synthetic result comparison"),
        ("vendor-procedure", "CREATE PROCEDURE ptu_stream() RETURNING INTEGER; DEFINE i INTEGER; "
         "FOREACH SELECT o.order_id INTO i FROM orders o JOIN customers c ON "
         "c.customer_id=o.customer_id RETURN i WITH RESUME; END FOREACH; END PROCEDURE;",
         "Identify streaming procedure differences or unsupported constructs"),
        ("demographic-schema", "SELECT customer_id, gender, age_group FROM customers WHERE active = 1;",
         "No unwarranted refusal of harmless demographic schema; preserve all fields and filter"),
    ]
    for name, source, expected in cases:
        # This fallback has at most four model requests, including failed runs.
        if len(state["calls"]) >= 4:
            break
        started = time.monotonic()
        test = {"id": name, "source": source, "expected": expected}
        _, thread = api("POST", "/threads", {"messages": [{"role": "user", "content": source}]})
        state["created_thread_ids"].append(thread["id"])
        call = {"number": len(state["calls"])+1, "test_id": name, "thread_id": thread["id"]}
        state["calls"].append(call)
        save()
        try:
            code, run = api("POST", f"/threads/{thread['id']}/runs", {"assistant_id": assistant["id"]})
            call.update(http_status=code, run_id=run["id"])
            while run["status"] in ("queued", "in_progress", "cancelling"):
                if time.monotonic()-started > 300:
                    raise TimeoutError("Run exceeded 300 seconds; no automatic deletion/cancel")
                time.sleep(5)
                _, run = api("GET", f"/threads/{thread['id']}/runs/{run['id']}")
            call.update(status=run["status"], usage=run.get("usage"),
                        last_error=run.get("last_error"),
                        cached_tokens=(run.get("usage") or {}).get("prompt_token_details", {}).get("cached_tokens"))
            if run["status"] == "completed":
                _, messages = api("GET", f"/threads/{thread['id']}/messages?order=desc")
                text = next(
                    c["text"]["value"]
                    for m in messages["data"] if m["role"] == "assistant"
                    for c in m["content"] if c["type"] == "text")
                test["response"] = json.loads(text)
                test["actual"] = "structured Migrator response returned"
            else:
                test["actual"] = "run "+run["status"]
                test["error"] = run.get("last_error")
        except Exception as exc:
            test["actual"] = type(exc).__name__
            test["error"] = str(exc)[:2000]
            call["error"] = str(exc)[:2000]
        call["elapsed_seconds"] = round(time.monotonic()-started, 3)
        test["elapsed_seconds"] = call["elapsed_seconds"]
        state["tests"].append(test)
        save()
        print(json.dumps({"test": name, "actual": test["actual"], "usage": call.get("usage"),
                          "error": test.get("error")}), flush=True)
        if test.get("error") and "temperature" in str(test["error"]).lower():
            # Do not waste the four-request budget repeating an incompatibility.
            break
except Exception as exc:
    state["blocked"] = str(exc)[:2000]
    save()
    print(json.dumps({"blocked": state["blocked"]}), flush=True)
