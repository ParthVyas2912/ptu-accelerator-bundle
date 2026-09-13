"""Bounded evaluation of ORIGINAL Modernize agent components, NOT full deployment.

Only the repository convert_script/SqlAgents orchestration performs inference.
Persistence is an explicit recording test double: no UI/batch/blob E2E claim.
Run with the isolated Modernize venv after official requirements are installed.
No credentials are stored. All cloud deletes are blocked.
"""
import asyncio
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import uuid4

BUNDLE = Path(__file__).resolve().parents[1]
REPO = BUNDLE.parent.parent / "repo" / "Modernize-your-code-solution-accelerator"
BACKEND = REPO / "src" / "backend"
OUT = BUNDLE / "evidence" / "modernize"
if (OUT/"cloud-budget-snapshot.json").exists():
    raise SystemExit("Cloud evaluation owns the durable global budget; do not start a separate component ledger.")
LEDGER = OUT / "component-evaluation.json"
ENDPOINT = "https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj"
os.environ["APP_ENV"] = "dev"
os.environ["AI_PROJECT_ENDPOINT"] = ENDPOINT
for agent in ["MIGRATOR", "PICKER", "FIXER", "SEMANTIC_VERIFIER", "SYNTAX_CHECKER"]:
    os.environ[f"{agent}_AGENT_MODEL_DEPLOY"] = "gpt-5.1"
os.environ["AZURE_BASIC_LOGGING_LEVEL"] = "WARNING"
os.environ["AZURE_PACKAGE_LOGGING_LEVEL"] = "WARNING"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

# Import the pinned repository implementation, not a replacement model script.
from azure.core.pipeline.transport import AioHttpTransport
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient
from common.models.api import FileRecord, ProcessStatus
from sql_agents.agents.agent_config import AgentBaseConfig
from sql_agents.helpers.agents_manager import SqlAgents
import sql_agents.convert_script as conversion
from sql_agents.helpers.comms_manager import CommsManager

logging.basicConfig(level=logging.WARNING)
for name in ["azure", "semantic_kernel", "sql_agents"]:
    logging.getLogger(name).setLevel(logging.WARNING)

state = {
    "scope": "original-agent-component-with-recording-persistence-not-full-app",
    "model": "gpt-5.1", "version": "2025-11-13", "sku": "GlobalStandard",
    "endpoint": ENDPOINT,
    "model_request_cap": 12,
    "model_request_events": [], "run_usage": [], "tests": [],
    "created_agents": [], "threads": [], "deletes_blocked": 0,
    "adaptations": [
        "Async AzureCliCredential for async Foundry SDK; no secret files.",
        "Recording batch-service test double instead of Cosmos/Blob (component only).",
        "Disable orchestration retries and all cloud deletion for bounded evaluation.",
        "Guard model-start and tool-continuation HTTP requests at transport boundary.",
    ],
}
protocol_ledger = OUT / "migrator-protocol.json"
prior_protocol_calls = (len(json.loads(protocol_ledger.read_text(encoding="utf-8")).get("calls", []))
                        if protocol_ledger.exists() else 0)
state["prior_protocol_model_calls"] = prior_protocol_calls
state["model_request_cap"] = 12 - prior_protocol_calls
if LEDGER.exists():
    prior = json.loads(LEDGER.read_text(encoding="utf-8"))
    if prior.get("model_request_events"):
        raise SystemExit("Existing model-call ledger found; refusing an accidental rerun.")


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


class BoundedTransport(AioHttpTransport):
    async def send(self, request, **kwargs):
        path = urlparse(request.url).path
        if request.method.upper() == "DELETE":
            state["deletes_blocked"] += 1
            save()
            raise RuntimeError("Automatic Azure deletes forbidden by evaluation contract")
        if "/threads/" in path:
            thread_id = path.split("/threads/")[1].split("/")[0]
            if thread_id and thread_id not in state["threads"]:
                state["threads"].append(thread_id)
        consuming = request.method.upper() == "POST" and (
            path.endswith("/runs") or path.endswith("/submit_tool_outputs")
        )
        event = None
        if consuming:
            if len(state["model_request_events"]) >= state["model_request_cap"]:
                raise RuntimeError("Initial model HTTP request cap of 12 reached")
            event = {"attempt": len(state["model_request_events"]) + 1,
                     "path": path, "started_at": datetime.now(timezone.utc).isoformat()}
            state["model_request_events"].append(event)
            save()  # Persist before sending, including failures/timeouts.
        started = time.monotonic()
        try:
            result = await super().send(request, **kwargs)
            if event is not None:
                event.update(http_status=result.status_code,
                             response_headers_latency_seconds=round(time.monotonic()-started, 3))
            return result
        except Exception as exc:
            if event is not None:
                event["error_type"] = type(exc).__name__
            raise
        finally:
            if event is not None:
                save()


