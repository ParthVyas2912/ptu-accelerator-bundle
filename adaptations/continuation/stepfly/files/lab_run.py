"""Bounded, non-interactive StepFly run for the MCAPS continuation lab.

Runs the native Scheduler path against synthetic incident 700000001 with the
lab attempt budget installed. No live Azure remediation: StepFly's executor
tools are code_interpreter / sql_query_tool over the local synthetic SQLite DB.
"""
import argparse
import json
import os
import sys
import traceback
import uuid
from datetime import datetime, timezone

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if (os.environ.get("LAB_ALLOW_PROVIDER_CALLS") != "1"
        or int(os.environ.get("LAB_ATTEMPT_BUDGET", "0")) <= 0):
    raise SystemExit("Archived harness is disarmed; provider execution requires separate approval.")

import lab_instrument

lab_instrument.install()

from stepfly.agents.scheduler import Scheduler  # noqa: E402
from stepfly.utils.memory import Memory  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incident-id", required=True)
    ap.add_argument("--out", default="lab-run-summary.json")
    args = ap.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    session_id = f"{args.incident_id}_labsession-{ts}_{str(uuid.uuid4())[:8]}"
    summary = {
        "session_id": session_id,
        "incident_id": args.incident_id,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "budget": lab_instrument.BUDGET,
    }
    try:
        memory = Memory(session_id=session_id)
        scheduler = Scheduler(session_id=session_id, memory=memory)
        scheduler.start_session(incident_id=args.incident_id)
        summary["outcome"] = "completed"
    except lab_instrument.LabBudgetExceeded as exc:
        summary["outcome"] = "stopped_at_budget"
        summary["stop_reason"] = str(exc)
    except Exception as exc:  # noqa: BLE001
        summary["outcome"] = "error"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)[:1500]
        summary["traceback"] = traceback.format_exc()[-3000:]
    finally:
        summary["attempts_used"] = lab_instrument.global_attempts()
        summary["attempts_this_process"] = lab_instrument.attempts()
        summary["ended_utc"] = datetime.now(timezone.utc).isoformat()
        with open(args.out, "w", encoding="utf8") as fh:
            json.dump(summary, fh, indent=2)
        print(json.dumps({k: v for k, v in summary.items() if k != "traceback"}, indent=2))


if __name__ == "__main__":
    main()
