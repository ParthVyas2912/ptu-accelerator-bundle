"""Evaluation-only HTTPX inference meter and persistent 24-request hard gate.

No prompts, response text, headers, keys or tokens are persisted. Usage is copied
only from returned API usage fields. This is not a replacement inference client.
"""
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

import httpx

STATE = Path(os.environ["MACAE_STATE_DIR"])
STATE.mkdir(parents=True, exist_ok=True)
DB = STATE / "model-budget.sqlite"
EVIDENCE = Path(os.environ["MACAE_EVIDENCE_DIR"]) / "model-calls.jsonl"
LIMIT = 24
ALLOWED = {"ptumacae7d804f70.services.ai.azure.com", "ptumacae7d804f70.openai.azure.com"}


@contextmanager
def database():
    conn = sqlite3.connect(DB, timeout=20)
    try:
        with conn:
            conn.execute("CREATE TABLE IF NOT EXISTS calls(id INTEGER PRIMARY KEY, record TEXT NOT NULL)")
            yield conn
    finally:
        conn.close()


def reserve_record(record):
    """Default local ledger. Cloud runner replaces this with Cosmos ETag CAS."""
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        count = conn.execute("SELECT count(*) FROM calls").fetchone()[0]
        if count >= LIMIT:
            raise RuntimeError(f"MACAE live inference allowance exhausted: {LIMIT} requests including retries")
        ident = count + 1
        record["call_number"] = ident
        conn.execute("INSERT INTO calls(id,record) VALUES (?,?)", (ident, json.dumps(record)))
        return ident


def persist_record(ident, record):
    with database() as conn:
        conn.execute("UPDATE calls SET record=? WHERE id=?", (json.dumps(record), ident))


def reject_unmetered_search(request):
    path = request.url.path.lower()
    if (request.method == "POST" and request.url.host.endswith(".search.windows.net")
            and ("/knowledgebases/" in path or "/retrieve" in path)):
        raise RuntimeError("MACAE remote KB reasoning blocked until service-side call metering is coordinated")


def is_inference(request):
    path = request.url.path.lower().rstrip("/")
    return request.method == "POST" and any(
        path.endswith(s) for s in ("/responses", "/chat/completions", "/completions", "/embeddings", "/images/generations")
    )


class Meter:
    def __init__(self, request):
        if request.url.host not in ALLOWED:
            raise RuntimeError("MACAE inference blocked: unapproved endpoint")
        self.start = time.perf_counter()
        self.buffer = b""
        self.event_stream = False
        self.capture_overflow = False
        self.finished = False
        try:
            body = json.loads(request.content)
        except Exception:
            body = {}
        # Search knowledge-base reasoning runs remotely and cannot be bounded by
        # this client meter. Do not launch it under the bounded evaluation budget.
        for tool in body.get("tools") or []:
            if tool.get("type") == "mcp" and "search.windows.net" in tool.get("server_url", ""):
                raise RuntimeError("MACAE remote KB reasoning needs separately coordinated call allowance and metering")
        self.record = {
            "model_requested": body.get("model"),
            "model_returned": None,
            "response_id": None,
            "endpoint_host": request.url.host,
            "endpoint_path": request.url.path,
            "workflow": os.environ.get("MACAE_WORKFLOW", "native-app"),
            "http_status": None,
            "input_tokens": None,
            "output_tokens": None,
            "cache_tokens": None,
            "latency_ms": None,
            "error_code": None,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.ident = reserve_record(self.record)

    def document(self, obj):
        if not isinstance(obj, dict):
            return
        data = obj.get("response", obj)
        if not isinstance(data, dict):
            return
        if data.get("id"):
            self.record["response_id"] = data["id"]
        usage = data.get("usage")
        if isinstance(usage, dict):
            self.record["input_tokens"] = usage.get("input_tokens", usage.get("prompt_tokens"))
            self.record["output_tokens"] = usage.get("output_tokens", usage.get("completion_tokens"))
            details = usage.get("input_tokens_details", usage.get("prompt_tokens_details", {})) or {}
            self.record["cache_tokens"] = details.get("cached_tokens")
        if data.get("model"):
            self.record["model_returned"] = data["model"]
        error = data.get("error")
        if isinstance(error, dict):
            self.record["error_code"] = error.get("code") or error.get("type")

    def feed(self, chunk):
        if self.capture_overflow:
            return
        self.buffer += chunk
        # A normal JSON response can contain formatting newlines. Keep the
        # complete JSON document; only split actual SSE into event/data lines.
        if not self.event_stream:
            if len(self.buffer) > 2_000_000:
                self.buffer = b""
                self.capture_overflow = True
                self.record["observer_error"] = "json_body_exceeds_2MB_capture_limit"
            return
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            if line.startswith(b"data:"):
                try:
                    self.document(json.loads(line[5:].lstrip()))
                except (ValueError, TypeError):
                    pass
        if len(self.buffer) > 2_000_000:
            self.buffer = self.buffer[-1_000_000:]

    def finish(self, exception=None):
        if self.finished:
            return
        self.finished = True
        try:
            self.document(json.loads(self.buffer))
        except (ValueError, TypeError):
            pass
        if exception:
            self.record["error_code"] = type(exception).__name__
        self.record["latency_ms"] = round((time.perf_counter() - self.start) * 1000, 2)
        persist_record(self.ident, self.record)
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        with EVIDENCE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(self.record) + "\n")
        print("MACAE_MODEL_METER " + json.dumps(self.record), flush=True)


