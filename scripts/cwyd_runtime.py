"""Isolated CWYD evaluation launcher; upstream source is never modified.

Runs genuine backend or queue consumer delegating to the upstream
batch_push blueprint. Local-only compatibility bridges account for the
documented Compose stack's current Azurite/settings drift. No cloud keys.
"""
import argparse
import asyncio
import faulthandler
import json
import logging
import os
from pathlib import Path
import re
import sqlite3
import sys
import time

faulthandler.enable()
faulthandler.dump_traceback_later(180, repeat=False)

REPO = Path(r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\chat-with-your-data-solution-accelerator")
BUNDLE = Path(r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\projects\PTU accelerator Bundle")
STATE = Path(os.environ["LOCALAPPDATA"]) / "ptu-eval" / "cwyd"
EVIDENCE = BUNDLE / "evidence" / "cwyd"
STATE.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO / "src"))
LOCAL_PG_HOST, LOCAL_PG_PORT, LOCAL_PG_DATABASE = "127.0.0.1", 15432, "ptu_cwyd"
MAX_MODEL_ATTEMPTS = 16  # Parent reclaimed the unused two attempts; do not reset the ledger.
BUDGET_FILE = EVIDENCE / "evaluation-budget.json"
os.environ.update({
    "AZURE_DB_TYPE": "postgresql",
    "AZURE_INDEX_STORE": "pgvector",
    "AZURE_POSTGRES_ENDPOINT": f"postgresql://{LOCAL_PG_HOST}:{LOCAL_PG_PORT}/{LOCAL_PG_DATABASE}?sslmode=disable",
    "AZURE_POSTGRES_ADMIN_PRINCIPAL_NAME": "cwyd",
    "AZURE_AI_PROJECT_ENDPOINT": "https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj",
    "AZURE_AI_SERVICES_ENDPOINT": "https://edcfoundryhack01.services.ai.azure.com",
    "AZURE_OPENAI_GPT_DEPLOYMENT": "gpt-4.1-mini",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-3-small",
    "AZURE_OPENAI_EMBEDDING_DIMENSIONS": "1536",
    "CWYD_ORCHESTRATOR_NAME": "langgraph",
    "AZURE_DOCUMENTS_CONTAINER": "ptu-cwyd-documents",
    "AZURE_DOC_PROCESSING_QUEUE": "ptu-cwyd-ingestion",
    "AZURE_STORAGE_BLOB_ENDPOINT": "http://127.0.0.1:18100/devstoreaccount1",
    "BACKEND_CORS_ORIGINS": "http://127.0.0.1:5112",
    "AZURE_LOG_LEVEL": "WARNING",
    "LANGSMITH_TRACING": "false",
    "LANGCHAIN_TRACING_V2": "false",
})


def db():
    conn = sqlite3.connect(STATE / "model-budget.sqlite", timeout=30)
    conn.execute("CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY, record TEXT NOT NULL)")
    return conn


def read_budget_policy():
    policy = json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
    limit = policy["model_attempt_limit"]
    if type(limit) is not int or not 0 <= limit <= MAX_MODEL_ATTEMPTS:
        raise RuntimeError("CWYD persistent cap exceeds the authorized harness ceiling or is invalid")
    if type(policy["inference_enabled"]) is not bool or not policy.get("authorization_reference"):
        raise RuntimeError("CWYD persistent authorization policy is invalid")
    return policy


def budget_status():
    policy = read_budget_policy()
    with db() as conn:
        used = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
    return {
        "model_attempt_limit": policy["model_attempt_limit"],
        "model_attempts": used,
        "remaining_attempts": max(0, policy["model_attempt_limit"] - used),
        "inference_enabled": (policy["inference_enabled"]
                              and os.environ.get("CWYD_INFERENCE_DISABLED") != "true"
                              and used < policy["model_attempt_limit"]),
        "requires_new_explicit_authorization": True,
    }


