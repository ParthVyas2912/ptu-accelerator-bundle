import copy
import json
from pathlib import Path
import unittest
from claim_acceptance import assert_missing_police_result


class MissingPoliceCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (Path(__file__).resolve().parents[2] / "evidence" / "content" /
                   "isolated-run-result.json").read_text(encoding="utf-8")
        cls.result = json.loads(cls.raw)

    def test_real_native_capture_passes_without_rewriting_warning_or_fields(self):
        before = copy.deepcopy(self.result)
        assert_missing_police_result(self.result)
        self.assertEqual(before, self.result)
        self.assertEqual(self.result["ledger"]["requests"][-1]["error"],
                         "content_filter_error: The contents are not filtered")

    def test_completed_with_failed_child_is_not_accepted(self):
        changed = copy.deepcopy(self.result)
        changed["claimDetail"]["data"]["processed_documents"][0]["status"] = "Error"
        with self.assertRaises(AssertionError):
            assert_missing_police_result(changed)

    def test_wrong_saved_source_value_is_rejected(self):
        changed = copy.deepcopy(self.result)
        changed["documents"]["claim-form.pdf"]["artifacts"]["save_output.json"]["value"]["result"]["policy_number"] = "WRONG"
        with self.assertRaises(AssertionError):
            assert_missing_police_result(changed)

    def test_rewritten_or_missing_native_gap_is_rejected(self):
        changed = copy.deepcopy(self.result)
        gap = json.loads(changed["claimDetail"]["data"]["process_gaps"])
        gap["gaps"] = []
        changed["claimDetail"]["data"]["process_gaps"] = json.dumps(gap)
        changed["nativeAgents"]["gaps"]["text"] = json.dumps(gap)
        with self.assertRaises(AssertionError):
            assert_missing_police_result(changed)


if __name__ == "__main__":
    unittest.main()
