"""Deterministic verification against real API history, source blobs and index.

This script performs zero model calls. It does not inject source text into
the application or replace its retrieval/generation behavior.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote
import httpx
import psycopg2

B = Path(r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\projects\PTU accelerator Bundle")
E = B / "evidence" / "cwyd"
API = "http://127.0.0.1:8112"
norm = lambda value: value.replace("\r\n", "\n").strip()


def load(name):
    return json.loads((E / name).read_text(encoding="utf-8"))


def history(conversation_id):
    response = httpx.get(API + "/api/history/conversations/" + conversation_id, timeout=60)
    response.raise_for_status()
    return response.json()


parser = argparse.ArgumentParser()
parser.add_argument("stage", choices=["initial", "update"])
stage = parser.parse_args().stage
receipt = load("questions-grouped.json" if stage == "initial" else "question-update.json")
assert receipt["status"] == 200
answer = receipt["actual"]
saved = history(answer["conversation_id"])
assistant = [message for message in saved["messages"] if message["role"] == "assistant"][-1]
tests = []


def record(name, expected, actual, passed):
    tests.append({"name": name, "expected": expected, "actual": actual,
                  "verdict": "PASS" if passed else "FAIL"})


record("persisted_answer", answer["content"], assistant["content"],
       assistant["content"] == answer["content"])
stored_citations = assistant.get("metadata", {}).get("citations", [])
record("persisted_citations", answer["citations"], stored_citations,
       stored_citations == answer["citations"])
source_checks = []
with psycopg2.connect(host="127.0.0.1", port=15432, dbname="ptu_cwyd", user="cwyd") as conn:
    with conn.cursor() as cursor:
        for citation in answer["citations"]:
            title = citation["title"]
            response = httpx.get(API + "/api/files/" + quote(title), timeout=60)
            response.raise_for_status()
            raw = response.content
            text = raw.decode("utf-8")
            cursor.execute("SELECT id,title,content FROM documents WHERE title=%s", (title,))
            rows = cursor.fetchall()
            matched = [row for row in rows if row[0] == citation["metadata"]["source_id"]]
            valid = (len(matched) == 1 and norm(matched[0][2]) == norm(citation["snippet"])
                     and norm(citation["snippet"]) == norm(text))
            source_checks.append({
                "title": title, "source_id": citation["metadata"]["source_id"],
                "api_file_status": response.status_code, "source_sha256": hashlib.sha256(raw).hexdigest(),
                "source_body": text, "index_rows_for_title": len(rows),
                "index_content": matched[0][2] if matched else None,
                "citation_snippet": citation["snippet"],
                "verdict": "PASS" if valid else "FAIL",
            })
        cursor.execute("SELECT count(*),count(DISTINCT title) FROM documents")
        indexed_chunks, indexed_titles = cursor.fetchone()
record("citation_blob_and_index_grounding", "every citation source ID/snippet matches real index and source blob",
       source_checks, all(check["verdict"] == "PASS" for check in source_checks) and bool(source_checks))

if stage == "initial":
    sections = {int(number): body.strip() for number, body in
                re.findall(r"(?ms)^(\d+)\.\s+(.*?)(?=^\d+\.\s|\Z)", answer["content"])}
    expected_facts = [
        (1, r"\b73\b", "ptu-cwyd-travel.txt", "73 credits per travel day"),
        (2, r"\b640\b", "ptu-cwyd-learning.txt", "640 credits annually"),
        (3, r"\b(two|2)\b", "ptu-cwyd-remote.txt", "two remote days each week"),
        (4, r"\b(seven|7)\b", "ptu-cwyd-records.txt", "seven-year retention"),
        (5, r"\b90\b", "ptu-cwyd-equipment.txt", "90-day calibration interval"),
    ]
    citations_by_marker = {citation["id"]: citation["title"] for citation in answer["citations"]}
    for number, pattern, title, expected in expected_facts:
        section = sections.get(number, "")
        titles = {citations_by_marker.get(marker) for marker in re.findall(r"\[doc\d+\]", section)}
        record("factual_" + str(number), expected + " with " + title, section,
               bool(re.search(pattern, section, re.I)) and title in titles)
    comparison = sections.get(6, "")
    comparison_sources = {citations_by_marker.get(marker) for marker in re.findall(r"\[doc\d+\]", comparison)}
    record("cross_document_comparison", "21 travel days versus45 learning days; both source citations", comparison,
           "21" in comparison and "45" in comparison
           and {"ptu-cwyd-travel.txt", "ptu-cwyd-learning.txt"} <= comparison_sources)
    absent = sections.get(7, "")
    record("absent_answer", "explicit insufficient evidence, no invented allowance", absent,
           "insufficient evidence" in absent.lower() and "orbital" in absent.lower()
           and not re.search(r"\d+\s+credits", absent, re.I))
else:
    travel = [check for check in source_checks if check["title"] == "ptu-cwyd-travel.txt"]
    content = answer["content"].lower()
    record("contradictory_replacement", "active91 credits supersedes73 with travel citation", answer["content"],
           bool(travel) and "91" in content and "73" in content
           and any(word in content for word in ["supersed", "replac", "previous", "updated"]))
    record("active_blob_and_index", "one current travel chunk containing version2 and now91 credits",
           travel, bool(travel) and travel[0]["index_rows_for_title"] == 1
           and "Travel Policy, version 2" in travel[0]["source_body"]
           and "now 91 credits" in travel[0]["index_content"])
    old = load("questions-grouped.json")["actual"]
    old_saved = history(old["conversation_id"])
    old_assistant = [m for m in old_saved["messages"] if m["role"] == "assistant"][-1]
    record("historical_answer_and_snippets_preserved", "old conversation keeps original answer and citation metadata",
           {"content": old_assistant["content"], "citations": old_assistant.get("metadata", {}).get("citations")},
           old_assistant["content"] == old["content"]
           and old_assistant.get("metadata", {}).get("citations") == old["citations"])
record("index_source_count", "five policy titles and five active chunks",
       {"titles": indexed_titles, "chunks": indexed_chunks}, indexed_titles == indexed_chunks == 5)
output = {"stage": stage, "conversation_id": answer["conversation_id"],
          "app_call_latency_ms": receipt["latency_ms"], "tests": tests,
          "history": saved, "source_checks": source_checks,
          "passed": sum(test["verdict"] == "PASS" for test in tests),
          "failed": sum(test["verdict"] == "FAIL" for test in tests)}
(E / f"verified-{stage}.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
print(json.dumps({"stage": stage, "passed": output["passed"], "failed": output["failed"],
                  "tests": [{"name": t["name"], "verdict": t["verdict"]} for t in tests]}, indent=2))
