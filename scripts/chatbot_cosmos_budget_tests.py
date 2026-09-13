"""Offline CAS tests; no Azure requests or credentials."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).parent / "chatbot_runtime"))
from azure.cosmos.exceptions import CosmosHttpResponseError
from cosmos_budget import CosmosBudget


class FakeContainer:
    def __init__(self):
        self.doc = None
        self.version = 0
        self.conflicts = 0

    def read_item(self, **kwargs):
        if self.doc is None:
            raise CosmosHttpResponseError(status_code=404, message="missing")
        return copy.deepcopy(self.doc)

    def create_item(self, body):
        self.version += 1
        self.doc = copy.deepcopy(body)
        self.doc["_etag"] = str(self.version)
        return copy.deepcopy(self.doc)

    def replace_item(self, *, item, body, etag, match_condition):
        if self.conflicts:
            self.conflicts -= 1
            self.version += 1
            self.doc["_etag"] = str(self.version)
            raise CosmosHttpResponseError(status_code=412, message="conflict")
        if etag != self.doc["_etag"]:
            raise CosmosHttpResponseError(status_code=412, message="stale")
        return self.create_item(body)


class BudgetTests(unittest.TestCase):
    def test_closed_document_cannot_reserve_or_reset(self):
        container = FakeContainer()
        budget = CosmosBudget(container)
        budget.snapshot()
        container.doc.update(limit=10, closed=True, requests=[{"units": 10}])
        before = copy.deepcopy(container.doc)
        with self.assertRaisesRegex(RuntimeError, "allowance is closed"):
            budget.reserve({"units": 1})
        self.assertEqual(container.doc, before)

    def test_limit_survives_new_store_and_finish(self):
        container = FakeContainer()
        first = CosmosBudget(container)
        request_id = first.reserve({"units": 3, "kind": "responses"})
        first.finish(request_id, {"input_tokens": 10, "status": 200})
        second = CosmosBudget(container)
        for _ in range(3):
            second.reserve({"units": 3})
        with self.assertRaisesRegex(RuntimeError, "exhausted"):
            second.reserve({"units": 1})
        self.assertEqual(len(second.snapshot()["requests"]), 4)
        self.assertEqual(second.snapshot()["requests"][0]["input_tokens"], 10)

    def test_etag_retry_does_not_duplicate_reservation(self):
        container = FakeContainer()
        container.conflicts = 2
        budget = CosmosBudget(container)
        budget.reserve({"units": 1})
        self.assertEqual(len(budget.snapshot()["requests"]), 1)

    def test_contention_fails_closed(self):
        container = FakeContainer()
        container.conflicts = 20
        with self.assertRaisesRegex(RuntimeError, "contention"):
            CosmosBudget(container).reserve({"units": 1})
        self.assertEqual(len(container.doc["requests"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
