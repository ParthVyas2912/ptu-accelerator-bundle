"""Original FastAPI/SQL pipeline with cloud identity and bounded-evaluation adapters."""
import asyncio
import os
from pathlib import Path
import time
from urllib.parse import urlparse

from azure.core.pipeline.transport import AioHttpTransport, RequestsTransport
from azure.identity.aio import ManagedIdentityCredential
from azure.ai.projects.aio import AIProjectClient
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from budget import production_budget

os.chdir("/app")
ENDPOINT = "https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj"
budget = production_budget()
credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
send_async = AioHttpTransport.send
send_sync = RequestsTransport.send


def guarded_sync(self, request, **kwargs):
    if request.method.upper() == "DELETE":
        raise RuntimeError("Azure deletion disabled by evaluation contract")
    return send_sync(self, request, **kwargs)


async def guarded_async(self, request, **kwargs):
    parsed = urlparse(request.url)
    if request.method.upper() == "DELETE":
        raise RuntimeError("Azure deletion disabled by evaluation contract")
    consumes = parsed.hostname == "edcfoundryhack01.services.ai.azure.com" and request.method.upper() == "POST" and (
        parsed.path.endswith("/runs") or parsed.path.endswith("/submit_tool_outputs"))
    if not consumes:
        return await send_async(self, request, **kwargs)
    # Reservation MUST be persisted before network send. No Blob/data access => no model call.
    event_id = await asyncio.to_thread(budget.reserve, parsed.path)
    started = time.monotonic()
    details = {}
    try:
        response = await send_async(self, request, **kwargs)
        details = {"http_status": response.status_code,
                   "headers_latency_seconds": round(time.monotonic()-started, 3)}
        return response
    except Exception as exc:
        details = {"error_type": type(exc).__name__}
        raise
    finally:
        # Even if this update fails, the original reservation remains spent.
        if details:
            await asyncio.to_thread(budget.finish, event_id, details)


RequestsTransport.send = guarded_sync
AioHttpTransport.send = guarded_async
AzureAIAgent.create_client = staticmethod(
    lambda *a, **kw: AIProjectClient(endpoint=ENDPOINT, credential=credential, retry_total=0))

from common.config.config import Config
Config.get_azure_credentials = lambda self: credential
from sql_agents.helpers.comms_manager import CommsManager
from sql_agents.helpers.agents_manager import SqlAgents
original_comms_init = CommsManager.__init__


def bounded_comms(self, *args, **kwargs):
    kwargs["max_retries"] = 1
    original_comms_init(self, *args, **kwargs)


async def no_automatic_delete(self):
    return None


CommsManager.__init__ = bounded_comms
CommsManager.cleanup = no_automatic_delete
SqlAgents.delete_agents = no_automatic_delete

import app as upstream
from fastapi.responses import JSONResponse
from sql_agents.agent_manager import get_sql_agents
app = upstream.app


@app.middleware("http")
async def evaluation_gate(request, call_next):
    if request.method == "DELETE":
        return JSONResponse({"detail": "Azure deletion disabled for evaluation"}, status_code=403)
    if request.method == "POST" and request.url.path == "/api/start-processing":
        try:
            payload = await request.json()
            await asyncio.to_thread(budget.claim_batch, payload.get("batch_id"))
        except Exception as exc:
            return JSONResponse({"detail": str(exc)}, status_code=409)
    return await call_next(request)


@app.get("/eval/status", include_in_schema=False)
async def status():
    agents = get_sql_agents()
    identities = [{"name": a.name, "id": a.id} for a in agents.agents] if agents else []
    try:
        state, _ = await asyncio.to_thread(budget.read)
        await asyncio.to_thread(budget.record, "current_agents", identities)
        total = state["prior_calls"]+len(state["events"])
        return {"agents_initialized": agents is not None, "agents": identities,
                "model_http_attempts_total": total, "model_http_attempts_remaining": 12-total,
                "processing_enabled": state["processing_enabled"], "claimed_batch": state["claimed_batch"],
                "persistence": "actual Azure Blob/Cosmos through approved private endpoints",
                "deployment": "adapted official-source cloud container"}
    except Exception as exc:
        return JSONResponse({"agents_initialized": agents is not None, "agents": identities,
                             "budget_ready": False, "error_type": type(exc).__name__}, status_code=503)


@app.get("/eval/ledger", include_in_schema=False)
async def ledger():
    state, _ = await asyncio.to_thread(budget.read)
    return state


@app.get("/eval/usage", include_in_schema=False)
async def usage():
    state, _ = await asyncio.to_thread(budget.read)
    threads = sorted({e["path"].split("/threads/")[1].split("/")[0] for e in state["events"]})
    rows = []
    for thread in threads:
        async for run in upstream.azure_client.agents.runs.list(thread_id=thread):
            data = run.as_dict()
            row = {key: data.get(key) for key in
                   ["id", "status", "usage", "last_error", "created_at", "completed_at", "assistant_id", "agent_id"]}
            row["thread_id"] = thread
            rows.append(row)
    await asyncio.to_thread(budget.record, "run_usage", rows)
    return rows
