"""Budget actual HTTP attempts; record usage only, never credentials or prompts.

Specialist Responses calls conservatively reserve three units: the outbound
request plus allowances for a hosted Search embedding and a hosted model turn.
Reserved units are not claimed as measured server-side requests.
"""
import json
import os
from pathlib import Path
import sqlite3
from time import perf_counter
from datetime import datetime, timezone
from contextlib import contextmanager

import httpx

ALLOWED_HOSTS = {
    "aif-ccptu1feb0911.openai.azure.com",
    "aif-ccptu1feb0911.services.ai.azure.com",
}
LIMIT = 12
ALLOWANCE_CLOSED = True
_installed = False


@contextmanager
def database():
    path = Path(os.environ["CHATBOT_USAGE_DB"])
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.execute("""CREATE TABLE IF NOT EXISTS requests (
      id INTEGER PRIMARY KEY, started TEXT, kind TEXT, model TEXT, agent TEXT,
      units INTEGER, status INTEGER, elapsed_ms REAL, input_tokens INTEGER,
      output_tokens INTEGER, cached_tokens INTEGER, tool_names TEXT, error TEXT
    )""")
    try:
        with db:
            yield db
    finally:
        db.close()


def prepare(request):
    path = request.url.path.rstrip("/")
    kind = next((k for k in ("embeddings", "responses", "chat/completions")
                 if path.endswith("/" + k)), None)
    if request.method != "POST" or not kind:
        return request, None
    if request.url.host not in ALLOWED_HOSTS:
        raise RuntimeError("Model request blocked: endpoint is not the approved isolated chatbot account.")
    if ALLOWANCE_CLOSED:
        raise RuntimeError("Chatbot allowance is closed; a new explicit operator allowance is required.")
    body = json.loads(request.content)
    agent = str((body.get("agent_reference") or {}).get("name", ""))
    specialist = agent.startswith(("ptu-chatbot-product-", "ptu-chatbot-policy-"))
    units = 3 if specialist else 1
    if kind == "responses":
        body["max_tool_calls"] = 1
        body["max_output_tokens"] = min(int(body.get("max_output_tokens") or 2048), 2048)
        if not body.get("agent_reference"):
            body.setdefault("reasoning", {"effort": "low"})
        headers = dict(request.headers)
        headers.pop("content-length", None)
        request = httpx.Request(
            request.method, request.url, headers=headers,
            content=json.dumps(body).encode(), extensions=request.extensions,
        )
    model = str(body.get("model") or ("gpt-5.4-mini" if kind == "responses" else "unknown"))
    if os.getenv("CHATBOT_METERING_BACKEND") == "cosmos":
        from cosmos_budget import store
        request_id = store().reserve({
            "started": datetime.now(timezone.utc).isoformat(),
            "kind": kind, "model": model, "agent": agent, "units": units,
        })
        return request, request_id
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        used = db.execute("SELECT COALESCE(SUM(units),0) FROM requests").fetchone()[0]
        if used + units > LIMIT:
            raise RuntimeError(f"Chatbot request budget exhausted: {used}/{LIMIT} conservative units already used.")
        row = db.execute(
            "INSERT INTO requests(started,kind,model,agent,units) VALUES(?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), kind, model, agent, units),
        )
        request_id = row.lastrowid
    return request, request_id


def finish(request_id, response, elapsed, error=None):
    if request_id is None:
        return
    payload = {}
    if response is not None:
        try:
            payload = response.json()
        except ValueError:
            # Failed SSE streams can still have HTTP200.
            for line in response.text.splitlines():
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[6:])
                        if event.get("type") in ("response.completed", "response.incomplete", "response.failed"):
                            payload = event.get("response", {})
                        elif event.get("type") == "error":
                            payload = {"error": event.get("error") or event}
                    except (ValueError, TypeError):
                        pass
    usage = payload.get("usage") or {}
    details = usage.get("input_tokens_details") or usage.get("prompt_tokens_details") or {}
    names = [
        {"type": item.get("type"), "name": item.get("name")}
        for item in payload.get("output", [])
        if isinstance(item, dict) and ("call" in str(item.get("type", "")))
    ]
    # Save only an error code, never an arbitrary server echo of request headers.
    server_error = payload.get("error") or {}
    if isinstance(server_error, dict):
        error = error or server_error.get("code")
    if os.getenv("CHATBOT_METERING_BACKEND") == "cosmos":
        from cosmos_budget import store
        store().finish(request_id, {
            "status": response.status_code if response is not None else None,
            "elapsed_ms": round(elapsed * 1000, 3),
            "input_tokens": usage.get("input_tokens", usage.get("prompt_tokens")),
            "output_tokens": usage.get("output_tokens", usage.get("completion_tokens")),
            "cached_tokens": details.get("cached_tokens"),
            "tool_names": names, "error": error,
        })
        return
    with database() as db:
        db.execute(
            """UPDATE requests SET status=?,elapsed_ms=?,input_tokens=?,
            output_tokens=?,cached_tokens=?,tool_names=?,error=? WHERE id=?""",
            (
                response.status_code if response is not None else None,
                round(elapsed * 1000, 3),
                usage.get("input_tokens", usage.get("prompt_tokens")),
                usage.get("output_tokens", usage.get("completion_tokens")),
                details.get("cached_tokens"),
                json.dumps(names), error, request_id,
            ),
        )


def install():
    global _installed
    if _installed:
        return
    backend = os.getenv("CHATBOT_METERING_BACKEND", "sqlite")
    if backend not in ("sqlite", "cosmos"):
        raise RuntimeError("Unsupported metering backend.")
    if backend == "sqlite":
        with database():
            pass
    # Avoid hidden OpenAI SDK retry attempts. Any explicit retry still crosses
    # the metered transport and consumes a fresh budget reservation.
    import openai
    def no_retry_initializer(original):
        def initialize(self, *args, **kwargs):
            kwargs["max_retries"] = 0
            return original(self, *args, **kwargs)
        return initialize
    for client_type in (openai.OpenAI, openai.AsyncOpenAI, openai.AzureOpenAI, openai.AsyncAzureOpenAI):
        client_type.__init__ = no_retry_initializer(client_type.__init__)
    original_send = httpx.Client.send
    original_async_send = httpx.AsyncClient.send

    def send(self, request, *args, **kwargs):
        request, request_id = prepare(request)
        started = perf_counter()
        try:
            response = original_send(self, request, *args, **kwargs)
            if request_id is not None:
                response.read()
            finish(request_id, response, perf_counter() - started)
            return response
        except Exception as exc:
            finish(request_id, None, perf_counter() - started, type(exc).__name__)
            raise

    async def async_send(self, request, *args, **kwargs):
        request, request_id = prepare(request)
        started = perf_counter()
        try:
            response = await original_async_send(self, request, *args, **kwargs)
            if request_id is not None:
                await response.aread()
            finish(request_id, response, perf_counter() - started)
            return response
        except Exception as exc:
            finish(request_id, None, perf_counter() - started, type(exc).__name__)
            raise

    httpx.Client.send = send
    httpx.AsyncClient.send = async_send
    _installed = True
