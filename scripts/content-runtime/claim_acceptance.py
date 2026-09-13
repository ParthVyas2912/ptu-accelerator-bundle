"""Evaluation acceptance, separate from the application's native status semantics."""
from collections import Counter
from collections.abc import Sequence
import json


def assert_clean_claim(detail: object, expected_filenames: Sequence[str]) -> None:
    """Require successful processing of every submitted fixture, without modifying results."""
    if not isinstance(detail, dict) or detail.get("status") != "success":
        raise AssertionError("Claim details were not returned successfully")
    data = detail.get("data")
    if not isinstance(data, dict) or data.get("status") != "Completed":
        raise AssertionError("Claim workflow has not completed")
    documents = data.get("processed_documents")
    if not expected_filenames or not isinstance(documents, list) or not documents:
        raise AssertionError("Clean processing requires expected and returned documents")
    if not all(isinstance(document, dict) for document in documents):
        raise AssertionError("Malformed per-document outcomes")
    actual_names = [document.get("file_name") for document in documents]
    if not all(isinstance(name, str) for name in actual_names):
        raise AssertionError("Per-document filenames are missing")
    if Counter(actual_names) != Counter(expected_filenames):
        raise AssertionError("Returned documents do not match every expected submitted file")
    failures = [
        f"{document['file_name']} ({document.get('status', 'missing status')})"
        for document in documents if document.get("status") != "Completed"
    ]
    if failures:
        raise AssertionError("Completed is not clean processing: " + ", ".join(failures))


def assert_missing_police_result(result: dict) -> None:
    expected = ("claim-form.pdf", "repair-estimate.pdf", "damage-diagram.png")
    assert_clean_claim(result["claimDetail"], expected)
    claim = result["claimDetail"]["data"]
    control = result["control"]
    assert control["mode"] == "disarmed"
    assert set(control["documents"]) == set(expected)
    values = {}
    for name in expected:
        document = result["documents"][name]
        assert document["processId"] == control["documents"][name]["processId"]
        artifacts = document["artifacts"]
        assert all(not item.get("missing") for item in artifacts.values())
        mapped = artifacts["gpt_output.json"]["value"]["choices"][0]["message"]["parsed"]
        saved = artifacts["save_output.json"]["value"]
        assert mapped == artifacts["evaluate_output.json"]["value"]["extracted_result"] == saved["result"]
        assert saved["process_id"] == document["processId"]
        status = artifacts["process-status.json"]["value"]["pipeline_status"]
        assert status["completed"] is True
        assert status["completed_steps"] == ["extract", "map", "evaluate", "save"]
        values[name] = saved["result"]
    form = values["claim-form.pdf"]
    assert form["claim_number"] == "PTU-CONTENT-001"
    assert form["policy_number"] == "TEST-POLICY-001"
    assert form["vehicle_information"]["vin"] == "1TST23456DEMO0001"
    assert form["incident_details"]["date_of_loss"] == "2026-09-01"
    assert "Third party involved: Yes" in form["incident_details"]["description"]
    assert form["damage_assessment"]["total_estimated_repair"] == 2500
    estimate = values["repair-estimate.pdf"]
    assert estimate["vehicle"]["vin"] == "1TST23456DEMO0001"
    assert estimate["date"] == "2026-09-01"
    assert estimate["total_estimate"] == 2500 and estimate["total_estimate_currency"] == "USD"
    items = {item["service_description"]: item for item in estimate["repair_details"]}
    assert {name: item["total"] for name, item in items.items()} == {
        "Front bumper": 1000, "Labor": 1000, "Paint": 500}
    assert items["Labor"]["labor_hours"] == 5 and items["Labor"]["rate_per_hour"] == 200
    image = values["damage-diagram.png"]
    assert image["image_info"]["width"] == 640 and image["image_info"]["height"] == 360
    assert image["vehicle_count"] == 1
    assert image["vehicles"][0]["damage_regions"][0]["location_on_vehicle"] == "front-left bumper"
    assert "fictional" in image["vehicles"][0]["overall_assessment"]["notes"].lower()
    agents = result["nativeAgents"]
    assert json.loads(agents["rai"]["text"])["IsNotSafe"] is False
    assert agents["summary"]["text"] == claim["process_summary"]
    assert agents["gaps"]["text"] == claim["process_gaps"]
    summary = claim["process_summary"]
    assert all(value in summary for value in ("TEST-POLICY-001", "1TST23456DEMO0001", "2026-09-01", "2,500"))
    assert "contents are not provided" in summary
    gap = json.loads(claim["process_gaps"])
    assert gap["inputs"]["involves_third_party"]["value"] is True
    assert gap["inputs"]["loss_amount"]["value"] == 2500
    assert len(gap["gaps"]) == 1
    assert gap["gaps"][0]["rule_id"] == "REQ-PR-THIRD-PARTY-006"
    assert gap["gaps"][0]["missing_types"] == ["police_report"]
    assert gap["gaps"][0]["severity"] == "high"
    assert gap["discrepancies"] == []
    assert {item["filename"] for item in gap["documents"]} == set(expected)
    rows = [row for row in result["ledger"]["requests"] if row["kind"] == "model" and row["id"] > 33]
    assert len(rows) == 6 and Counter(row["stage"] for row in rows) == {
        "map": 3, "rai": 1, "summary": 1, "gaps": 1}
    assert all(row["claimId"] == control["claimId"] and row["status"] == 200 and row["usage"] for row in rows)
