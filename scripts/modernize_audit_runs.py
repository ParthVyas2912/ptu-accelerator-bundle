"""Read-only post-run service usage/step audit. Never starts a model run."""
import asyncio
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential

B = Path(__file__).resolve().parents[1]
OUT = B/"evidence/modernize"
arguments = argparse.ArgumentParser()
arguments.add_argument("--cloud", action="store_true")
options = arguments.parse_args()
if options.cloud:
    state = json.loads((OUT/"cloud-budget-snapshot.json").read_text())
    ledger = {
        "agents": state.get("current_agents", []),
        "previous_agent_sets": state.get("previous_agent_sets", []),
        "threads": sorted({e["path"].split("/threads/")[1].split("/")[0] for e in state["events"]}),
        "endpoint": "https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj",
    }
else:
    ledger = json.loads((OUT/"native-model-events.json").read_text())
names = {a["id"]: a["name"] for group in ledger.get("previous_agent_sets", []) for a in group}
names.update({a["id"]: a["name"] for a in ledger.get("agents", [])})

async def main():
    result = {"scope": "Read-only Azure service run usage and tool-step audit",
              "audited": datetime.now(timezone.utc).isoformat(), "runs": [], "new_model_requests": 0}
    async with AzureCliCredential(process_timeout=150) as credential:
        async with AIProjectClient(endpoint=ledger["endpoint"], credential=credential, retry_total=0) as client:
            for thread in ledger["threads"]:
                async for run in client.agents.runs.list(thread_id=thread):
                    data = run.as_dict()
                    aid = data.get("assistant_id", data.get("agent_id"))
                    row = {key: data.get(key) for key in
                           ["id", "status", "usage", "last_error", "created_at", "completed_at",
                            "started_at", "failed_at", "model"]}
                    row.update(thread_id=thread, agent_id=aid, agent_name=names.get(aid), steps=[])
                    try:
                        async for step in client.agents.run_steps.list(thread_id=thread, run_id=run.id):
                            sd = step.as_dict()
                            row["steps"].append({key: sd.get(key) for key in
                                                 ["id", "type", "status", "usage", "step_details",
                                                  "created_at", "completed_at", "last_error"]})
                    except Exception as exc:
                        row["step_audit_error_type"] = type(exc).__name__
                    result["runs"].append(row)
    output = "cloud-run-audit.json" if options.cloud else "native-run-audit.json"
    (OUT/output).write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"runs": len(result["runs"]), "agents": [r["agent_name"] for r in result["runs"]],
                      "new_model_requests": 0}, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
