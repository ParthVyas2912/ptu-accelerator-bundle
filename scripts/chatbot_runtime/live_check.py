"""One catalog/unknown-SKU journey through the guarded native API."""
import json
import time
import httpx
from cosmos_budget import store

ledger = store().snapshot()
if ledger["limit"] - sum(row["units"] for row in ledger["requests"]) < 5:
    raise SystemExit("Insufficient budget: catalog journey requires five conservative units.")
if any("status" not in row for row in ledger["requests"]):
    raise SystemExit("An earlier model attempt is unfinished.")
question = (
    "What is the catalog price of Snow Veil paint? "
    "Do you sell the SKU ZZ-999999?"
)
start = time.perf_counter()
response = httpx.post(
    "http://127.0.0.1:8001/api/chat/message",
    json={
        "content": question, "message_type": "user",
        "session_id": "ptu-chatbot-catalog-eval-20260912",
    },
    timeout=210,
)
print(json.dumps({
    "check": "native_catalog_and_negative_sku", "question": question,
    "status": response.status_code, "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
    "response": response.json(),
}), flush=True)
ledger = store().snapshot()
print(json.dumps({
    "ledger_id": ledger["id"], "limit": ledger["limit"],
    "reserved_units": sum(row["units"] for row in ledger["requests"]),
    "requests": ledger["requests"],
}), flush=True)
if response.status_code != 200:
    raise SystemExit(f"Native text journey returned HTTP {response.status_code}.")
