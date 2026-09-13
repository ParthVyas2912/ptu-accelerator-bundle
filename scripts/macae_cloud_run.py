"""Thin evaluation entrypoint; imports the native FastAPI app."""
import json
import os
import sys

os.environ.setdefault("MACAE_STATE_DIR", "/tmp/macae-state")
os.environ.setdefault("MACAE_EVIDENCE_DIR", "/tmp/macae-evidence")

from macae_cosmos_budget import CosmosBudget
import macae_model_guard as guard


def main():
    sys.path.insert(0, os.getcwd())  # Official backend image WORKDIR is /app.
    budget = CosmosBudget()
    if sys.argv[1:] == ["authorize-22"]:
        if os.environ.get("MACAE_LIVE_REQUESTS_ENABLED") == "true":
            raise RuntimeError("Disable inference before the one-time allowance migration")
        print("MACAE_RESULT " + json.dumps({
            "name": "cloud-budget-migration", "data": budget.authorize_second_pass(),
        }), flush=True)
        return
    if sys.argv[1:] == ["init-budget"]:
        # Stop local backend first; verify/export its ledger and explicitly pass
        # the already-consumed total. This command must never silently assume 0.
        used = int(os.environ["MACAE_PREVIOUS_LIVE_CALLS"])
        budget.initialize_once(used)
        print(f"MACAE durable ledger initialized once; previous consumed total={used}")
        return

    def reserve(record):
        if os.environ.get("MACAE_LIVE_REQUESTS_ENABLED") != "true":
            raise RuntimeError("MACAE connectivity-only revision: live inference disabled")
        return budget.reserve(record)

    guard.reserve_record = reserve
    guard.persist_record = budget.persist
    guard.install()
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=1)


if __name__ == "__main__":
    main()
