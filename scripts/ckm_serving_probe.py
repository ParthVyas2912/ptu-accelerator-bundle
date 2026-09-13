"""One bounded real-HTTP verification of the serving PID; no TestClient/model SDK."""
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

report_path = Path("/tmp/ckm-serving-http-result.json")
if report_path.exists():
    print("CKM_SERVING_RESULT_BASE64=" + base64.b64encode(report_path.read_bytes()).decode())
    raise SystemExit(0)

result = {"started_at": datetime.now(timezone.utc).isoformat(), "tests": [], "model_requests": 0,
          "transport": "real HTTP to Uvicorn127.0.0.1:8000", "probe_pid": os.getpid()}


def request(method, path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request("http://127.0.0.1:8000" + path, data=body, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        response = urllib.request.urlopen(req, timeout=90)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        payload = json.loads(response.read())
        headers = {k.lower(): v for k, v in response.headers.items() if k.lower().startswith("x-ckm-")}
        assert headers["x-ckm-inference"] == "disarmed-9-of-9"
        assert headers["x-ckm-model-dispatches"] == "0"
        assert int(headers["x-ckm-serving-pid"]) != os.getpid()
        result["serving_pid"] = int(headers["x-ckm-serving-pid"])
        result["last_response_guard_headers"] = headers
        return response.status, payload


def check(case, expected, actual, passed):
    result["tests"].append({"id": case, "expected": expected, "actual": actual,
                            "status": "passed" if passed else "failed"})
    if not passed:
        raise AssertionError(case)


try:
    status, body = request("GET", "/api/health")
    check("native-deep-health", "HTTP200/sql ok/search configured", {"status": status, "body": body},
          status == 200 and body["checks"]["sql"] == "ok" and body["checks"]["search"] == "configured")
    status, body = request("GET", "/api/pipelines/automation/config")
    check("native-automatic-processing-off", "enabled=false/auto_select=false", body,
          status == 200 and not body["enabled"] and not body["auto_select"])
    status, body = request("POST", "/api/ingestion/refresh")
    check("native-http-sql-reload", "HTTP200/refreshed/one file", {"status": status, "body": body},
          status == 200 and body["status"] == "refreshed" and body["files"] == 1)
    expected = json.loads(Path(__file__).with_name("ckm-serving-expected.json").read_text())
    status, docs = request("GET", "/api/ingestion/documents")
    check("native-list-three", sorted(item["id"] for item in expected), sorted(item["id"] for item in docs),
          status == 200 and {item["id"] for item in docs} == {item["id"] for item in expected})
    for source in expected:
        status, doc = request("GET", "/api/ingestion/documents/" + source["id"])
        check(source["id"], {"id": source["id"], "original_text_sha256": hashlib.sha256(source["text"].encode()).hexdigest()},
              {"status": status, "id": doc.get("id"), "original_text_sha256": hashlib.sha256(doc.get("text", "").encode()).hexdigest()},
              status == 200 and doc["id"] == source["id"] and doc["text"] == source["text"])
    for method, path, payload in [
        ("POST", "/api/processing/summarize", {"text": "Must not dispatch"}),
        ("GET", "/api/insights/dashboard", None),
        ("POST", "/api/rag/ask", {"question": "Must remain unsupported"}),
        ("POST", "/api/embeddings/index", {}),
        ("POST", "/api/documents/analyze", {}),
        ("POST", "/api/pipelines/run", {"pipeline_name": "full_knowledge_mining"}),
        ("PUT", "/api/pipelines/automation/config", {"enabled": True, "auto_select": True}),
        ("POST", "/api/ingestion/upload/json", {}),
    ]:
        status, body = request(method, path, payload)
        check("disarmed-" + path, "Explicit503 without inference or heuristic output", {"status": status, "body": body},
              status == 503 and body.get("inference_armed") is False and body.get("model_requests_dispatched") == 0
              and body.get("error") in {"CKM_INFERENCE_DISARMED", "CKM_EXPLORE_UNSUPPORTED_AND_DISARMED"})
    result["status"] = "passed"
except (AssertionError, KeyError, ValueError, urllib.error.URLError, TimeoutError) as exc:
    result["status"] = "failed"
    result["error_type"] = type(exc).__name__
    result["error"] = str(exc)[:500]
finally:
    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    report_path.write_text(json.dumps(result, indent=2) + "\n")
    print("CKM_SERVING_RESULT_BASE64=" + base64.b64encode(report_path.read_bytes()).decode())
raise SystemExit(0 if result["status"] == "passed" else 2)
