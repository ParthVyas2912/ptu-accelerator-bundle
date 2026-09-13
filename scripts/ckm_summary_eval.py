"""Bounded component evaluation through CKM's original summarization API route.

Run only inside the approved CKM container. The serving process stays
unconfigured; endpoint settings below affect this short-lived probe process.
No agents, retrieval, CU, embeddings, or generic replacement chat are invoked.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import socket
import time
from urllib.parse import urlsplit

ACCOUNT = "aif-ptu-conversation-7d804f70"
ENDPOINT = f"https://{ACCOUNT}.openai.azure.com"
DEPLOYMENT = "gpt-5.2"
EXPECTED_VERSION = "2025-12-11"
PASS_LIMIT = 7
REPORT = Path("/tmp/ckm-summary-pass.json")
FIXTURE = Path(__file__).with_name("ckm-support-conversations.json")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def persist(report, path):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class Meter:
    def __init__(self, report, path, limit=PASS_LIMIT):
        self.report = report
        self.path = path
        self.limit = limit
        self.case = ""

    def wrap(self, raw_create):
        def create(*args, **kwargs):
            if kwargs.get("model") != DEPLOYMENT or kwargs.get("stream"):
                raise RuntimeError("Only approved, non-streaming native summaries are permitted")
            if len(self.report["requests"]) >= self.limit:
                raise RuntimeError("Component pass request budget exhausted; request not sent")
            item = {
                "sequence": len(self.report["requests"]) + 1,
                "case": self.case,
                "deployment": DEPLOYMENT,
                "expected_model_version": EXPECTED_VERSION,
                "started_at": utc_now(),
                "status": "dispatching",
                "usage": None,
            }
            self.report["requests"].append(item)
            persist(self.report, self.path)
            started = time.perf_counter()
            try:
                raw = raw_create(*args, **kwargs)
                item["http_status"] = raw.status_code
                result = raw.parse()
                item["returned_model"] = result.model
                item["usage"] = result.usage.model_dump() if result.usage else None
                item["status"] = "completed"
                return result
            except Exception as exc:
                # Record only safe exception metadata, then propagate the failure.
                item["status"] = "failed"
                item["error_type"] = type(exc).__name__
                item["http_status"] = getattr(exc, "status_code", None)
                raise
            finally:
                item["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
                persist(self.report, self.path)
        return create


def configure():
    for name in (
        "AZURE_FOUNDRY_ENDPOINT", "AZURE_AI_AGENT_ENDPOINT", "AGENT_NAME_CHAT",
        "AGENT_NAME_TITLE", "AZURE_SEARCH_ENDPOINT", "AZURE_SQL_SERVER",
        "AZURE_STORAGE_ACCOUNT", "AZURE_COSMOS_ENDPOINT",
        "AZURE_CONTENT_UNDERSTANDING_ENDPOINT",
    ):
        os.environ[name] = ""
    os.environ["AZURE_OPENAI_ENDPOINT"] = ENDPOINT
    os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"] = DEPLOYMENT
    os.environ["APP_ENV"] = "development"
    os.environ["ENABLE_EXTERNAL_DATA_SOURCES"] = "false"
    from src.api.capabilities._llm import get_llm_client
    client = get_llm_client()
    client.max_retries = 0
    return client


def probe():
    result = {
        "scope": "CKM own AI endpoint metadata probe, not inference",
        "endpoint": ENDPOINT,
        "model_requests": 0,
        "checked_at": utc_now(),
    }
    host = urlsplit(ENDPOINT).hostname
    try:
        result["addresses"] = sorted({
            row[4][0] for row in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        })
    except socket.gaierror as exc:
        result["dns_error"] = type(exc).__name__
        print(json.dumps(result))
        return 2
    client = configure()
    try:
        response = client.models.with_raw_response.list()
        result["http_status"] = response.status_code
        result["metadata_access"] = "succeeded"
        result["model_requests"] = 0
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        result["http_status"] = status
        result["error_type"] = type(exc).__name__
        message = str(exc).lower()
        result["network_denial_indicated"] = status == 403 and any(
            term in message for term in ("firewall", "virtual network", "public network")
        )
        result["metadata_access"] = "failed"
        print(json.dumps(result))
        return 2
    finally:
        client.close()
    print(json.dumps(result))
    return 0


def checks(text, case_index):
    text = text.lower()
    if case_index == 2:
        return {
            "printer_mentioned": "printer" in text or "printing" in text,
            "uncertainty_explicit": bool(re.search(
                r"unknown|uncertain|unconfirmed|unclear|cannot confirm|not confirmed", text
            )),
            "callback_or_followup": bool(re.search(r"callback|follow.up|call.*tomorrow", text)),
            "exact_error_requested": "error" in text,
        }
    return {
        "vpn_issue": "vpn" in text,
        "credential_cache_cause": bool(re.search(r"cache|stale|saved credential|old credential", text)),
        "recovery_or_resolution": bool(re.search(r"connect|restor|resolv|success", text)),
        "followup": bool(re.search(
            r"tomorrow|guide" if case_index == 0 else r"friday|onboarding|checklist", text
        )),
    }


def evaluate(include_counterfactuals):
    # An existing file blocks rerunning the live pass in this replica.
    with REPORT.open("x", encoding="utf-8") as initial:
        initial.write("{}\n")
    report = {
        "scope": "Original CKM /api/processing/summarize in-process API component",
        "not_full_app_or_ptu_test": True,
        "endpoint": ENDPOINT,
        "deployment": DEPLOYMENT,
        "expected_model_version": EXPECTED_VERSION,
        "pass_request_limit": PASS_LIMIT,
        "overall_user_limit": 12,
        "sdk_retries": 0,
        "started_at": utc_now(),
        "requests": [],
        "tests": [],
        "status": "running",
        "limitations": [
            "Original API handlers run through TestClient in a short-lived cloud process.",
            "No durable ingestion, Search grounding, cross-call citations, SQL dashboard or CU test.",
            "Four counterfactual cases, if run, do not establish statistical fairness.",
            "Report is replica-local: export before stopping; do not rerun on a fresh replica.",
        ],
    }
    persist(report, REPORT)
    client = configure()
    assert client.max_retries == 0
    meter = Meter(report, REPORT)
    raw_create = client.chat.completions.with_raw_response.create
    client.chat.completions.create = meter.wrap(raw_create)

    from fastapi.testclient import TestClient
    from src.api.main import app
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cases = [
        (item["id"], item["text"], index, None)
        for index, item in enumerate(fixture)
    ]
    if include_counterfactuals:
        for gender, age in (("woman", 30), ("man", 30), ("nonbinary", 30), ("woman", 65)):
            cases.append((
                f"counterfactual-{gender}-{age}",
                f"Synthetic caller self-description: {gender}, age {age}. " + fixture[0]["text"],
                0,
                {"gender": gender, "age": age},
            ))
    api = TestClient(app)
    try:
        for case_id, text, index, demographic in cases:
            meter.case = case_id
            started = time.perf_counter()
            response = api.post("/api/processing/summarize", json={
                "text": text, "max_length": 180, "style": "bullet_points",
            })
            item = {
                "id": case_id,
                "expected": "Native summary preserves issue, resolution/follow-up and stated uncertainty",
                "http_status": response.status_code,
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                "demographic_counterfactual": demographic,
            }
            if response.status_code != 200:
                item["status"] = "failed"
                item["actual"] = "Native route failed; see safe request metadata"
                report["tests"].append(item)
                report["status"] = "stopped_after_first_failure"
                persist(report, REPORT)
                break
            body = response.json()
            item["actual"] = body
            item["fact_checks"] = checks(body["summary"], index)
            item["status"] = "fact_checks_passed_pending_manual_review" if all(
                item["fact_checks"].values()
            ) else "fact_check_failure"
            report["tests"].append(item)
            persist(report, REPORT)
            time.sleep(5)
        else:
            report["status"] = "completed_pending_manual_review"
    finally:
        api.close()
        client.close()
        report["finished_at"] = utc_now()
        report["actual_model_requests"] = len(report["requests"])
        persist(report, REPORT)
    print(json.dumps(report))
    return 0 if report["status"] == "completed_pending_manual_review" else 2


def selftest():
    import tempfile
    from types import SimpleNamespace
    import unittest

    class MeterTests(unittest.TestCase):
        def test_budget_and_usage(self):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "report.json"
                report = {"requests": []}
                meter = Meter(report, path, limit=1)
                usage = SimpleNamespace(model_dump=lambda: {"prompt_tokens": 4, "completion_tokens": 2})
                completion = SimpleNamespace(model="gpt-5.2-2025-12-11", usage=usage)
                calls = []
                def raw(**kwargs):
                    calls.append(kwargs)
                    return SimpleNamespace(status_code=200, parse=lambda: completion)
                wrapped = meter.wrap(raw)
                self.assertIs(wrapped(model=DEPLOYMENT), completion)
                with self.assertRaisesRegex(RuntimeError, "budget exhausted"):
                    wrapped(model=DEPLOYMENT)
                self.assertEqual(len(calls), 1)
                self.assertEqual(report["requests"][0]["usage"]["prompt_tokens"], 4)

        def test_failed_attempt_is_charged(self):
            with tempfile.TemporaryDirectory() as directory:
                report = {"requests": []}
                meter = Meter(report, Path(directory) / "report.json", limit=1)
                def fail(**kwargs):
                    raise TimeoutError()
                wrapped = meter.wrap(fail)
                with self.assertRaises(TimeoutError):
                    wrapped(model=DEPLOYMENT)
                self.assertEqual(len(report["requests"]), 1)
                self.assertEqual(report["requests"][0]["status"], "failed")
                with self.assertRaises(RuntimeError):
                    wrapped(model=DEPLOYMENT)

        def test_wrong_model_and_stream_not_sent(self):
            with tempfile.TemporaryDirectory() as directory:
                report = {"requests": []}
                meter = Meter(report, Path(directory) / "report.json")
                wrapped = meter.wrap(lambda **kwargs: self.fail("Must not dispatch"))
                for kwargs in ({"model": "other"}, {"model": DEPLOYMENT, "stream": True}):
                    with self.assertRaises(RuntimeError):
                        wrapped(**kwargs)
                self.assertEqual(report["requests"], [])

        def test_real_sdk_raw_wrapper_without_network(self):
            import httpx
            from openai import AzureOpenAI
            with tempfile.TemporaryDirectory() as directory:
                calls = []
                def handler(request):
                    calls.append(request)
                    return httpx.Response(200, json={
                        "id": "offline-completion", "object": "chat.completion", "created": 0,
                        "model": "gpt-5.2-2025-12-11",
                        "choices": [{"index": 0, "finish_reason": "stop",
                                     "message": {"role": "assistant", "content": "Offline summary"}}],
                        "usage": {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
                    })
                client = AzureOpenAI(
                    azure_endpoint="https://offline.invalid", api_version="2024-10-21",
                    azure_ad_token_provider=lambda: "offline-placeholder-not-a-credential",
                    max_retries=0, http_client=httpx.Client(transport=httpx.MockTransport(handler)),
                )
                report = {"requests": []}
                meter = Meter(report, Path(directory) / "report.json")
                raw = client.chat.completions.with_raw_response.create
                client.chat.completions.create = meter.wrap(raw)
                completion = client.chat.completions.create(
                    model=DEPLOYMENT, messages=[{"role": "user", "content": "Offline test"}]
                )
                self.assertEqual(completion.choices[0].message.content, "Offline summary")
                self.assertEqual(len(calls), 1)
                self.assertEqual(report["requests"][0]["http_status"], 200)
                self.assertEqual(report["requests"][0]["usage"]["total_tokens"], 6)
                client.close()

    outcome = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(MeterTests)
    )
    return 0 if outcome.wasSuccessful() else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["probe", "run", "export", "selftest"])
    parser.add_argument("--counterfactuals", action="store_true")
    args = parser.parse_args()
    if args.mode == "selftest":
        raise SystemExit(selftest())
    if args.mode == "probe":
        raise SystemExit(probe())
    if args.mode == "export":
        print(REPORT.read_text(encoding="utf-8"))
        raise SystemExit(0)
    raise SystemExit(evaluate(args.counterfactuals))
