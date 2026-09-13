"""Close only the fixed evaluation ledger, preserving every request."""
import hashlib
import json
from datetime import datetime, timezone
from azure.core import MatchConditions
from cosmos_budget import store, DOCUMENT_ID, PARTITION

budget = store()
before = budget.snapshot()
rows = before["requests"]
if len(rows) != 8 or sum(row["units"] for row in rows) != 10:
    raise SystemExit("Unexpected committed usage; refusing closure.")
if any("status" not in row for row in rows):
    raise SystemExit("An attempt is unfinished; refusing closure.")
fingerprint = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
if not before.get("closed"):
    if before["limit"] != 12:
        raise SystemExit("Unexpected original allowance.")
    before.update(
        original_limit=12, limit=10, closed=True,
        closed_at=datetime.now(timezone.utc).isoformat(),
        reclaimed_uncommitted_units=2,
        new_operator_allowance_required=True,
    )
    budget.container.replace_item(
        item=DOCUMENT_ID, body=before, etag=before["_etag"],
        match_condition=MatchConditions.IfNotModified,
    )
try:
    budget.reserve({"units": 1, "kind": "closure_guard_check"})
except RuntimeError as error:
    if "budget limit" not in str(error) and "closed" not in str(error):
        raise
else:
    raise SystemExit("Guard did not reject admission.")
after = budget.container.read_item(item=DOCUMENT_ID, partition_key=PARTITION)
if not after["closed"] or after["limit"] != 10 or hashlib.sha256(
    json.dumps(after["requests"], sort_keys=True).encode()
).hexdigest() != fingerprint:
    raise SystemExit("Closure verification failed.")
print(json.dumps({
    "check": "allowance_closed", "limit": 10, "committed": 10,
    "visible_attempts": len(after["requests"]), "reclaimed": 2,
    "closed_at": after["closed_at"], "requests_sha256": fingerprint,
    "guard_rejected_admission": True, "new_model_calls": 0,
}), flush=True)