class RecordingBatchService:
    def __init__(self):
        self.logs = []

    async def create_file_log(self, file_id, description, last_candidate, log_type,
                              agent_type, author_role):
        self.logs.append({
            "file_id": file_id, "description": description, "last_candidate": last_candidate,
            "log_type": log_type.value, "agent_type": agent_type.value,
            "author_role": author_role.value,
        })


class BoundedComms(CommsManager):
    def __init__(self, *args, **kwargs):
        kwargs["max_retries"] = 1
        super().__init__(*args, **kwargs)

    async def cleanup(self):
        # The upstream cleanup deletes Foundry threads. Retain evidence, do not delete.
        return None


conversion.CommsManager = BoundedComms
status_events = []
conversion.send_status_update = lambda status: status_events.append(
    {k: getattr(v, "value", str(v)) for k, v in vars(status).items()}
)


def native_parse(sql):
    result = subprocess.run(
        [str(BACKEND / "sql_agents" / "tools" / "win-x64" / "tsqlParser.exe"),
         "--string", sql], capture_output=True, text=True, timeout=45)
    try:
        return {"exit_code": result.returncode, "errors": json.loads(result.stdout)}
    except ValueError:
        return {"exit_code": result.returncode, "error": "parser output was not JSON"}


async def usage_snapshot(client):
    seen = {item["run_id"] for item in state["run_usage"]}
    for thread in list(state["threads"]):
        try:
            async for run in client.agents.runs.list(thread_id=thread):
                if run.id not in seen:
                    details = run.as_dict()
                    state["run_usage"].append({
                        "run_id": run.id, "thread_id": thread, "status": str(run.status),
                        "usage": details.get("usage"), "last_error": details.get("last_error"),
                        "created_at": details.get("created_at"),
                        "completed_at": details.get("completed_at"),
                    })
        except Exception as exc:
            state.setdefault("usage_errors", []).append(type(exc).__name__)
    save()


async def main():
    save()
    credential = AzureCliCredential(process_timeout=150)
    transport = BoundedTransport()
    client = AIProjectClient(endpoint=ENDPOINT, credential=credential,
                             transport=transport, retry_total=0)
    config = AgentBaseConfig(client, "informix", "tsql")
    try:
        agents = await SqlAgents.create(config)
        state["created_agents"] = [{"id": x.id, "name": x.name} for x in agents.agents]
        save()
        cases = [
            ("malformed", "SELEC customer_id FROM WHERE;", "Reject invalid input with diagnostic"),
            ("repo-nvl", (REPO/"data/informix/simple/q3_informix.sql").read_text(encoding="utf-8-sig"),
             "Translate correlated query and NVL; valid T-SQL; compare null/duplicate synthetic rows"),
        ]
        batch_id = uuid4()
        for name, sql, expected in cases:
            if len(state["model_request_events"]) >= state["model_request_cap"]:
                state["tests"].append({"id": name, "expected": expected, "actual": "Not run: request cap"})
                continue
            file_id = uuid4()
            now = datetime.now(timezone.utc)
            record = FileRecord(file_id, batch_id, name+".sql", "", "", ProcessStatus.IN_PROGRESS,
                                0, 0, now, now)
            service = RecordingBatchService()
            status_events.clear()
            started = time.monotonic()
            before = len(state["model_request_events"])
            test = {"id": name, "expected": expected, "source": sql, "file_id": str(file_id)}
            try:
                target = await asyncio.wait_for(
                    conversion.convert_script(sql, record, service, agents), timeout=360)
                test["target"] = target
                test["native_tsql_parse"] = native_parse(target) if target else None
                test["actual"] = "target returned" if target else "no target returned"
            except Exception as exc:
                test["actual"] = type(exc).__name__
                test["error"] = str(exc)[:1600]
            test.update(elapsed_seconds=round(time.monotonic()-started, 3),
                        model_http_attempts=len(state["model_request_events"])-before,
                        logs=service.logs, status_events=list(status_events))
            state["tests"].append(test)
            await usage_snapshot(client)
            save()
            print(json.dumps({"test": name, "actual": test["actual"],
                              "model_http_attempts": test["model_http_attempts"]}), flush=True)
    except Exception as exc:
        state["initialization_error"] = {"type": type(exc).__name__, "detail": str(exc)[:1600]}
        save()
        print(json.dumps(state["initialization_error"]), flush=True)
    finally:
        await client.close()
        await credential.close()
        save()


if __name__ == "__main__":
    asyncio.run(main())
