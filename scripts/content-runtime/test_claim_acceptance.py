"""Offline regressions; these never import Azure clients or invoke models."""
import copy
import json
from pathlib import Path
import unittest

from claim_acceptance import assert_clean_claim


def details(statuses, names=None, claim_status="Completed"):
    names = names or [f"document-{index}.pdf" for index in range(len(statuses))]
    return {"status": "success", "data": {
        "status": claim_status,
        "processed_documents": [
            {"file_name": name, "status": status}
            for name, status in zip(names, statuses)]}}


class ClaimAcceptanceTests(unittest.TestCase):
    def test_all_submitted_documents_completed(self):
        value = details(["Completed", "Completed"])
        assert_clean_claim(value, ["document-0.pdf", "document-1.pdf"])

    def test_missing_business_document_is_not_a_processing_failure(self):
        # The missing-police case submits three files; gap-rule assertions are separate.
        names = ["claim-form.pdf", "repair-estimate.pdf", "damage-diagram.png"]
        assert_clean_claim(details(["Completed"] * 3, names), names)

    def test_all_failed_children_are_rejected(self):
        with self.assertRaisesRegex(AssertionError, "Completed is not clean"):
            assert_clean_claim(details(["Error"] * 4), [f"document-{i}.pdf" for i in range(4)])

    def test_partial_failure_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, r"document-1.pdf \(Error\)"):
            assert_clean_claim(details(["Completed", "Error"]), ["document-0.pdf", "document-1.pdf"])

    def test_nonterminal_or_missing_child_status_is_rejected(self):
        for status in ("Failed", "Processing", None):
            with self.subTest(status=status), self.assertRaises(AssertionError):
                assert_clean_claim(details([status]), ["document-0.pdf"])

    def test_missing_expected_file_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "every expected"):
            assert_clean_claim(details(["Completed"]), ["document-0.pdf", "document-1.pdf"])

    def test_duplicate_file_cannot_hide_missing_file(self):
        with self.assertRaisesRegex(AssertionError, "every expected"):
            assert_clean_claim(details(["Completed"] * 2, ["a.pdf", "a.pdf"]), ["a.pdf", "b.pdf"])

    def test_noncompleted_claim_is_rejected(self):
        for status in ("Failed", "Pending", "Processing"):
            with self.subTest(status=status), self.assertRaises(AssertionError):
                assert_clean_claim(details(["Completed"], claim_status=status), ["document-0.pdf"])

    def test_empty_document_result_is_not_clean_acceptance(self):
        with self.assertRaises(AssertionError):
            assert_clean_claim(details([]), [])

    def test_invalid_api_shapes_fail_explicitly(self):
        for value in (None, {}, {"status": "failed"}, {"status": "success", "data": None},
                      {"status": "success", "data": {"status": "Completed", "processed_documents": [None]}}):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                assert_clean_claim(value, ["a.pdf"])

    def test_recorded_native_completed_with_errors_is_rejected_without_rewrite(self):
        bundle = Path(__file__).resolve().parents[2]
        recording = json.loads((bundle / "evidence/content/batch-run-complete-recovery.json").read_text())
        value = recording["evidence"]["functional-results.json"]["cases"]["complete-recovery"]["lastDetail"]
        before = copy.deepcopy(value)
        self.assertEqual(value["data"]["status"], "Completed")
        with self.assertRaisesRegex(AssertionError, "Completed is not clean"):
            assert_clean_claim(value, ["claim-form.pdf", "police-report.pdf",
                                      "repair-estimate.pdf", "damage-diagram.png"])
        self.assertEqual(value, before)


if __name__ == "__main__":
    unittest.main()
