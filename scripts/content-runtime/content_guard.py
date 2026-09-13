"""Cross-process request admission and metadata-only CU/OpenAI evidence.

The production SDKs still send and consume real requests/responses. Response
bodies are inspected in memory; prompts, documents and credentials aren't logged.
The ledger is durable across restarts, outside OneDrive. A reservation counts
against the cap even if a transport fails before the server receives it.
"""
import datetime
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlsplit

AI = "aif-ptuv-content-260911"
ALLOWED = {
    AI + ".openai.azure.com",
    AI + ".cognitiveservices.azure.com",
    AI + ".services.ai.azure.com",
    "stptuvcontent260911.blob.core.windows.net",
    "stptuvcontent260911.queue.core.windows.net",
    "appcs-ptuv-content-260911.azconfig.io",
}
CLOUD_SUFFIXES = (".openai.azure.com", ".cognitiveservices.azure.com",
                  ".services.ai.azure.com", ".blob.core.windows.net",
                  ".queue.core.windows.net", ".azconfig.io")
CAP = 17


def connect():
    path = Path(os.environ["CONTENT_REQUEST_LEDGER"])
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.execute("""CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY, kind TEXT, service TEXT, pid INTEGER,
        started TEXT, method TEXT, host TEXT, path TEXT, model TEXT,
        status INTEGER, elapsed_ms REAL, usage TEXT, pages INTEGER,
        operation TEXT, error TEXT)""")
    return db


def redact(value):
    text = str(value)
    secret = os.environ.get("APP_COSMOS_CONNSTR")
    if secret:
        text = text.replace(secret, "[REDACTED_MONGO]")
    text = re.sub(r"mongodb(?:\+srv)?://[^\s\"'<>]+", "[REDACTED_MONGO]", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",
                  "[REDACTED_TOKEN]", text)
    text = re.sub(r"(?i)(AccountKey|api-key|Authorization)([=:]\s*)[^\s,;}]+",
                  r"\1\2[REDACTED]", text)
    return text


def reserve(method, url, body=b""):
    parsed = urlsplit(str(url))
    host, path = parsed.hostname or "", parsed.path
    if host.endswith(CLOUD_SUFFIXES) and host not in ALLOWED:
        raise RuntimeError("CONTENT_GUARD: unapproved Azure data endpoint blocked")
    model_call = method.upper() == "POST" and any(
        part in path for part in ("/responses", "/chat/completions", "/embeddings"))
    cu = "/contentunderstanding/" in path
    if os.environ.get("CONTENT_INFERENCE_DISARMED") == "1" and (
            model_call or cu or host.endswith((
                ".openai.azure.com", ".cognitiveservices.azure.com", ".services.ai.azure.com"))):
        raise RuntimeError("CONTENT_GUARD: inference hard-disarmed")
    if not model_call and not cu:
        return None
    if host not in ALLOWED or parsed.scheme != "https":
        raise RuntimeError("CONTENT_GUARD: unapproved inference endpoint blocked")
    model = None
    if model_call:
        try:
            payload = json.loads(body)
            model = payload.get("model")
        except (ValueError, TypeError):
            pass
        match = re.search(r"/deployments/([^/]+)/", path)
        model = model or (match.group(1) if match else None)
        if model != "gpt-5.1":
            raise RuntimeError("CONTENT_GUARD: model must be approved gpt-5.1")
    kind = "model" if model_call else (
        "cu-analyze" if method.upper() == "POST" else (
            "cu-poll" if "/analyzerResults/" in path else "cu-metadata"))
    scope = {}
    if os.environ.get("CONTENT_SCOPE_WORKER") == "1":
        from isolated_scope import inference_scope
        scope = inference_scope(kind)
    if os.environ.get("CONTENT_BUDGET_BACKEND") == "blob":
        import cloud_budget
        row = cloud_budget.reserve({
            "kind": kind, "service": os.environ.get("CONTENT_SERVICE", "unknown"),
            "pid": os.getpid(), "started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "method": method, "host": host, "path": path, "model": model, **scope,
        }, CAP)
        return row, time.perf_counter()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        if model_call and db.execute(
                "SELECT COUNT(*) FROM requests WHERE kind='model'").fetchone()[0] >= CAP:
            raise RuntimeError(f"CONTENT_GUARD: {CAP}-request lifetime cap reached")
        row = db.execute("""INSERT INTO requests
            (kind,service,pid,started,method,host,path,model)
            VALUES(?,?,?,?,?,?,?,?)""", (
                kind, os.environ.get("CONTENT_SERVICE", "unknown"), os.getpid(),
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                method, host, path, model)).lastrowid
    return row, time.perf_counter()