class AsyncMeterStream(httpx.AsyncByteStream):
    def __init__(self, inner, meter):
        self.inner, self.meter = inner, meter

    async def __aiter__(self):
        try:
            async for chunk in self.inner:
                self.meter.feed(chunk)
                yield chunk
        except BaseException as exc:
            self.meter.finish(exc)
            raise
        finally:
            self.meter.finish()

    async def aclose(self):
        await self.inner.aclose()
        self.meter.finish()


class MeterStream(httpx.SyncByteStream):
    def __init__(self, inner, meter):
        self.inner, self.meter = inner, meter

    def __iter__(self):
        try:
            for chunk in self.inner:
                self.meter.feed(chunk)
                yield chunk
        except BaseException as exc:
            self.meter.finish(exc)
            raise
        finally:
            self.meter.finish()

    def close(self):
        self.inner.close()
        self.meter.finish()


def install():
    original_async = httpx.AsyncClient.send
    original_sync = httpx.Client.send

    async def async_send(client, request, **kwargs):
        reject_unmetered_search(request)
        if not is_inference(request):
            return await original_async(client, request, **kwargs)
        meter = Meter(request)
        try:
            response = await original_async(client, request, **kwargs)
            meter.record["http_status"] = response.status_code
            meter.event_stream = "text/event-stream" in response.headers.get("content-type", "").lower()
            if response.is_stream_consumed:
                meter.feed(response.content)
                meter.finish()
            else:
                response.stream = AsyncMeterStream(response.stream, meter)
            return response
        except BaseException as exc:
            meter.finish(exc)
            raise

    def sync_send(client, request, **kwargs):
        reject_unmetered_search(request)
        if not is_inference(request):
            return original_sync(client, request, **kwargs)
        meter = Meter(request)
        try:
            response = original_sync(client, request, **kwargs)
            meter.record["http_status"] = response.status_code
            meter.event_stream = "text/event-stream" in response.headers.get("content-type", "").lower()
            if response.is_stream_consumed:
                meter.feed(response.content)
                meter.finish()
            else:
                response.stream = MeterStream(response.stream, meter)
            return response
        except BaseException as exc:
            meter.finish(exc)
            raise

    httpx.AsyncClient.send = async_send
    httpx.Client.send = sync_send
