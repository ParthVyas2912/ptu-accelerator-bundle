"""Finalize only the authorized fourteen-attempt comparison supplement; no network calls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess

b = Path(__file__).resolve().parents[1]
e = b / "evidence/documents"
def load(name):
    return json.loads((e / name).read_text(encoding="utf-8-sig"))
def save(name, obj):
    (e / name).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
def snapshot(name, target):
    if not (e / target).exists():
        (e / target).write_bytes((e / name).read_bytes())

response = load("comparison14-read-result.json")
value = response["value"]
answer = json.loads(value["body"])
metrics = load("comparison14-final-metrics-summary.json")
baseline = load("comparison14-before-metrics-summary.json")
budget = load("model-budget.json")
guard = load("comparison14-guard.json")
state = load("comparison14-final-runtime-state.json")
persistence = load("comparison14-persistence.json")
di = {m["name"]["value"]: sum(p.get("total") or 0 for s in m["timeseries"] for p in s["data"])
      for m in load("comparison14-di-metrics.json")["value"]}
assert di["ProcessedPages"] == 1 and di["TotalErrors"] == 0 and di["TotalCalls"] == 3
assert value["status"] == 200 and not answer["noResult"]
assert response["proof"]["persisted"]
canonical = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
assert hashlib.sha256(canonical).hexdigest() == response["proof"]["sha256"]
assert len(canonical) == response["proof"]["bytes"] == 9493
assert metrics["requests"] == 14 and baseline["requests"] == 12 and metrics["alias_check"]
assert metrics["input_tokens"] > baseline["input_tokens"] and metrics["output_tokens"] > baseline["output_tokens"]
assert all(x["statuscode"] == "200" for x in metrics["statuses"])
assert budget["cap_including_retries"] == 14 and not guard["armed"]
assert all(not r["active"] and r["replicas"] == 0 for app in state["apps"] for r in app["revisions"])
assert persistence["kernel_status"] == persistence["backend_status"] == 200
assert persistence["total_documents"] == 2
original_sources = {x["name"]: x for x in load("retry-phase-sources.json")["result"]}
for x in persistence["files"]:
    assert x["status"] == 200 and x["sha256"] == original_sources[x["name"]]["sha256"]
assert {x["sourceName"] for x in answer["relevantSources"]} == set(original_sources)
assert {x["documentId"] for x in answer["relevantSources"]} == {x["id"] for x in original_sources.values()}
subprocess.run(["python", str(b / "scripts/documents-functional-checks.py")], check=True)
checks = load("functional-checks.json")
assert all(x["status"] == "PASS" for x in checks["checks"] if
           x["name"].startswith(("qa-corpus", "Comparison ", "Persisted PDF table")))
snapshot("result.json", "result-before-comparison14.json")
snapshot("cloud-functional-result.json", "cloud-functional-before-comparison14.json")

weights = {}
for m in load("comparison14-final-metrics-totals.json")["value"]:
    if m["name"]["value"] != "ModelRequests":
        continue
    for series in m["timeseries"]:
        deployment = series["metadatavalues"][0]["value"]
        for point in series["data"]:
            if point.get("total") is not None:
                weights[deployment, point["timeStamp"]] = point["total"]
latency = {}
for m in load("comparison14-final-metrics-latency.json")["value"]:
    for series in m["timeseries"]:
        operation = series["metadatavalues"][0]["value"]
        deployment = "text-embedding-3-large" if "embedding" in operation.lower() else "gpt-5-mini"
        points = [(p["average"], weights.get((deployment, p["timeStamp"]), 0))
                  for p in series["data"] if p.get("average") is not None]
        count = sum(n for _, n in points)
        if count:
            latency[operation] = sum(avg * n for avg, n in points) / count

delta = {k: metrics[k] - baseline[k] for k in ["requests","input_tokens","output_tokens","total_tokens"]}
if budget.get("pending_operation"):
    assert budget["pending_operation"]["case"] == "qa-corpus-approved14"
    budget["reconciled_operations"].append(budget["pending_operation"] | {
        "observed_delta": delta["requests"], "observed_total": 14,
        "application_response_captured": True, "grade": "PASS: both source facts/citations and differences",
        "evidence": "comparison14-final-metrics-summary.json"})
budget.update(actual_observed_attempts=14, remaining_attempts=0, pending_operation=None,
              cap_exhausted=True, further_paid_actions_blocked_reason="Final fourteen-attempt cap exhausted; guard disarmed")
budget["final_comparison_approval"]["guard_armed"] = False
guard.update(armed=False, finalized=True, disarmed_reason="Single approved repeat completed; no further inference authorized")
save("model-budget.json", budget)
save("comparison14-guard.json", guard)

comparison = {
    "status": "PASS", "endpoint": "/Documents/Ask", "http_status": 200,
    "elapsed_ms": value["ms"], "request": value["request"],
    "expected": {"2025_training_days":10,"2026_training_days":15,"increase_days":5,
                 "increase_percent":50,"supersession":"2026 supersedes2025"},
    "actual_answer": answer["text"],
    "citation_document_ids": [x["documentId"] for x in answer["relevantSources"]],
    "citation_source_names": [x["sourceName"] for x in answer["relevantSources"]],
    "source_hashes_verified": True, "response_storage": response["proof"],
    "full_response_evidence": "comparison14-read-result.json", "new_inference": delta,
    "initial_lost_attempt_preserved": "retry-phase-qa-corpus-uncaptured.json"
}
c = load("cloud-functional-result.json")
c["historical_twelve_attempt_telemetry"] = load("cloud-functional-before-comparison14.json")["model_telemetry"]
c.setdefault("historical_uncaptured_comparison", c["scope_qa"]["corpus_comparison"])
c["scope_qa"]["corpus_comparison"] = comparison
per_deployment = [{"model": name, "requests": d["ModelRequests"], "input_tokens": d.get("InputTokens", 0),
                   "output_tokens": d.get("OutputTokens", 0), "total_tokens": d["TotalTokens"], "http_status":200}
                  for name, d in metrics["by_deployment"].items()]
c["model_telemetry"].update(total_observed_requests=14, cap=14, remaining_attempts=0,
    by_deployment=per_deployment, input_tokens=metrics["input_tokens"], output_tokens=metrics["output_tokens"],
    total_tokens=metrics["total_tokens"], operation_average_latency_ms=latency,
    wire_count_caveat="4+4+2+2 original attempts retained, plus2 approved comparison repeat. All14 account statuses200; SDK retries0.")
extra_names = ["Full browser UI","Upstream frontend unit suite","Full /chat orchestration and suggestions",
               "Ten-document, chart and handwriting coverage","Pause/resume source persistence"]
c["tests"] = checks["checks"] + [x for x in c["tests"] if x["name"] in extra_names]
c["retry_budget_finding"] = "Final approved allocation14 exhausted. Recovery-first found no old response; one2-attempt repeat succeeded with full JSON persisted to owned Blob before console."
c["current_runtime_action"] = "PAUSED_VERIFIED: all retained revisions inactive/zero replicas; comparison guard disarmed; no resources deleted."
c["finalized_utc"] = datetime.now(timezone.utc).isoformat()
c["comparison_supplement_persistence"] = persistence
c["comparison_supplement_runtime_state"] = state
c["document_intelligence_telemetry"].update(di)
c["document_intelligence_telemetry"]["final_metrics_evidence"] = "comparison14-di-metrics.json"
save("cloud-functional-result.json", c)

r = load("result.json")
r["status"] = "CORE_INGESTION_DOCUMENT_AND_CORPUS_QA_COMPARISON_VERIFIED_PAUSED_PARTIAL"
r["finalized"] = True
r["current_phase_evidence"] = "evidence/documents/comparison14-final.json"
r["runtime"].update(status=c["current_runtime_action"], corpus_comparison_verified=True,
                    running_full_app=False, full_browser_e2e_verified=False,
                    final_runtime_evidence="evidence/documents/comparison14-final-runtime-state.json")
r["tests"] = c["tests"]
r["inference_telemetry"].update(live_model_requests=14, input_tokens=metrics["input_tokens"],
    output_tokens=metrics["output_tokens"], total_tokens=metrics["total_tokens"], model_latency_ms=latency,
    model_http_statuses=[200]*14, per_deployment=per_deployment,
    ptu_claim="No PTUs created or tested; all14 OpenAI requests used GlobalStandard.",
    comparison_repeat_delta=delta, final_metrics_evidence="comparison14-final-metrics-summary.json")
r["inference_telemetry"]["document_intelligence"] = c["document_intelligence_telemetry"]
r["functional_summary"]["completed_corpus_comparison"] = 1
for label in ["corpus-scoped QA", "two-document comparison with both citations"]:
    if label not in r["functional_summary"]["verified"]:
        r["functional_summary"]["verified"].append(label)
r["functional_summary"]["blocked_or_not_run"] = [x for x in r["functional_summary"]["blocked_or_not_run"]
                                                 if x != "corpus comparison response uncaptured"]
r["functional_summary"]["historical_uncaptured_attempt"] = "Preserved and charged within original12; approved repeat now verified"
for feature in r["ptu"]["per_feature"]:
    if feature["feature"] == "Corpus QA/two-document comparison":
        feature["verification"] = "PASS: original corpus Ask200,2025=10/2026=15,+5/+50%,supersession,both source citations;durableBlobJSON"
        feature["chat_ptu_dependence"] = "Query embedding plus GPT answer;2 approved repeat requests. Entire run14GlobalStandard requests, no PTUs."
    if feature["feature"] == "Vectorization/indexing":
        feature["verification"] = "PASS:two documents persisted/retrieved;7embedding requests including3queries;no new document ingestion"
r["recommendation"] = ("Retain paused resources as authorized; residual estimate$0.245/hour plus shared allocations/usage. "
    "Corpus comparison now verified with durable Blob evidence. Final14-attempt cap exhausted and guard disarmed. "
    "Do not count as fully verified browser app:public403,summary greeting defects,2/10coverage and untestedfull/chat remain.")
save("result.json", r)
final = {
    "status":r["status"],"finalized":True,"approval":load("comparison14-approval.json"),
    "recovery":load("comparison14-recovery-result.json"),"comparison":comparison,
    "capture_probe":load("comparison14-probe.json"),"offline_capture_tests":{"passed":4,"model_calls":0},
    "metrics":metrics,"prior_twelve_attempts_preserved":True,"new_attempts":2,
    "document_intelligence":c["document_intelligence_telemetry"],
    "runtime_state":state,"guard":guard,"persistence":persistence,"functional_checks":checks["counts"],
    "limits":["2/10logicalfixtures","publicbrowser403","bothsummarygreetingdefects","full/chatnotrun",
              "chart/handwriting/fairnessnotrun"],"full_app_e2e_passed":False,
    "cost_usd_hour":c["cost_usd_hour"],"model_or_infrastructure_configuration_changes":False,
    "runtime_state_changes":"Resumed then paused existing revisions only",
    "data_changes":"Probe, immutable attempt lock and response evidence blobs in existing smemory; no additional documents ingested"
}
save("comparison14-final.json", final)

summary_path = b / "reports/documents-current-summary.md"
text = summary_path.read_text(encoding="utf-8")
lines = text.splitlines()
for i, line in enumerate(lines):
    if line.startswith("| Corpus QA / two-document comparison"):
        lines[i] = ("| Corpus QA / two-document comparison |10 to15 days,+5/+50%,2026 supersedes2025,both cited |"
                    "**PASS:** one explicitly approved repeat returned200 in15.103s; all facts and both citation IDs/names verified. "
                    "Full9493-byte JSON persisted in owned private Blob before console and read back with matchingSHA256. Original lost attempt retained. |")
    if line.startswith("**12/12 OpenAI") or line.startswith("**14/14 OpenAI"):
        g = metrics["by_deployment"]["gpt-5-mini"]; emb = metrics["by_deployment"]["text-embedding-3-large"]
        lines[i] = (f"**14/14 OpenAI attempts consumed, all account HTTP statuses200. Guard disarmed; no further inference authorized.** "
                    f"GPT-5-mini:{int(g['ModelRequests'])} requests,{int(g['InputTokens'])}input +{int(g['OutputTokens'])}output "
                    f"={int(g['TotalTokens'])}tokens. Embedding-3-large:{int(emb['ModelRequests'])} requests,{int(emb['InputTokens'])}input tokens. "
                    f"**Total{int(metrics['total_tokens'])}tokens:{int(metrics['input_tokens'])}input +{int(metrics['output_tokens'])}output.** "
                    f"The approved repeat added{int(delta['input_tokens'])}input +{int(delta['output_tokens'])}output tokens; all original12 records remain. "
                    "Dedicated-account Azure Monitor counters/status aliases agree; aliases are not summed. DI remains separately billed:1page,3successfulHTTPcalls.")
    if line.startswith("- Unicode capture is now"):
        lines[i] = ("- Recovery first inspected18 ownedBlobobjects/13eligible text-JSON contents plus both Mongo databases; "
                    "no old comparison/history/stored responseID was recoverable. No reconstruction. The approved repeat's fullJSON is at "
                    "`smemory/_dkm-evaluation/comparison14-result.json`,SHA256`99a60b96a6867bf9f96ff9297daf2d7497158b79f3cfa57f11a9357619327704`. "
                    "Managed identity was used; no keys/SAS. UTF8/ASCII-safe transport and4offline capture checks passed. "
                    "The probe/lock/result are evidence blobs, not ingested documents or new infrastructure.")
    if line.startswith("**Smallest remaining comparison action:**") or line.startswith("**Final comparison budget"):
        lines[i] = ("**Final comparison budget exhausted:**14/14 used; no additional quality/probing calls. "
                    "Publicbrowser403, both stored greeting defects,2/10coverage and full/chat coverage remain explicit limitations. "
                    "Final proof:`comparison14-final.json`,`comparison14-final-metrics-summary.json`,`comparison14-final-runtime-state.json`. "
                    "All replicas are zero, existing sources remain intact, and the one-shot guard is disarmed.")
current = "\n".join(lines) + "\n"
summary_path.write_text(current, encoding="utf-8")
report = b / "reports/documents.md"
old = report.read_text(encoding="utf-8")
history = old.split("## Historical phase logs", 1)[1]
report.write_text("# Document Knowledge Mining evaluation\n\n" + current +
                  "\n## Historical phase logs" + history, encoding="utf-8")

runbook = b / "reports/documents-cloud-runbook.md"
book = runbook.read_text(encoding="utf-8")
book = book.replace("Corpus comparison was attempted but its output was lost to Azure CLI Unicode encoding; it is not graded as a pass.",
                    "The original corpus response was lost, but the explicitly approved2-attempt repeat is now verified with both citations and correct10-to15/+5/+50% comparison; fullJSON is durable in ownedBlob.")
start = book.index("**12/12 OpenAI") if "**12/12 OpenAI" in book else book.index("**14/14 OpenAI")
end = book.index("\n\nDo not repeat", start)
book = book[:start] + (f"**14/14 OpenAI attempts used; guard disarmed; no further inference authorized.** "
    f"All account statuses200. Total{int(metrics['total_tokens'])}tokens "
    f"({int(metrics['input_tokens'])}input,{int(metrics['output_tokens'])}output), including the original12 attempts. "
    "DI remains separate:1processed page,3successfulHTTPcalls. See`comparison14-final-metrics-summary.json`.") + book[end:]
start = book.index("Real request accounting:")
end = book.index("\n\nSafe read-only checks", start)
book = book[:start] + (
    "Real request accounting:4first ingestion +4second ingestion +2document QA +2lost corpus attempt +2approved repeat =14. "
    "Both actual document-scoped and corpus comparison /Documents/Ask routes are verified; full/chat synthesis/suggestions remain untested. "
    "Recovery first found no previous result in ownedBlob/Mongo/history or stored responseID. The repeat saved fullJSON to "
    "`https://stdkmeval0911a.blob.core.windows.net/smemory/_dkm-evaluation/comparison14-result.json` before console export, "
    "then verified readback SHA256`99a60b96a6867bf9f96ff9297daf2d7497158b79f3cfa57f11a9357619327704` (9493bytes). "
    "Blob access uses existing managed identity over private networking, never keys/SAS. The permanent attempt-lock blob and "
    "`comparison14-guard.json` prevent an accidental repeat. Do not remove the lock or re-arm the guard to run more inference.\n\n"
    "After a future authorized read-only Resume, durable response retrieval can restage the evaluator without inference:\n\n"
    "```powershell\n"
    ".\\scripts\\Invoke-DocumentsComparison14.ps1 -Mode read-result -Container smemory -EvidenceLabel operator-recovery-1 -Stage\n"
    "```\n\n"
    "Use a unique read-only evidence label; the command refuses overwriting existing local evidence. "
    "Console staging uses short chunks; honor any429Retry-After600 response rather than changing identities or ingress. "
    "No future comparison request is authorized by this runbook."
    ) + book[end:]
runbook.write_text(book, encoding="utf-8")
print(json.dumps({"status":r["status"],"requests":14,"tokens":metrics["total_tokens"],
                  "input_tokens":metrics["input_tokens"],"output_tokens":metrics["output_tokens"],
                  "new_attempt_delta":delta,"checks":checks["counts"],"paused":True,"guard_armed":False}, indent=2))
