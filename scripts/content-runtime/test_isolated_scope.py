import base64
import contextlib
import copy
import json
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import isolated_scope as scope
import cloud_budget
import content_guard


def state():
    return {"run": scope.RUN, "approvedTotal": 17, "mode": "armed", "claimId": "new-claim",
            "expected": {"form": {"schemaId": "schema"}, "estimate": {}, "image": {}},
            "documents": {"form": {"processId": "new-process", "schemaId": "schema"}}}


def payload(claim="new-claim", pid="new-process"):
    return {"process_id": pid, "pipeline_status": {"process_id": pid, "metadata_id": claim, "schema_id": "schema"},
            "files": [{"name": "form", "process_id": pid, "artifact_type": "source_content"}]}


class IsolationTests(unittest.TestCase):
    def test_native_derived_artifacts_preserve_single_source_scope(self):
        data = payload()
        data["files"].append({"name": "extract_output.json", "process_id": "new-process",
                              "artifact_type": "extracted_content"})
        self.assertEqual(scope.classify("content-pipeline-map-queue", data, state())["fileName"], "form")
        data["files"][-1]["process_id"] = "other-process"
        with self.assertRaises(RuntimeError):
            scope.classify("content-pipeline-map-queue", data, state())

    def test_old_claim_and_document_rejected(self):
        self.assertIsNone(scope.classify("claim-process-queue", {"claim_process_id": "old-claim"}, state()))
        self.assertIsNone(scope.classify("content-pipeline-map-queue", payload("old-claim"), state()))
        with self.assertRaises(RuntimeError):
            scope.classify("content-pipeline-map-queue", payload(pid="old-process"), state())

    def test_plain_and_base64_preserve_payload(self):
        data = payload()
        encoded = json.dumps(data)
        self.assertEqual(scope.decode(encoded), data)
        self.assertEqual(scope.decode(base64.b64encode(encoded.encode())), data)

    def test_unrelated_messages_deferred_not_deleted_or_dispatched(self):
        items = [SimpleNamespace(id="old", content=json.dumps(payload("old-claim"))),
                 SimpleNamespace(id="new", content=json.dumps(payload()))]
        updates, events = [], []
        client = SimpleNamespace(queue_name="content-pipeline-map-queue",
                                 update_message=lambda message, **kw: updates.append((message.id, kw)))
        with patch.object(scope, "read_control", side_effect=lambda: state()), \
             patch.object(scope, "event", side_effect=lambda kind, **kw: events.append(kind)):
            dispatched = []
            for message in scope.receive_scoped(lambda *_a, **_k: iter(items), client):
                dispatched.append(message.id)
                self.assertEqual(scope.CURRENT.get()["processId"], "new-process")
        self.assertEqual(dispatched, ["new"])
        self.assertEqual(updates, [("old", {"visibility_timeout": 3600})])
        self.assertEqual(events, ["deferred-unrelated", "admitted-native-message"])
        self.assertIsNone(scope.CURRENT.get())

    def test_disarm_prevents_dequeue(self):
        value = state()
        value["mode"] = "disarmed"
        with patch.object(scope, "read_control", return_value=value):
            with self.assertRaises(RuntimeError):
                next(scope.receive_scoped(lambda *_: self.fail("dequeue called"), None))

    def test_inference_requires_exact_context(self):
        with patch.object(scope, "read_control", side_effect=lambda: state()):
            with self.assertRaises(RuntimeError):
                scope.inference_scope("model")
            for context in ({"claimId": "old-claim", "stage": "map"},
                            {"claimId": "new-claim", "stage": "claim"}):
                token = scope.CURRENT.set(context)
                try:
                    with self.assertRaises(RuntimeError):
                        scope.inference_scope("model")
                finally:
                    scope.CURRENT.reset(token)
            token = scope.CURRENT.set({"claimId": "new-claim", "stage": "map",
                                       "processId": "new-process", "fileName": "form"})
            try:
                self.assertIn("/map/new-process", scope.inference_scope("model")["scopeKey"])
                with self.assertRaises(RuntimeError):
                    scope.inference_scope("cu-analyze")
            finally:
                scope.CURRENT.reset(token)

    def test_global_cap17_and_one_attempt_per_scoped_stage(self):
        ledger = {"requests": [{"id": i + 1, "kind": "model"} for i in range(11)]}
        before = copy.deepcopy(ledger["requests"])
        with patch.object(cloud_budget, "transaction", side_effect=lambda change: change(ledger)):
            for i in range(6):
                record = {"kind": "model", "scopeKey": f"stage-{i}"}
                cloud_budget.reserve(record, 17)
                with self.assertRaises(RuntimeError):
                    cloud_budget.reserve(record, 17)
            with self.assertRaises(RuntimeError):
                cloud_budget.reserve({"kind": "model", "scopeKey": "seventh"}, 17)
        self.assertEqual(len(ledger["requests"]), 17)
        self.assertEqual(ledger["requests"][:11], before)

    def test_guard_checks_scope_before_budget_or_transport(self):
        with patch.dict(os.environ, {"CONTENT_SCOPE_WORKER": "1", "CONTENT_INFERENCE_DISARMED": "0",
                                     "CONTENT_BUDGET_BACKEND": "blob"}), \
             patch.object(scope, "read_control", side_effect=lambda: state()), \
             patch.object(cloud_budget, "reserve", side_effect=AssertionError("budget reached")):
            with self.assertRaisesRegex(RuntimeError, "armed allowed claim"):
                content_guard.reserve("POST", "https://aif-ptuv-content-260911.openai.azure.com/openai/deployments/gpt-5.1/chat/completions")


if __name__ == "__main__":
    unittest.main()
