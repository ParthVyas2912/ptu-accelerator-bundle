"""Summarize only isolated DKM model metrics; optionally reconcile one pending operation."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

p = argparse.ArgumentParser()
p.add_argument("label")
p.add_argument("--reconcile", action="store_true")
p.add_argument("--reconcile-uncaptured", action="store_true",
               help="Only reconcile the documented lost corpus response, never grade it")
a = p.parse_args()
root = Path(__file__).resolve().parents[1] / "evidence/documents"
raw = json.loads((root / f"{a.label}-metrics-totals.json").read_text(encoding="utf-8-sig"))
deployments = {}
for metric in raw["value"]:
    for series in metric["timeseries"]:
        dims = {x["name"]["value"].lower(): x["value"] for x in series.get("metadatavalues", [])}
        points = [x["total"] for x in series["data"] if x.get("total") is not None]
        if points:
            deployments.setdefault(dims["modeldeploymentname"], {})[metric["name"]["value"]] = sum(points)
count = sum(x.get("ModelRequests", 0) for x in deployments.values())
statuses_raw = json.loads((root / f"{a.label}-metrics-statuses.json").read_text(encoding="utf-8-sig"))
statuses = []
for m in statuses_raw["value"]:
    for series in m["timeseries"]:
        dims = {x["name"]["value"].lower(): x["value"] for x in series.get("metadatavalues", [])}
        points = [x["total"] for x in series["data"] if x.get("total") is not None]
        if points:
            statuses.append(dims | {"requests": sum(points)})
out = {
    "label": a.label, "captured_utc": datetime.now(timezone.utc).isoformat(),
    "timespan": raw["timespan"], "by_deployment": deployments, "requests": count,
    "statuses": statuses, "total_tokens": sum(x.get("TotalTokens", 0) for x in deployments.values()),
    "input_tokens": sum(x.get("InputTokens", 0) for x in deployments.values()),
    "output_tokens": sum(x.get("OutputTokens", 0) for x in deployments.values()),
    "alias_check": sum(x["requests"] for x in statuses) == count,
}
if a.reconcile or a.reconcile_uncaptured:
    budget_path = root / "model-budget.json"
    budget = json.loads(budget_path.read_text(encoding="utf-8-sig"))
    pending = budget.get("pending_operation")
    if not pending:
        raise SystemExit("No pending operation; no ledger mutation")
    result_path = root / f"retry-phase-{pending['case']}.json"
    uncaptured = a.reconcile_uncaptured
    if uncaptured:
        assert pending["case"] == "qa-corpus"
        assert (root / "retry-phase-qa-corpus-uncaptured.json").exists()
        response = {}
    else:
        response = json.loads(result_path.read_text(encoding="utf-8-sig"))
    delta = count - pending["baseline"]
    expected = 4 if pending["case"] == "ingest-second" else 2
    if (not uncaptured and response.get("result", {}).get("status") != 200) or not out["alias_check"]:
        raise SystemExit("Outcome/error counters need manual reconciliation; reservation retained")
    if delta < expected or delta > pending["maximum"] or count > 12:
        raise SystemExit(f"Unsettled/unexpected counters: delta={delta}; reservation retained")
    budget["actual_observed_attempts"] = count
    budget["remaining_attempts"] = 12 - count
    budget.setdefault("reconciled_operations", []).append(pending | {
        "observed_delta": delta, "observed_total": count, "evidence": f"{a.label}-metrics-summary.json",
        "application_response_captured": not uncaptured,
        "grade": "UNVERIFIED: console encoding failure" if uncaptured else "See actual response checks"
    })
    budget["pending_operation"] = None
    budget["further_paid_actions_blocked_pending_safe_retry_control"] = False
    budget_path.write_text(json.dumps(budget, indent=2) + "\n")
(root / f"{a.label}-metrics-summary.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