def require_model_allowance(conn):
    policy = read_budget_policy()
    if not policy["inference_enabled"] or os.environ.get("CWYD_INFERENCE_DISABLED") == "true":
        raise RuntimeError("CWYD evaluation is closed; new model allowance requires explicit authorization")
    if conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0] >= policy["model_attempt_limit"]:
        raise RuntimeError(f"CWYD approved hard limit of {policy['model_attempt_limit']} model HTTP attempts reached")


def install_measurement():
    """Count every attempted model HTTP request, including SDK retries."""
    import httpx
    original = httpx.AsyncClient.send

    async def measured(self, request, *args, **kwargs):
        url = request.url
        is_model = (url.host in {"edcfoundryhack01.services.ai.azure.com",
                                "edcfoundryhack01.openai.azure.com"}
                    and "/openai/" in url.path and request.method == "POST")
        if not is_model:
            return await original(self, request, *args, **kwargs)
        payload = json.loads(request.content)
        record = {"operation": url.path.rsplit("/", 1)[-1],
                  "endpoint_host": url.host,
                  "model": payload.get("model"), "stream": payload.get("stream", False),
                  "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "status": None, "usage": None, "latency_ms": None,
                  "retry_header": request.headers.get("x-stainless-retry-count", "0")}
        with db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            require_model_allowance(conn)
            cursor = conn.execute("INSERT INTO calls(record) VALUES (?)", (json.dumps(record),))
            call_id = cursor.lastrowid
        started = time.perf_counter()
        try:
            response = await original(self, request, *args, **kwargs)
            record["status"] = response.status_code
            if not payload.get("stream"):
                await response.aread()
                try:
                    body = response.json()
                    record["usage"] = body.get("usage")
                    if response.status_code >= 400:
                        error = body.get("error", {})
                        record["error"] = {"code": error.get("code"), "param": error.get("param"),
                                           "message": str(error.get("message", ""))[:1000]}
                except (ValueError, AttributeError):
                    record["error"] = "Non-JSON model response"
            return response
        except Exception as exc:
            record["exception_type"] = type(exc).__name__
            raise
        finally:
            record["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
            record["id"] = call_id
            with db() as conn:
                conn.execute("UPDATE calls SET record=? WHERE id=?", (json.dumps(record), call_id))
            print("CWYD_MODEL " + json.dumps(record), flush=True)

    httpx.AsyncClient.send = measured


def install_local_storage_bridge():
    """Local emulator auth only; never changes an Azure endpoint or credential."""
    from azure.storage.blob.aio import BlobServiceClient, ContainerClient, BlobClient
    from azure.storage.queue.aio import QueueServiceClient, QueueClient
    # This is the public Azurite emulator value already in upstream Compose.
    # Parse only into process memory; never write or print it.
    compose = (REPO / "docker" / "docker-compose.dev.yml").read_text(encoding="utf-8")
    emulator_key = re.search(r"AccountKey=([^;]+);", compose).group(1)
    for cls in [BlobServiceClient, ContainerClient, BlobClient, QueueServiceClient, QueueClient]:
        original = cls.__init__
        def local_init(self, *args, _original=original, **kwargs):
            url = kwargs.get("account_url", args[0] if args else "")
            if str(url).startswith(("http://127.0.0.1:18100/", "http://127.0.0.1:18101/")):
                kwargs["credential"] = emulator_key
            _original(self, *args, **kwargs)
        cls.__init__ = local_init
    import functions.core.storage_endpoints as endpoints
    original_resolve = endpoints.resolve_storage_endpoints
    def local_endpoints(settings):
        if settings.storage_blob_endpoint.startswith("http://127.0.0.1:18100/"):
            return settings.storage_blob_endpoint, settings.storage_blob_endpoint.replace(":18100/", ":18101/")
        return original_resolve(settings)
    endpoints.resolve_storage_endpoints = local_endpoints


def install_local_database_bridge():
    """Skip the Azure-only password callback for the exact local trust DB."""
    import asyncpg
    from urllib.parse import urlparse
    original = asyncpg.create_pool
    def local_pool(*args, **kwargs):
        endpoint = kwargs.get("dsn", args[0] if args else "")
        parsed = urlparse(str(endpoint))
        if (parsed.scheme == "postgresql" and parsed.hostname == LOCAL_PG_HOST
                and parsed.port == LOCAL_PG_PORT and parsed.path == "/" + LOCAL_PG_DATABASE):
            kwargs.pop("password", None)
            kwargs["max_size"] = 2
        return original(*args, **kwargs)
    asyncpg.create_pool = local_pool
    # Native Azure CLI can be slower than the SDK's default ten-second limit
    # while seven builds share this host. Pin its subscription and bound it.
    from azure.identity.aio import AzureCliCredential
    original_credential_init = AzureCliCredential.__init__
    def credential_init(self, *args, **kwargs):
        kwargs.setdefault("process_timeout", 90)
        kwargs.setdefault("subscription", "1feb53b2-854a-4ea7-b5a6-709b7d804f70")
        original_credential_init(self, *args, **kwargs)
    AzureCliCredential.__init__ = credential_init


def install_account_endpoint_bridge():
    """Optional account-embedding endpoint correction; unchanged Entra identity.

    The contract supplies this account's Azure OpenAI endpoint. The Foundry
    SDK documents base_url override on get_openai_client, and Microsoft Learn's
    Entra v1 example uses this endpoint shape with the same ai.azure.com scope.
    Project chat calls and all unrelated endpoints remain untouched.
    """
    if os.environ.get("CWYD_USE_ACCOUNT_OPENAI_ENDPOINT") != "true":
        return
    from azure.ai.projects.aio import AIProjectClient
    import httpx
    original = AIProjectClient.get_openai_client
    def account_client(self, *args, **kwargs):
        kwargs.setdefault("max_retries", 1)
        kwargs.setdefault("timeout", httpx.Timeout(90, connect=30))
        if kwargs.get("base_url", "").rstrip("/") == "https://edcfoundryhack01.services.ai.azure.com/openai/v1":
            kwargs["base_url"] = "https://edcfoundryhack01.openai.azure.com/openai/v1"
        return original(self, *args, **kwargs)
    AIProjectClient.get_openai_client = account_client


async def run_worker():
    from azure.storage.blob.aio import ContainerClient
    from azure.storage.queue.aio import QueueClient
    from azure.core.exceptions import ResourceExistsError
    from backend.core.settings import get_settings
    from functions.batch_push.blueprint import _execute
    from functions.core.contracts import BatchPushQueueMessage
    import base64
    settings = get_settings()
    async with ContainerClient(account_url=settings.storage.storage_blob_endpoint,
                               container_name=settings.storage.documents_container) as container:
        try:
            await container.create_container()
        except ResourceExistsError:
            pass
    async with QueueClient(account_url="http://127.0.0.1:18101/devstoreaccount1",
                           queue_name=settings.storage.doc_processing_queue) as queue:
        try:
            await queue.create_queue()
        except ResourceExistsError:
            pass
        print(json.dumps({"worker": "upstream batch_push._execute", "pid": os.getpid(), "ready": True}), flush=True)
        faulthandler.cancel_dump_traceback_later()
        while True:
            async for message in queue.receive_messages(messages_per_page=1, visibility_timeout=120):
                started = time.perf_counter()
                raw = message.content
                if not raw.lstrip().startswith("{"):
                    raw = base64.b64decode(raw).decode()
                request = BatchPushQueueMessage.model_validate_json(raw)
                record = {"filename": request.filename, "started_epoch": time.time(), "dequeue_count": message.dequeue_count}
                try:
                    documents = await _execute(request, settings)
                    record.update(status="indexed", chunks=len(documents))
                except Exception as exc:
                    record.update(status="failed", error_type=type(exc).__name__)
                # First-pass safety: never blindly repeat a paid failed batch.
                await queue.delete_message(message)
                record["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
                filename = EVIDENCE / ("ingestion-" + str(int(time.time() * 1000)) + ".json")
                filename.write_text(json.dumps(record, indent=2), encoding="utf-8")
                print(json.dumps(record), flush=True)
            await asyncio.sleep(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["backend", "worker", "export", "budget-status"])
    args = parser.parse_args()
    status = budget_status()
    if args.mode == "budget-status":
        print(json.dumps(status), flush=True)
        return
    if args.mode == "worker" and not status["inference_enabled"]:
        parser.exit(2, "CWYD ingestion worker is disabled; queued data is untouched. Explicit new allowance is required.\n")
    if args.mode == "export":
        with db() as conn:
            calls = [json.loads(row[0]) for row in conn.execute("SELECT record FROM calls ORDER BY id")]
        (EVIDENCE / "model-calls.json").write_text(json.dumps(calls, indent=2), encoding="utf-8")
        result_path = EVIDENCE / "result.json"
        if result_path.exists():
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["model_attempts"] = len(calls)
            result["model_attempt_limit"] = status["model_attempt_limit"]
            result["remaining_first_pass_attempts"] = status["remaining_attempts"]
            result["evaluation_inference_enabled"] = status["inference_enabled"]
            result["measured_model_usage"] = calls
            returned = [call["usage"] for call in calls if call.get("usage")]
            result["usage_summary"] = {
                "tokens_reported": bool(returned),
                "calls_reporting_usage": len(returned),
                "sum_returned_prompt_tokens": sum(u.get("prompt_tokens", u.get("input_tokens", 0)) for u in returned) if returned else None,
                "sum_returned_output_tokens": sum(u.get("completion_tokens", u.get("output_tokens", 0)) for u in returned)
                    if any("completion_tokens" in u or "output_tokens" in u for u in returned) else None,
                "sum_returned_total_tokens": sum(u.get("total_tokens", 0) for u in returned) if returned else None,
                "successful_model_responses": sum(c.get("status") == 200 for c in calls),
                "retried_calls": sum(int(c.get("retry_header", 0)) > 0 for c in calls),
                "http_401": sum(c.get("status") == 401 for c in calls),
                "http_429": sum(c.get("status") == 429 for c in calls),
                "upstream_http_5xx": sum(500 <= (c.get("status") or 0) < 600 for c in calls),
                "connection_timeouts": sum(c.get("exception_type") == "ConnectTimeout" for c in calls),
                "estimated_tokens_presented_as_actual": False,
            }
            assignment_path = BUNDLE / "evidence" / "preflight" / "inference-role-assignment.json"
            if assignment_path.exists():
                assignment = json.loads(assignment_path.read_text(encoding="utf-8"))
                result["parent_role_assignment"] = {key: assignment.get(key) for key in
                                                    ["id", "principalId", "roleDefinitionId", "scope", "createdOn"]}
                result["required_unblock"]["parent_assignment_performed"] = True
                result["required_unblock"]["role_request_status"] = (
                    "parent executed; CWYD did not duplicate; successful account model calls verified"
                    if any(c.get("status") == 200 for c in calls)
                    else "parent executed; CWYD did not duplicate; data-plane retest required"
                )
            result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps({"attempts": len(calls), "calls": calls}, indent=2))
        return
    logging.basicConfig(level=logging.WARNING)
    install_measurement()
    install_local_storage_bridge()
    install_local_database_bridge()
    install_account_endpoint_bridge()
    (STATE / f"{args.mode}.pid").write_text(str(os.getpid()), encoding="ascii")
    if args.mode == "worker":
        asyncio.run(run_worker())
    else:
        import uvicorn
        from backend.app import app
        from starlette.responses import JSONResponse

        @app.middleware("http")
        async def evaluation_read_only(request, call_next):
            if request.method not in {"GET", "HEAD", "OPTIONS"} and request.url.path.startswith("/api/"):
                current = budget_status()
                if not current["inference_enabled"]:
                    return JSONResponse(
                        status_code=503,
                        content={"code": "cwyd_evaluation_closed",
                                 "detail": "CWYD evaluation is closed. Read-only access remains available; new model allowance requires explicit authorization.",
                                 **current},
                    )
            return await call_next(request)

        print(json.dumps({"backend_pid": os.getpid(), "bind": "127.0.0.1:8112"}), flush=True)
        faulthandler.cancel_dump_traceback_later()
        uvicorn.run(app, host="127.0.0.1", port=8112, log_level="warning")


if __name__ == "__main__":
    main()
