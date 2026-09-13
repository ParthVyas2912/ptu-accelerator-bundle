"""Offline transport tests: no Azure connections or model calls."""
import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "chatbot_runtime"))
import httpx
import chatbot_metering as meter


class MeteringTests(unittest.TestCase):
    def setUp(self):
        self.allowance = patch.object(meter, "ALLOWANCE_CLOSED", False)
        self.allowance.start()
        self.temp = tempfile.TemporaryDirectory()
        os.environ["CHATBOT_USAGE_DB"] = str(Path(self.temp.name) / "usage.sqlite")
        meter.install()
        self.host = "https://aif-ccptu1feb0911.openai.azure.com"

    def tearDown(self):
        self.temp.cleanup()
        self.allowance.stop()

    def test_closed_allowance_blocks_before_transport(self):
        def forbidden_transport(request):
            raise AssertionError("Closed allowance reached HTTP transport")
        with patch.object(meter, "ALLOWANCE_CLOSED", True):
            with httpx.Client(transport=httpx.MockTransport(forbidden_transport)) as client:
                with self.assertRaisesRegex(RuntimeError, "allowance is closed"):
                    client.post(self.host + "/responses", json={"model": "gpt-5.4-mini"})
        with meter.database() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM requests").fetchone()[0], 0)

    def test_denies_unapproved_endpoint(self):
        with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={}))) as client:
            with self.assertRaisesRegex(RuntimeError, "not the approved"):
                client.post("https://unapproved.invalid/embeddings", json={"model": "x"})

    def test_limit_counts_every_http_attempt(self):
        with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(429, json={}))) as client:
            for _ in range(12):
                self.assertEqual(client.post(self.host + "/embeddings", json={"model": "x"}).status_code, 429)
            with self.assertRaisesRegex(RuntimeError, "budget exhausted"):
                client.post(self.host + "/embeddings", json={"model": "x"})
        with meter.database() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM requests").fetchone()[0], 12)

    def test_captures_usage_without_prompt_or_secret(self):
        def transport(request):
            return httpx.Response(200, json={
                "usage": {"input_tokens": 11, "output_tokens": 7,
                          "input_tokens_details": {"cached_tokens": 3}},
                "output": [{"type": "function_call", "name": "policy_agent"}],
            })
        with httpx.Client(transport=httpx.MockTransport(transport)) as client:
            client.post(self.host + "/responses", json={
                "model": "gpt-5.4-mini", "input": "synthetic-private-marker",
                "agent_reference": {"name": "ptu-chatbot-product-eval"},
            }, headers={"Authorization": "Bearer synthetic-secret-marker"})
        with meter.database() as db:
            row = db.execute("SELECT units,input_tokens,output_tokens,cached_tokens,tool_names FROM requests").fetchone()
            self.assertEqual(row[:4], (3, 11, 7, 3))
            self.assertIn("policy_agent", row[4])
        raw = Path(os.environ["CHATBOT_USAGE_DB"]).read_bytes()
        self.assertNotIn(b"synthetic-private-marker", raw)
        self.assertNotIn(b"synthetic-secret-marker", raw)

    def test_async_transport_instrumented(self):
        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(
                200, json={"usage": {"input_tokens": 4, "output_tokens": 2}}))) as client:
                await client.post(self.host + "/responses", json={"model": "gpt-5.4-mini"})
        asyncio.run(run())
        with meter.database() as db:
            self.assertEqual(db.execute("SELECT input_tokens,output_tokens FROM requests").fetchone(), (4, 2))

    def test_agent_reference_does_not_override_reasoning(self):
        def transport(request):
            body = json.loads(request.content)
            self.assertNotIn("reasoning", body)
            self.assertEqual(body["max_tool_calls"], 1)
            self.assertEqual(body["max_output_tokens"], 2048)
            return httpx.Response(200, json={})
        with httpx.Client(transport=httpx.MockTransport(transport)) as client:
            client.post(self.host + "/responses", json={
                "agent_reference": {"name": "ptu-chatbot-chat-eval"},
            })

    def test_failed_sse_preserves_error_despite_http_200(self):
        event = {"type": "response.failed", "response": {
            "error": {"code": "azure_search_error", "message": "synthetic-secret-marker"},
        }}
        with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
            200, text="data: " + json.dumps(event) + "\n\n",
            headers={"Content-Type": "text/event-stream"},
        ))) as client:
            client.post(self.host + "/responses", json={"agent_reference": {"name": "ptu-chatbot-product-eval"}})
        with meter.database() as db:
            self.assertEqual(db.execute("SELECT status,error,input_tokens FROM requests").fetchone(),
                             (200, "azure_search_error", None))
        self.assertNotIn(b"synthetic-secret-marker", Path(os.environ["CHATBOT_USAGE_DB"]).read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