def finish(ticket, status=None, content=b"", error=None):
    if ticket is None:
        return
    usage, pages, operation = [], None, None
    try:
        data = [json.loads(content)]
    except (ValueError, TypeError, UnicodeDecodeError):
        data = []
        # Streaming is buffered, not fabricated; capture the actual final usage.
        for line in content.splitlines():
            if line.startswith(b"data: "):
                try:
                    data.append(json.loads(line[6:]))
                except ValueError:
                    pass

    def walk(obj):
        nonlocal pages, operation, error
        if isinstance(obj, dict):
            if "usage" in obj:
                usage.append(obj["usage"])
            if isinstance(obj.get("pages"), list):
                pages = max(pages or 0, len(obj["pages"]))
            if "id" in obj and "status" in obj:
                operation = str(obj["id"])
            if isinstance(obj.get("error"), dict):
                err = obj["error"]
                error = redact(str(err.get("code")) + ": " + str(err.get("message")))[:1500]
            for key, value in obj.items():
                if key != "usage":
                    walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)
    for obj in data:
        walk(obj)
    if os.environ.get("CONTENT_BUDGET_BACKEND") == "blob":
        import cloud_budget
        cloud_budget.finish(ticket[0], {
            "status": status, "elapsed_ms": round((time.perf_counter() - ticket[1]) * 1000, 3),
            "usage": usage or None, "pages": pages, "operation": operation,
            "error": redact(error)[:1500] if error else None})
        return
    with connect() as db:
        db.execute("""UPDATE requests SET status=?,elapsed_ms=?,usage=?,
            pages=?,operation=?,error=? WHERE id=?""", (
                status, round((time.perf_counter() - ticket[1]) * 1000, 3),
                json.dumps(usage) if usage else None, pages, operation,
                redact(error)[:1500] if error else None, ticket[0]))


def install():
    import httpx
    import requests
    # The shared Windows host measured >13 seconds just launching Azure CLI.
    # Preserve Entra authentication, only increase the SDK's local process timeout.
    from azure.identity import AzureCliCredential
    from azure.identity.aio import AzureCliCredential as AsyncAzureCliCredential
    from azure.identity import ManagedIdentityCredential
    from azure.identity.aio import ManagedIdentityCredential as AsyncManagedIdentityCredential
    if os.environ.get("CONTENT_BUDGET_BACKEND") == "blob":
        # Upstream API constructs ManagedIdentityCredential(client_id=None).
        # With UAI-only ACA that selects a nonexistent system identity. Bind the
        # app's assigned client ID without changing auth type or permissions.
        for identity_class in (ManagedIdentityCredential, AsyncManagedIdentityCredential):
            identity_init = identity_class.__init__

            def managed_identity_init(self, *args, _original=identity_init, **kwargs):
                if not kwargs.get("client_id"):
                    kwargs["client_id"] = os.environ["AZURE_CLIENT_ID"]
                _original(self, *args, **kwargs)

            identity_class.__init__ = managed_identity_init
    for credential_class in (AzureCliCredential, AsyncAzureCliCredential):
        original_init = credential_class.__init__

        def credential_init(self, *args, _original=original_init, **kwargs):
            kwargs["process_timeout"] = max(kwargs.get("process_timeout", 10), 120)
            _original(self, *args, **kwargs)

        credential_class.__init__ = credential_init
    sync_send = httpx.Client._send_single_request
    async_send = httpx.AsyncClient._send_single_request
    requests_send = requests.Session.send

    def sync(self, request):
        ticket = reserve(request.method, request.url, request.content)
        try:
            response = sync_send(self, request)
            if ticket:
                finish(ticket, response.status_code, response.read())
            return response
        except BaseException as exc:
            finish(ticket, error=type(exc).__name__ + ": " + redact(exc))
            raise

    async def asynchronous(self, request):
        ticket = reserve(request.method, request.url, request.content)
        try:
            response = await async_send(self, request)
            if ticket:
                finish(ticket, response.status_code, await response.aread())
            return response
        except BaseException as exc:
            finish(ticket, error=type(exc).__name__ + ": " + redact(exc))
            raise

    def request_send(self, request, **kwargs):
        ticket = reserve(request.method, request.url, request.body or b"")
        try:
            response = requests_send(self, request, **kwargs)
            if ticket:
                finish(ticket, response.status_code, response.content)
            return response
        except BaseException as exc:
            finish(ticket, error=type(exc).__name__ + ": " + redact(exc))
            raise

    httpx.Client._send_single_request = sync
    httpx.AsyncClient._send_single_request = asynchronous
    requests.Session.send = request_send
    if os.environ.get("CONTENT_BUDGET_BACKEND") == "blob":
        import cloud_budget  # Import/implementation must exist or fail closed.
    else:
        with connect():
            pass
