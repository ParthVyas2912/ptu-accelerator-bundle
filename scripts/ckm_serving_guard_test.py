"""Offline transport/policy checks: all underlying transports are replaced by stubs."""
import asyncio
import json
import os
from unittest.mock import patch

import aiohttp
import httpx
import requests
from ckm_serving_guard import InferenceDisarmed, ReadOnlyGate, check_outbound, install_transport_guard, route_allowed

forwarded = []


def sync_stub(*args, **kwargs):
    forwarded.append("sync")


async def async_stub(*args, **kwargs):
    forwarded.append("async")


def rejected(call):
    try:
        call()
    except InferenceDisarmed:
        return
    raise AssertionError("Expected inference disarm before underlying transport")


async def main():
    with patch.object(httpx.Client, "send", sync_stub), \
         patch.object(httpx.AsyncClient, "send", async_stub), \
         patch.object(requests.Session, "send", sync_stub), \
         patch.object(aiohttp.ClientSession, "_request", async_stub):
        install_transport_guard()
        request = httpx.Request("POST", "https://aif-ptu-conversation-7d804f70.openai.azure.com/openai/v1/responses")
        rejected(lambda: httpx.Client.send(None, request))
        rejected(lambda: requests.Session.send(None, request))
        for call in [
            lambda: httpx.AsyncClient.send(None, request),
            lambda: aiohttp.ClientSession._request(None, "POST", str(request.url)),
        ]:
            try:
                await call()
            except InferenceDisarmed:
                pass
            else:
                raise AssertionError("Async inference was not blocked")
        assert forwarded == []
        os.environ["IDENTITY_ENDPOINT"] = "http://localhost:42356/msi/token"
        httpx.Client.send(None, httpx.Request("GET", "https://srch-ptu-conversation-7d804f70.search.windows.net/indexes"))
        requests.Session.send(None, httpx.Request("GET", os.environ["IDENTITY_ENDPOINT"] + "?resource=offline"))
        assert forwarded == ["sync", "sync"]
        rejected(lambda: check_outbound("PUT", "https://stptuconv7d804f70.blob.core.windows.net/unsafe"))
        rejected(lambda: check_outbound("GET", "https://example.invalid"))

    assert route_allowed("POST", "/api/ingestion/refresh")
    assert route_allowed("GET", "/api/ingestion/documents/ptu-conversation-call-001")
    messages = []
    called = []

    async def native(scope, receive, send):
        called.append(scope["path"])
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"{}"})

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        messages.append(message)

    for method, path in [
        ("POST", "/api/processing/summarize"), ("GET", "/api/insights/dashboard"),
        ("POST", "/api/rag/ask"), ("POST", "/api/embeddings/index"),
        ("POST", "/api/documents/analyze"), ("POST", "/api/pipelines/run"),
        ("PUT", "/api/pipelines/automation/config"), ("POST", "/api/ingestion/upload/json"),
    ]:
        messages.clear()
        await ReadOnlyGate(native)({"type": "http", "method": method, "path": path}, receive, send)
        assert messages[0]["status"] == 503
        assert json.loads(messages[1]["body"])["inference_armed"] is False
    assert called == []
    messages.clear()
    await ReadOnlyGate(native)({"type": "http", "method": "GET", "path": "/api/health"}, receive, send)
    assert messages[0]["status"] == 200 and called == ["/api/health"]
    print(json.dumps({"status": "passed", "live_model_requests": 0, "real_network_requests": 0,
                      "sdk_transports_blocked": 4, "http_model_mutation_routes_blocked": 8,
                      "native_health_delegation": True, "data_and_identity_mock_forwarding": True}))


asyncio.run(main())
