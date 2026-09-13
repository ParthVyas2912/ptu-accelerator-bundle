"""Pure unit tests: no Azure connection, credential, resource or model request."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, ResourceNotFoundError
from budget import DurableBudget


class FakeBlob:
    def __init__(self):
        self.data = None
        self.version = 0
        self.lock = threading.Lock()

    def download_blob(self):
        with self.lock:
            if self.data is None:
                raise ResourceNotFoundError("missing")
            body, version = self.data, str(self.version)
        return SimpleNamespace(readall=lambda: body, properties=SimpleNamespace(etag=version))

    def upload_blob(self, body, overwrite, etag=None, match_condition=None):
        with self.lock:
            if not overwrite and self.data is not None:
                raise ResourceExistsError("exists")
            if overwrite and str(self.version) != etag:
                raise ResourceModifiedError("etag conflict")
            self.data = body.encode()
            self.version += 1


class BudgetTests(unittest.TestCase):
    def setUp(self):
        # Exercise the original accounting rules only inside these historical-policy unit fixtures.
        opened = patch("budget.EVALUATION_CLOSED", False)
        opened.start()
        self.addCleanup(opened.stop)
        self.blob = FakeBlob()
        self.budget = DurableBudget(self.blob)

    def test_default_disabled_fail_closed(self):
        with self.assertRaises(RuntimeError):
            self.budget.reserve("/threads/test/runs")
        self.assertEqual(len(self.budget.read()[0]["events"]), 0)

    def test_exact_remaining_eight_including_failed_attempt(self):
        self.budget.set_enabled(True, 4)
        for _ in range(8):
            event = self.budget.reserve("/threads/test/runs")
            self.budget.finish(event, {"http_status": 401})
        with self.assertRaises(RuntimeError):
            self.budget.reserve("/threads/test/runs")
        self.assertEqual(len(self.budget.read()[0]["events"]), 8)

    def test_restart_does_not_reset(self):
        self.budget.set_enabled(True, 4)
        self.budget.reserve("/threads/test/runs")
        restarted = DurableBudget(self.blob)
        self.assertEqual(len(restarted.read()[0]["events"]), 1)
        with self.assertRaises(RuntimeError):
            restarted.set_enabled(True, 4)

    def test_disarm_blocks_without_spending(self):
        self.budget.set_enabled(True, 4)
        self.budget.set_enabled(False)
        with self.assertRaises(RuntimeError):
            self.budget.reserve("/threads/test/runs")
        self.assertEqual(len(self.budget.read()[0]["events"]), 0)

    def test_single_batch_claim(self):
        self.budget.set_enabled(True, 4)
        self.budget.claim_batch("synthetic-one")
        with self.assertRaises(RuntimeError):
            self.budget.claim_batch("synthetic-one")

    def test_concurrent_instances_cannot_overspend(self):
        self.budget.set_enabled(True, 4)
        def attempt(_):
            try:
                DurableBudget(self.blob).reserve("/threads/test/runs")
                return 1
            except RuntimeError:
                return 0
        with ThreadPoolExecutor(max_workers=16) as pool:
            successes = sum(pool.map(attempt, range(32)))
        self.assertEqual(successes, 8)
        self.assertEqual(len(self.budget.read()[0]["events"]), 8)

    def test_baseline_tampering_fails_closed(self):
        self.budget.read()
        bad = json.loads(self.blob.data)
        bad["prior_calls"] = 0
        self.blob.data = json.dumps(bad).encode()
        with self.assertRaises(RuntimeError):
            self.budget.read()

    def test_old_agent_ids_preserved(self):
        self.budget.record("current_agents", [{"id": "a"}])
        self.budget.record("current_agents", [{"id": "b"}])
        self.assertEqual(self.budget.read()[0]["previous_agent_sets"], [[{"id": "a"}]])

    def test_service_datetimes_are_persistable(self):
        self.budget.record("run_usage", [{"created_at": datetime(2026, 9, 12, tzinfo=timezone.utc)}])
        self.assertIn("2026-09-12", self.budget.read()[0]["run_usage"][0]["created_at"])


class BudgetClosureTests(unittest.TestCase):
    def test_closed_arm_fails_before_blob_access(self):
        blob = FakeBlob()
        with self.assertRaisesRegex(RuntimeError, "closed at 10/10"):
            DurableBudget(blob).set_enabled(True, 10)
        self.assertIsNone(blob.data)

    def test_old_headroom_cannot_reserve_or_claim(self):
        blob = FakeBlob()
        blob.data = json.dumps({"prior_calls": 4, "total_cap": 12,
                                "events": [{"number": i} for i in range(5, 11)],
                                "processing_enabled": True, "claimed_batch": None}).encode()
        original = blob.data
        budget = DurableBudget(blob)
        with self.assertRaisesRegex(RuntimeError, "closed at 10/10"):
            budget.reserve("/threads/test/runs")
        with self.assertRaisesRegex(RuntimeError, "closed at 10/10"):
            budget.claim_batch("new-batch")
        self.assertEqual(blob.data, original)

    def test_closed_ledger_can_still_be_disarmed_and_read(self):
        blob = FakeBlob()
        blob.data = json.dumps({"prior_calls": 4, "total_cap": 12,
                                "events": [{} for _ in range(6)],
                                "processing_enabled": True, "claimed_batch": "completed"}).encode()
        budget = DurableBudget(blob)
        self.assertEqual(budget.set_enabled(False), 10)
        self.assertFalse(budget.read()[0]["processing_enabled"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
