"""One tiny REAL browser -> API -> Azure persistence -> five-agent batch -> ZIP run."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time
import zipfile

import requests
from playwright.sync_api import sync_playwright, expect

B = Path(__file__).resolve().parents[1]
OUT = B / "evidence/modernize"
RESULT = OUT / "native-e2e.json"
API = "http://127.0.0.1:8114"
UI = "http://127.0.0.1:5114"
if RESULT.exists() and json.loads(RESULT.read_text()).get("processing_clicked"):
    raise SystemExit("Processing already clicked in prior evidence; do not accidentally spend again.")
state = {"scope": "real browser and original native app with actual Azure Cosmos/Blob",
         "started": datetime.now(timezone.utc).isoformat(), "events": [], "page_errors": [],
         "processing_clicked": False, "tests": [], "uploads": [], "websockets": []}


def save():
    RESULT.write_text(json.dumps(state, indent=2), encoding="utf-8")


def fetch(path):
    r = requests.get(API+path, timeout=120)
    return {"http_status": r.status_code, "body": r.json()}


state["preflight"] = fetch("/eval/status")
assert state["preflight"]["body"]["agents_initialized"], "Original SQL agents not initialized"
assert state["preflight"]["body"]["model_http_attempts_remaining"] >= 6, "Insufficient bounded batch allowance"
state["persistence_preflight"] = fetch("/api/batch-history")
if state["persistence_preflight"]["http_status"] != 200:
    state["error"] = {"type": "PersistencePreflightBlocked",
                      "message": "Original Cosmos-backed history route is not ready; no upload/processing/model call attempted."}
    state["tests"].append({"id": "real-persistence-preflight", "expected": "HTTP 200 from native Cosmos-backed history",
                           "actual": state["persistence_preflight"], "passed": False})
save()
if state.get("error"):
    raise SystemExit(state["error"]["message"])

executables = list((Path(os.environ["LOCALAPPDATA"])/"ms-playwright").glob("chromium-*/chrome-win*/chrome.exe"))
if not executables:
    raise SystemExit("No existing Chromium found; no browser download attempted.")
executable = max(executables, key=lambda p: int(re.search(r"chromium-(\d+)", str(p)).group(1)))

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=str(executable),
                                args=["--renderer-process-limit=2"])
    context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
    page = context.new_page()
    page.on("pageerror", lambda error: state["page_errors"].append(str(error)))
    def socket_observed(socket):
        item = {"url": socket.url, "frames_received": []}
        state["websockets"].append(item)
        socket.on("framereceived", lambda payload: item["frames_received"].append(str(payload)[:1800]))
    page.on("websocket", socket_observed)

    def response_observed(response):
        if not response.url.startswith(API):
            return
        event = {"url": response.url, "status": response.status, "method": response.request.method}
        if "/api/upload" in response.url:
            try:
                body = response.json()
                event["body"] = body
                state["uploads"].append(body)
            except Exception:
                pass
        state["events"].append(event)
        save()

    page.on("response", response_observed)
    started = time.monotonic()
    try:
        page.goto(UI, wait_until="networkidle", timeout=90000)
        expect(page.get_by_text("Modernize your code", exact=False).first).to_be_visible(timeout=30000)
        state["tests"].append({"id": "real-ui", "expected": "Original UI renders", "actual": "visible", "passed": True})
        page.screenshot(path=str(OUT/"native-home.png"), full_page=True)

        # A non-SQL file must be rejected client-side without model consumption.
        page.locator("input[type=file]").set_input_files(
            {"name": "ptu-invalid.txt", "mimeType": "text/plain", "buffer": b"not a SQL file"})
        page.wait_for_timeout(1000)
        rejected = "Only .sql files are allowed" in page.locator("body").inner_text()
        state["tests"].append({"id": "unsupported-extension", "expected": "Reject .txt without model calls",
                               "actual": rejected, "passed": rejected})
        # Real upload to Azure through the app (UI starts both uploads).
        page.locator("input[type=file]").set_input_files([
            str(B/"test-data/modernize/ptu-malformed.sql"),
            str(B/"test-data/modernize/ptu-nvl.sql"),
        ])
        button = page.get_by_role("button", name="Start translating", exact=False)
        expect(button).to_be_enabled(timeout=180000)
        assert len(state["uploads"]) == 2, "Expected two real upload API responses"
        assert all(item.get("file", {}).get("file_id") for item in state["uploads"]), "Upload API failed"
        state["batch_id"] = state["uploads"][0]["file"]["batch_id"]
        state["tests"].append({"id": "real-two-file-upload", "expected": "Two file records in one batch",
                               "actual": [u["file"]["original_name"] for u in state["uploads"]], "passed": True})
        page.screenshot(path=str(OUT/"native-uploaded.png"), full_page=True)
        # Exactly one click, persisted before sending model-consuming request.
        state["processing_clicked"] = True
        save()
        with page.expect_response(
            lambda response: response.url.endswith("/api/start-processing") and response.request.method == "POST",
            timeout=900000
        ) as completion:
            button.click()
        response = completion.value
        state["processing"] = {"http_status": response.status, "body": response.json(),
                               "elapsed_seconds": round(time.monotonic()-started, 3)}
        page.wait_for_timeout(3000)
        state["summary"] = fetch("/api/batch-summary/"+state["batch_id"])
        state["final_status"] = fetch("/eval/status")
        state["run_usage"] = fetch("/eval/usage")
        page.screenshot(path=str(OUT/"native-completed.png"), full_page=True)
        state["final_ui_text"] = page.locator("body").inner_text()
        button = page.get_by_role("button", name="Download all as .zip", exact=False)
        expect(button).to_be_enabled(timeout=30000)
        with page.expect_download(timeout=90000) as download:
            button.click()
        download.value.save_as(OUT/"native-results.zip")
        with zipfile.ZipFile(OUT/"native-results.zip") as archive:
            state["download"] = {"filename": download.value.suggested_filename,
                                 "members": archive.namelist()}
            state["download"]["sql"] = {name: archive.read(name).decode("utf-8-sig")
                                        for name in archive.namelist()}
        state["tests"].append({"id": "real-browser-download", "expected": "ZIP containing translated valid file",
                               "actual": state["download"]["members"],
                               "passed": any("ptu-nvl" in n for n in state["download"]["members"])})
    except Exception as exc:
        state["error"] = {"type": type(exc).__name__, "message": str(exc)[:2400]}
        try:
            state["final_status"] = fetch("/eval/status")
            state["run_usage"] = fetch("/eval/usage")
            if state.get("batch_id"):
                state["summary"] = fetch("/api/batch-summary/"+state["batch_id"])
            state["final_ui_text"] = page.locator("body").inner_text()
            page.screenshot(path=str(OUT/"native-blocker.png"), full_page=True)
        except Exception as secondary:
            state["secondary_error_type"] = type(secondary).__name__
    finally:
        state["elapsed_seconds"] = round(time.monotonic()-started, 3)
        save()
        browser.close()

print(json.dumps({"batch_id": state.get("batch_id"), "tests": state["tests"],
                  "error": state.get("error"), "final_status": state.get("final_status")}, indent=2))
