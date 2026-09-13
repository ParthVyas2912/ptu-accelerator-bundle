"""Launch original native Modernize backend with eval-only cost/deletion safeguards.

No storage or batch-service substitutes: uses the real approved Cosmos/Blob.
All application modules and SQL agents come from the cloned official repo.
"""
import asyncio
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlparse

B = Path(__file__).resolve().parents[1]
R = B.parent.parent / "repo" / "Modernize-your-code-solution-accelerator"
OUT = B / "evidence/modernize"
if (OUT/"cloud-budget-snapshot.json").exists():
    raise SystemExit("Cloud evaluation owns the durable global budget; do not restart the obsolete local ledger.")
ENDPOINT = "https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj"
ENV = {
    "APP_ENV": "dev",
    "AI_PROJECT_ENDPOINT": ENDPOINT,
    "COSMOSDB_ENDPOINT": "https://cosmos-ptu-modernize-eus20911.documents.azure.com:443/",
    "COSMOSDB_DATABASE": "ptu-modernize",
    "COSMOSDB_BATCH_CONTAINER": "ptu-modernize-batches",
    "COSMOSDB_FILE_CONTAINER": "ptu-modernize-files",
    "COSMOSDB_LOG_CONTAINER": "ptu-modernize-logs",
    "AZURE_BLOB_ACCOUNT_NAME": "stptumodernize0911pv",
    "AZURE_BLOB_CONTAINER_NAME": "ptu-modernize-files",
    "AZURE_BASIC_LOGGING_LEVEL": "WARNING",
    "AZURE_PACKAGE_LOGGING_LEVEL": "WARNING",
}
for name in ["MIGRATOR", "PICKER", "FIXER", "SEMANTIC_VERIFIER", "SYNTAX_CHECKER"]:
    ENV[name+"_AGENT_MODEL_DEPLOY"] = "gpt-5.1"
os.environ.update(ENV)
os.chdir(R/"src/backend")
sys.path.insert(0, str(R/"src/backend"))

from azure.core.pipeline.transport import AioHttpTransport
from azure.identity.aio import AzureCliCredential
from azure.identity import AzureCliCredential as SyncAzureCliCredential
from azure.ai.projects.aio import AIProjectClient
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent

protocol = json.loads((OUT/"migrator-protocol.json").read_text(encoding="utf-8"))
prior = len(protocol["calls"])
component_file = OUT/"component-evaluation.json"
if component_file.exists():
    prior += len(json.loads(component_file.read_text()).get("model_request_events", []))
ledger_file = OUT/"native-model-events.json"
ledger = (json.loads(ledger_file.read_text()) if ledger_file.exists()
          else {"model_events": [], "threads": [], "blocked_deletes": 0})
if ledger.get("agents") and ledger["agents"] not in ledger.get("previous_agent_sets", []):
    ledger.setdefault("previous_agent_sets", []).append(ledger["agents"])
ledger.update(prior_model_calls=prior, total_cap=12, backend_pid=os.getpid(),
              endpoint=ENDPOINT, backend_url="http://127.0.0.1:8114")


def save():
    ledger_file.write_text(json.dumps(ledger, indent=2, default=str), encoding="utf-8")


send_original = AioHttpTransport.send


async def guarded_send(self, request, **kwargs):
    parsed = urlparse(request.url)
    path = parsed.path
    is_foundry = parsed.hostname == "edcfoundryhack01.services.ai.azure.com"
    if request.method.upper() == "DELETE":
        ledger["blocked_deletes"] += 1
        save()
        raise RuntimeError("Automatic Azure deletion blocked by evaluation contract")
    if is_foundry and "/threads/" in path:
        thread = path.split("/threads/")[1].split("/")[0]
        if thread not in ledger["threads"]:
            ledger["threads"].append(thread)
    consumes = is_foundry and request.method.upper() == "POST" and (
        path.endswith("/runs") or path.endswith("/submit_tool_outputs"))
    event = None
    if consumes:
        if prior + len(ledger["model_events"]) >= 12:
            raise RuntimeError("Modernize total live model HTTP-request cap reached (12)")
        event = {"number": prior+len(ledger["model_events"])+1, "path": path,
                 "started": datetime.now(timezone.utc).isoformat()}
        ledger["model_events"].append(event)
        save()
    started = time.monotonic()
    try:
        response = await send_original(self, request, **kwargs)
        if event is not None:
            event["http_status"] = response.status_code
            event["headers_latency_seconds"] = round(time.monotonic()-started, 3)
        return response
    except Exception as exc:
        if event is not None:
            event["error_type"] = type(exc).__name__
        raise
    finally:
        if event is not None:
            save()


AioHttpTransport.send = guarded_send
credential = AzureCliCredential(process_timeout=150)


def create_client(*args, **kwargs):
    # Upstream lifespan passes a synchronous credential to its async Agent client.
    # Use the explicitly documented Azure CLI identity in its async SDK form.
    return AIProjectClient(endpoint=ENDPOINT, credential=credential, retry_total=0)


AzureAIAgent.create_client = staticmethod(create_client)
import helper.azure_credential_utils as identity_helpers
identity_helpers.get_azure_credential = lambda client_id=None: SyncAzureCliCredential(process_timeout=150)
from common.config.config import Config
Config.get_azure_credentials = lambda self: AzureCliCredential(process_timeout=150)

from sql_agents.helpers.comms_manager import CommsManager
from sql_agents.helpers.agents_manager import SqlAgents
comms_init = CommsManager.__init__


def bounded_comms_init(self, *args, **kwargs):
    kwargs["max_retries"] = 1
    comms_init(self, *args, **kwargs)


async def preserve_remote_objects(self):
    return None


CommsManager.__init__ = bounded_comms_init
CommsManager.cleanup = preserve_remote_objects
SqlAgents.delete_agents = preserve_remote_objects

import app as upstream
from sql_agents.agent_manager import get_sql_agents
import uvicorn

app = upstream.app


@app.get("/eval/status", include_in_schema=False)
async def evaluation_status():
    agents = get_sql_agents()
    ledger["agents"] = [{"name": agent.name, "id": agent.id} for agent in agents.agents] if agents else []
    save()
    return {"agents_initialized": agents is not None, "agents": ledger["agents"],
            "model_http_attempts_total": prior+len(ledger["model_events"]),
            "model_http_attempts_remaining": 12-prior-len(ledger["model_events"]),
            "backend_pid": os.getpid(), "persistence": "real approved Azure Cosmos and Blob"}


@app.get("/eval/usage", include_in_schema=False)
async def evaluation_usage():
    usage = []
    for thread in ledger["threads"]:
        try:
            async for run in upstream.azure_client.agents.runs.list(thread_id=thread):
                data = run.as_dict()
                usage.append({"thread_id": thread, "run_id": run.id, "status": str(run.status),
                              "agent_id": data.get("assistant_id", data.get("agent_id")),
                              "usage": data.get("usage"), "last_error": data.get("last_error"),
                              "created_at": data.get("created_at"), "completed_at": data.get("completed_at")})
        except Exception as exc:
            usage.append({"thread_id": thread, "error_type": type(exc).__name__})
    ledger["run_usage"] = usage
    save()
    return usage


save()
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8114, workers=1, log_level="warning")
