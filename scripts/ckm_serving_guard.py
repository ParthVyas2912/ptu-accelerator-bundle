"""Irreversible read-only policy for the closed nine-request CKM evaluation."""
import logging
import os
from urllib.parse import urlsplit

logger = logging.getLogger("ckm.serving")
DATA_HOSTS = frozenset({
    "stptuconv7d804f70.blob.core.windows.net",
    "srch-ptu-conversation-7d804f70.search.windows.net",
})
READ_PATHS = frozenset({
    "/", "/api/health", "/api/ingestion/documents", "/api/ingestion/stats",
    "/api/ingestion/filters", "/api/pipelines/automation/config",
})
STATE = {"outbound_denied": 0, "model_dispatches": 0, "last_sql_access_at": None}


class InferenceDisarmed(RuntimeError):
    pass


def check_outbound(method, url):
    target = urlsplit(str(url))
    identity = urlsplit(os.environ.get("IDENTITY_ENDPOINT", ""))
    if identity.hostname and (
        target.scheme, target.netloc, target.path
    ) == (identity.scheme, identity.netloc, identity.path) and method.upper() in {"GET", "POST"}:
        return
    if target.scheme == "https" and target.hostname in DATA_HOSTS and method.upper() in {"GET", "HEAD"}:
        return
    STATE["outbound_denied"] += 1
    logger.error("CKM outbound operation blocked: inference budget closed; no request dispatched")
    raise InferenceDisarmed("CKM_INFERENCE_DISARMED: closed budget9/9; outbound operation not allowed")


def install_transport_guard():
    import aiohttp
    import httpx
    import requests

    sync_send = httpx.Client.send
    async_send = httpx.AsyncClient.send
    session_send = requests.Session.send
    aio_request = aiohttp.ClientSession._request

    def guarded_sync(client, request, *args, **kwargs):
        check_outbound(request.method, request.url)
        return sync_send(client, request, *args, **kwargs)

    async def guarded_async(client, request, *args, **kwargs):
        check_outbound(request.method, request.url)
        return await async_send(client, request, *args, **kwargs)

    def guarded_requests(client, request, *args, **kwargs):
        check_outbound(request.method, request.url)
        return session_send(client, request, *args, **kwargs)

    async def guarded_aio(client, method, url, *args, **kwargs):
        check_outbound(method, url)
        return await aio_request(client, method, url, *args, **kwargs)

    httpx.Client.send = guarded_sync
    httpx.AsyncClient.send = guarded_async
    requests.Session.send = guarded_requests
    aiohttp.ClientSession._request = guarded_aio


def route_allowed(method, path):
    if method == "POST":
        return path == "/api/ingestion/refresh"
    if method != "GET":
        return False
    if path in READ_PATHS:
        return True
    prefix = "/api/ingestion/documents/"
    return path.startswith(prefix) and bool(path[len(prefix):]) and "/" not in path[len(prefix):]


class ReadOnlyGate:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        from starlette.responses import JSONResponse

        async def stamped(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend([
                    (b"x-ckm-inference", b"disarmed-9-of-9"),
                    (b"x-ckm-auto-processing", b"disabled"),
                    (b"x-ckm-queue-worker", b"disabled"),
                    (b"x-ckm-model-dispatches", b"0"),
                    (b"x-ckm-outbound-denied", str(STATE["outbound_denied"]).encode()),
                    (b"x-ckm-serving-pid", str(os.getpid()).encode()),
                    (b"x-ckm-last-sql-access", (STATE["last_sql_access_at"] or "none").encode()),
                ])
            await send(message)

        if not route_allowed(scope["method"], scope["path"]):
            explore = scope["path"].startswith("/api/rag")
            response = JSONResponse(status_code=503, content={
                "error": "CKM_EXPLORE_UNSUPPORTED_AND_DISARMED" if explore else "CKM_INFERENCE_DISARMED",
                "detail": "Read-only deployment. Inference budget9/9 is closed; automatic processing and mutation routes are disabled.",
                "inference_armed": False, "model_requests_dispatched": 0,
            })
            logger.warning("CKM disabled route rejected: %s %s", scope["method"], scope["path"])
            await response(scope, receive, stamped)
            return
        if scope["path"].startswith("/api/ingestion/"):
            from src.api.storage.sql_service import sql_service
            if not sql_service.available:
                response = JSONResponse(status_code=503, content={
                    "error": "CKM_PERSISTENT_SQL_UNAVAILABLE",
                    "detail": "Native SQL is unavailable; refusing an in-memory success response.",
                })
                await response(scope, receive, stamped)
                return
        await self.app(scope, receive, stamped)
