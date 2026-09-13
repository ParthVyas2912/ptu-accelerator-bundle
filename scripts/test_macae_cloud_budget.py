"""Offline only: no Azure or model requests; fake Cosmos and HTTPX transport."""
import asyncio
import copy
import json
import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from azure.cosmos.exceptions import CosmosHttpResponseError
from macae_cosmos_budget import CosmosBudget, LIMIT


class FakeContainer:
    def __init__(self):
        self.doc = None
        self.lock = threading.Lock()
        self.conflicts_remaining = 0

    def create_item(self, body):
        with self.lock:
            if self.doc is not None:
                raise CosmosHttpResponseError(status_code=409, message="exists")
            self.doc = copy.deepcopy(body) | {"_etag": "1"}
            return copy.deepcopy(self.doc)

    def read_item(self, item, partition_key):
        with self.lock:
            if self.doc is None:
                raise CosmosHttpResponseError(status_code=404, message="missing")
            return copy.deepcopy(self.doc)

    def replace_item(self, item, body, etag, match_condition):
        with self.lock:
            if self.conflicts_remaining:
                self.conflicts_remaining -= 1
                raise CosmosHttpResponseError(status_code=412, message="contended")
            if etag != self.doc["_etag"]:
                raise CosmosHttpResponseError(status_code=412, message="changed")
            self.doc = copy.deepcopy(body) | {"_etag": str(int(etag) + 1)}
            return copy.deepcopy(self.doc)


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.container = FakeContainer()
        self.budget = CosmosBudget(self.container)

    def test_missing_ledger_fails_closed(self):
        with self.assertRaises(CosmosHttpResponseError):
            self.budget.reserve({})

    def test_initialize_never_resets(self):
        self.budget.initialize_once(3)
        with self.assertRaises(CosmosHttpResponseError):
            self.budget.initialize_once(0)
        self.assertEqual(self.container.doc["used"], 3)

    def test_migration_preserves_previous_total_and_usage(self):
        self.budget.initialize_once(LIMIT - 1)
        record = {"input_tokens": None}
        ident = self.budget.reserve(record)
        self.assertEqual(ident, LIMIT)
        self.budget.persist(ident, record | {"input_tokens": 10, "http_status": 200})
        self.assertEqual(self.container.doc["records"][str(LIMIT)]["input_tokens"], 10)
        with self.assertRaises(RuntimeError):
            CosmosBudget(self.container).reserve({})

    def test_concurrent_limit(self):
        self.budget.initialize_once(0)
        def attempt(_):
            try:
                return self.budget.reserve({})
            except RuntimeError:
                return None
        with ThreadPoolExecutor(max_workers=8) as pool:
            ids = list(pool.map(attempt, range(30)))
        self.assertEqual(sorted(i for i in ids if i), list(range(1, LIMIT + 1)))
        self.assertEqual(self.container.doc["used"], LIMIT)

    def test_exact_second_pass_migration_preserves_records_and_is_idempotent(self):
        prior = {str(i): {"call_number": i, "input_tokens": i * 10} for i in range(1, 13)}
        self.container.create_item({
            "id": "test", "session_id": "test", "used": 12, "limit": 12,
            "previous_live_calls": 0, "records": prior,
        })
        evidence = self.budget.authorize_second_pass()
        self.assertEqual(self.container.doc["used"], 12)
        self.assertEqual(self.container.doc["limit"], 22)
        self.assertEqual(self.container.doc["records"], prior)
        self.assertEqual(evidence["beforeRecordsSha256"], evidence["afterRecordsSha256"])
        self.assertFalse(self.budget.authorize_second_pass()["changed"])
        with self.assertRaises(RuntimeError):
            self.budget.reserve({})
        final = self.budget.authorize_final_pass()
        self.assertEqual(self.container.doc["limit"], 24)
        self.assertEqual(self.container.doc["used"], 12)
        self.assertEqual(self.container.doc["records"], prior)
        self.assertEqual(final["beforeRecordsSha256"], final["afterRecordsSha256"])
        self.assertFalse(self.budget.authorize_final_pass()["changed"])
        self.assertEqual(self.budget.reserve({}), 13)
        self.assertFalse(self.budget.authorize_final_pass()["changed"])
        with self.assertRaises(RuntimeError):
            self.budget.authorize_second_pass()
        self.assertEqual(self.container.doc["used"], 13)

    def test_final_pass_refuses_spent_or_unapproved_source(self):
        self.budget.initialize_once(12)
        with self.assertRaises(RuntimeError):
            self.budget.authorize_final_pass()
        self.container.doc["limit"] = 22
        self.container.doc["used"] = 13
        with self.assertRaises(RuntimeError):
            self.budget.authorize_final_pass()

    def test_second_pass_migration_refuses_unexpected_first_pass(self):
        self.budget.initialize_once(0)
        self.container.doc["limit"] = 12
        with self.assertRaises(RuntimeError):
            self.budget.authorize_second_pass()
        self.assertEqual(self.container.doc["limit"], 12)
        self.assertEqual(self.container.doc["used"], 0)

    def test_conflicts_bounded_and_fail_closed(self):
        self.budget.initialize_once(0)
        self.container.conflicts_remaining = 15
        with self.assertRaises(RuntimeError):
            self.budget.reserve({})
        self.assertEqual(self.container.doc["used"], 0)

    def test_corrupt_limit_fails_closed(self):
        self.budget.initialize_once(0)
        self.container.doc["limit"] = 100
        with self.assertRaises(RuntimeError):
            self.budget.reserve({})

    def test_httpx_sync_async_usage_limit_and_remote_kb_gate(self):
        import httpx
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["MACAE_STATE_DIR"] = tmp
            os.environ["MACAE_EVIDENCE_DIR"] = tmp
            import macae_model_guard as guard
            old_sync, old_async = httpx.Client.send, httpx.AsyncClient.send
            try:
                guard.install()
                sent = []
                def respond(request):
                    sent.append(request)
                    payload = {
                        "model": "gpt-5.4-mini",
                        "usage": {"input_tokens": 10, "output_tokens": 2,
                                  "input_tokens_details": {"cached_tokens": 4}},
                    }
                    if len(sent) <= 8:
                        return httpx.Response(200, content=json.dumps(payload, indent=2),
                                              headers={"content-type": "application/json"})
                    return httpx.Response(200, content="event: response.completed\ndata:" + json.dumps({"response": payload}) + "\n\n",
                                          headers={"content-type": "text/event-stream"})
                url = "https://ptumacae7d804f70.openai.azure.com/openai/v1/responses"
                body = {"model": "gpt-5.4-mini", "input": "MOCK_ONLY", "tools": None}
                transport = httpx.MockTransport(respond)
                with httpx.Client(transport=transport) as client:
                    for _ in range(8):
                        self.assertEqual(client.post(url, json=body).status_code, 200)
                    with self.assertRaises(RuntimeError):
                        client.post("https://ptu-macae-7d804f70-srch.search.windows.net/knowledgebases/eval/retrieve")
                async def remaining():
                    async with httpx.AsyncClient(transport=transport) as client:
                        for _ in range(LIMIT - 8):
                            self.assertEqual((await client.post(url, json=body)).status_code, 200)
                        with self.assertRaises(RuntimeError):
                            await client.post(url, json=body)
                asyncio.run(remaining())
                self.assertEqual(len(sent), LIMIT)
                rows = [json.loads(line) for line in (Path(tmp) / "model-calls.jsonl").read_text().splitlines()]
                self.assertEqual(len(rows), LIMIT)
                self.assertTrue(all(
                    r["model_returned"] == "gpt-5.4-mini" and r["input_tokens"] == 10
                    and r["output_tokens"] == 2 and r["cache_tokens"] == 4 for r in rows
                ))
                # Parser-only checks reserve no request slots and make no I/O.
                meter = guard.Meter.__new__(guard.Meter)
                meter.buffer, meter.record = b"", {}
                meter.event_stream, meter.capture_overflow = True, False
                event = b'event: response.completed\ndata:{"response":{"id":"MOCK","usage":{"input_tokens":123,"output_tokens":7}}}\n\n'
                for offset in range(0, len(event), 3):
                    meter.feed(event[offset:offset + 3])
                self.assertEqual(meter.record["input_tokens"], 123)
                self.assertEqual(meter.record["output_tokens"], 7)
                self.assertEqual(meter.record["response_id"], "MOCK")
                meter.event_stream = False
                meter.feed(b" " * 2_000_001)
                self.assertTrue(meter.capture_overflow)
                self.assertEqual(meter.buffer, b"")
                self.assertIn("observer_error", meter.record)
            finally:
                httpx.Client.send, httpx.AsyncClient.send = old_sync, old_async


if __name__ == "__main__":
    unittest.main()
