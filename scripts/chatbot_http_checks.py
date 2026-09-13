"""Local native API diagnostics; refuses model-capable configurations.

This captures missing-infrastructure failures. It is NOT an end-to-end success
test and must not be used to claim grounding or routing works.
"""
import json
from time import perf_counter
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8116"


def request(path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    start = perf_counter()
    try:
        with urlopen(req, timeout=30) as response:
            status, raw = response.status, response.read()
    except HTTPError as error:
        status, raw = error.code, error.read()
    return {
        "path": path,
        "status": status,
        "elapsed_ms": round((perf_counter() - start) * 1000, 3),
        "body": json.loads(raw),
    }


health = request("/health")
print(json.dumps({"kind": "health_only", **health}))
if health["body"].get("database") != "not_configured":
    raise SystemExit("Refusing functional requests: real Cosmos may be configured; use a separately approved metered test.")
print(json.dumps({"kind": "scenario_configuration_only", **request("/api/chat/config")}))

cases = [
    ("product_discovery", "Show me warm white paint colors."),
    ("return_warranty", "What are your return and warranty policies?"),
    ("mixed_routing", "Show me a calm blue paint and explain the return policy."),
    ("nonexistent_sku", "Do you sell PTU-NONEXISTENT-SKU-999? Give its exact SKU and stock availability."),
]
for case, question in cases:
    result = request(
        "/api/chat/message",
        {"content": question, "message_type": "user", "session_id": f"ptu-chatbot-{case}"},
    )
    print(json.dumps({
        "case": case,
        "verdict": "blocked_missing_infrastructure",
        "model_requests": 0,
        "returned_input_tokens": None,
        "returned_output_tokens": None,
        "returned_cached_tokens": None,
        **result,
    }))
