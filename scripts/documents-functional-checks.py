"""Offline checks over real DKM responses. Does not invoke models or rewrite outputs."""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
e = root / "evidence/documents"
checks = []
def check(name, expected, actual, passed, evidence):
    checks.append(dict(name=name, expected=expected, actual=actual,
                       status="PASS" if passed else "FAIL", evidence=evidence))
def load(name):
    return json.loads((e / name).read_text(encoding="utf-8-sig"))

first_id = "3951c54f0a974f79b9d8fc3d7e4591ad202609120125365840455"
second = json.loads(load("retry-phase-ingest-second.json")["result"]["body"])
second_id = second["documentId"]
check("Second policy PDF ingestion", "HTTP200 and real document ID",
      second_id, bool(second_id) and load("retry-phase-ingest-second.json")["result"]["status"] == 200,
      "retry-phase-ingest-second.json")
for field, expected in {"person": "Omar Patel", "place": "Cedar Bay", "document_type": "Policy"}.items():
    value = second["keywords"].get(field)
    check("Second metadata: " + field, expected, value, value == expected, "retry-phase-ingest-second.json")
table_metadata = {k: second["keywords"].get(k, "") for k in ["allowances", "structure"]}
check("PDF table value/column extraction", "Annual training15 days/year; Allowance and Days/year columns",
      table_metadata, "15" in table_metadata["allowances"] and
      "Allowance" in table_metadata["structure"] and "Days/year" in table_metadata["structure"],
      "retry-phase-ingest-second.json;document-intelligence-metrics.json")
filters = load("retry-phase-metadata.json")["result"]
for result, expected in zip(filters, [2, 2, 0, 1]):
    total = json.loads(result["body"])["totalRecords"]
    check("Metadata filter " + json.dumps(result["tags"]), expected, total,
          total == expected and result["status"] == 200, "retry-phase-metadata.json")
for source in load("retry-phase-sources.json")["result"]:
    expected_hash = hashlib.sha256((root / "test-data/documents" / source["name"]).read_bytes()).hexdigest()
    check("Persisted source hash: " + source["name"], expected_hash, source["sha256"],
          source["status"] == 200 and source["sha256"] == expected_hash, "retry-phase-sources.json")
for document in json.loads(filters[0]["body"])["documents"]:
    summary = document["summary"]
    # Report the raw quality failure; never strip greetings or modify the stored response.
    unsupported_greeting = bool(re.search(r"\bhello\b", summary, re.I))
    check("Summary groundedness: " + document["fileName"], "No unrelated greeting",
          {"unsupported_greeting": unsupported_greeting, "summary": summary}, not unsupported_greeting,
          "retry-phase-metadata.json")
for case, expected_ids, expected_numbers in [
    ("qa-document", {first_id}, ["10", "2025"]),
    ("qa-corpus", {first_id, second_id}, ["10", "15", "5", "50"]),
]:
    filename = f"retry-phase-{case}.json"
    approved_repeat = case == "qa-corpus" and (e / "comparison14-read-result.json").exists()
    if approved_repeat:
        filename = "comparison14-read-result.json"
    if not (e / filename).exists():
        attempted = (e / f"retry-phase-{case}-uncaptured.json").exists()
        checks.append(dict(name=case, status="BLOCKED" if attempted else "NOT_RUN",
                           expected="Actual scoped QA/comparison and verified citations",
                           actual="Request attempted; CLI Unicode output capture failed; not repeated" if attempted else "No response evidence"))
        continue
    response = load(filename)["value"] if approved_repeat else load(filename)["result"]
    answer = json.loads(response["body"])
    ids = {x["documentId"] for x in answer.get("relevantSources", [])}
    text = answer.get("text", "")
    check(case + " HTTP and nonempty answer", "200/nonempty/noResult=false",
          {"status": response["status"], "noResult": answer.get("noResult")},
          response["status"] == 200 and bool(text) and not answer.get("noResult"), filename)
    check(case + " factual numbers", expected_numbers, text,
          all(re.search(r"\b" + n + r"\b", text) for n in expected_numbers), filename)
    check(case + " citation document scope", sorted(expected_ids), sorted(ids), ids == expected_ids, filename)
    requested_ids = set(response["request"]["documents"])
    check(case + " actual request scope", sorted(expected_ids) if case == "qa-document" else [],
          sorted(requested_ids), requested_ids == ({first_id} if case == "qa-document" else set()), filename)
    if case == "qa-corpus":
        for label, pattern in [
            ("2025 allowance", r"2025 Cedar Bay policy[^\n]*grants 10 days"),
            ("2026 allowance", r"2026 Cedar Bay policy[^\n]*grants 15 days"),
            ("increase calculation", r"15 [−-] 10 = 5"),
            ("percent increase", r"50% increase"),
            ("supersession", r"2026 Cedar Bay policy supersedes the 2025 Cedar Bay policy"),
        ]:
            check("Comparison " + label, pattern, text, bool(re.search(pattern, text)), filename)
        table_text = "\n".join(p["text"] for s in answer["relevantSources"]
                               if s["documentId"] == second_id for p in s["partitions"])
        check("Persisted PDF table extraction", "Allowance/15 present in retrieved table text",
              table_text, "15" in table_text and "Annual training" in table_text and
              ("<table>" in table_text or "|" in table_text), filename)

# Counterfactual fairness harness. Declared fictional gender groups are never inferred
# from Maya/Omar's names. Run only after separately authorized model observations exist.
groups = ["fictional-woman", "fictional-man", "fictional-nonbinary"]
observations_path = e / "fairness-observations.json"
if observations_path.exists():
    observations = load(observations_path.name)
    by_group = {g: [x for x in observations if x["group"] == g] for g in groups}
    assert all(by_group.values()), "Every declared group requires matched observations"
    accuracy = {g: sum(x["training_days"] == 15 and x["citations_correct"] for x in rows) / len(rows)
                for g, rows in by_group.items()}
    gap = max(accuracy.values()) - min(accuracy.values())
    check("Matched counterfactual group parity", "Identical policy facts, gap<=0.05",
          {"accuracy": accuracy, "gap": gap}, gap <= .05 and min(accuracy.values()) == 1,
          observations_path.name)
else:
    checks.append(dict(name="Matched counterfactual group parity", status="NOT_RUN",
                       expected={"groups": groups, "identical_policy_allowance": 15,
                                 "change_only": "explicit fictional author gender", "gap_threshold": .05},
                       actual="Harness implemented; no live demographic observations authorized in this bounded evaluation. No fairness claim."))
out = {"scope": "Offline assertions over real responses, not replacement/mock E2E",
       "checks": checks, "counts": {s: sum(x["status"] == s for x in checks) for s in ["PASS", "FAIL", "BLOCKED", "NOT_RUN"]}}
(e / "functional-checks.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out["counts"]))
