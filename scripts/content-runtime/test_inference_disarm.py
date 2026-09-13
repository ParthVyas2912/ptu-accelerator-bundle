"""Offline proof that disarm rejects inference before transport or budget reservation."""
import asyncio
import os
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import httpx
import requests
import content_guard


class InferenceDisarmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment = patch.dict(os.environ, {
            "CONTENT_INFERENCE_DISARMED": "1", "CONTENT_BUDGET_BACKEND": "blob"})
        cls.environment.start()
        cls.reserve = Mock(side_effect=AssertionError("Budget reservation must not occur"))
        cls.modules = patch.dict(sys.modules, {"cloud_budget": SimpleNamespace(reserve=cls.reserve)})
        cls.modules.start()
        content_guard.install()

    @classmethod
    def tearDownClass(cls):
        cls.modules.stop()
        cls.environment.stop()

    def test_sync_httpx_never_reaches_transport(self):
        transport = Mock(side_effect=AssertionError("Transport must not occur"))
        with httpx.Client(transport=httpx.MockTransport(transport)) as client:
            with self.assertRaisesRegex(RuntimeError, "hard-disarmed"):
                client.post("https://aif-ptuv-content-260911.openai.azure.com/openai/deployments/gpt-5.1/chat/completions",
                            json={"model": "gpt-5.1"})
        transport.assert_not_called()
        self.reserve.assert_not_called()

    def test_async_httpx_never_reaches_transport(self):
        transport = Mock(side_effect=AssertionError("Transport must not occur"))
        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as client:
                with self.assertRaisesRegex(RuntimeError, "hard-disarmed"):
                    await client.post("https://aif-ptuv-content-260911.openai.azure.com/openai/responses",
                                      json={"model": "gpt-5.1"})
        asyncio.run(run())
        transport.assert_not_called()
        self.reserve.assert_not_called()

    def test_requests_cu_never_reaches_adapter(self):
        with patch("requests.adapters.HTTPAdapter.send") as send:
            with self.assertRaisesRegex(RuntimeError, "hard-disarmed"):
                requests.post("https://aif-ptuv-content-260911.cognitiveservices.azure.com/contentunderstanding/analyzers/prebuilt-layout:analyzeBinary",
                              data=b"not sent")
            send.assert_not_called()
        self.reserve.assert_not_called()

    def test_all_ai_paths_blocked_including_metadata(self):
        for host, path in (
            ("openai", "/anything"), ("cognitiveservices", "/metadata"),
            ("services.ai", "/api/projects/ptu-content-project/agents")):
            with self.subTest(host=host), self.assertRaisesRegex(RuntimeError, "hard-disarmed"):
                content_guard.reserve("GET", f"https://aif-ptuv-content-260911.{host}.azure.com{path}")
        self.reserve.assert_not_called()

    def test_owned_storage_is_still_available(self):
        self.assertIsNone(content_guard.reserve("GET", "https://stptuvcontent260911.blob.core.windows.net/container/blob"))
        self.reserve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
