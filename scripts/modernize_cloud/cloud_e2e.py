"""One real original-app batch via loopback HTTP inside the approved cloud container.

Invoke only through authenticated Azure exec. This is API/worker/persistence E2E,
not a claim that a browser performed upload or download.
"""
import argparse
import collections
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import time
import uuid
import zipfile
import requests
from budget import assert_evaluation_open, production_budget

parser = argparse.ArgumentParser()
parser.add_argument("--execute", action="store_true", required=True)
args = parser.parse_args()
assert_evaluation_open()
budget = production_budget()
initial, _ = budget.read()
if initial["claimed_batch"] is not None or initial["events"]:
    raise SystemExit("Prior cloud processing exists; do not repeat or reset the global budget.")
API = "http://127.0.0.1:8000"
sources = {
    "ptu-malformed.sql": "SELEC customer_id FROM WHERE;",
    "ptu-nvl.sql": """SELECT o.order_id, o.customer_id,
    (SELECT NVL(SUM(ob.order_total), 0) FROM orders_backup ob
      WHERE ob.customer_id = o.customer_id) AS customer_total
FROM orders o;""",
}
state = {"scope": "Original app API/worker + real private Cosmos/Blob + original SQL agents, adapted cloud runtime",
         "browser_e2e": False, "started": datetime.now(timezone.utc).isoformat(),
         "batch_id": str(uuid.uuid4()), "uploads": [], "tests": [],
         "processing_sent": False}


def save():
    budget.record("cloud_e2e", state)
    Path("/tmp/modernize-cloud-e2e.json").write_text(json.dumps(state, indent=2), encoding="utf-8")


def get(path):
    response = requests.get(API+path, timeout=120)
    return {"http_status": response.status_code, "body": response.json()}


started = time.monotonic()
try:
    state["preflight"] = get("/eval/status")
    assert state["preflight"]["http_status"] == 200
    assert state["preflight"]["body"]["agents_initialized"]
    assert state["preflight"]["body"]["model_http_attempts_total"] == 4
    state["history_before"] = get("/api/batch-history")
    assert state["history_before"]["http_status"] == 200
    save()
    for name, sql in sources.items():
        response = requests.post(API+"/api/upload", data={"batch_id": state["batch_id"]},
                                 files={"file": (name, sql.encode(), "application/sql")}, timeout=120)
        state["uploads"].append({"name": name, "http_status": response.status_code, "body": response.json()})
        save()
        assert response.status_code == 200
    state["tests"].append({"id": "two-file-real-upload", "expected": "Both original upload API requests succeed",
                           "actual": [r["http_status"] for r in state["uploads"]], "passed": True})
    budget.set_enabled(True, expected_total=4)
    state["processing_sent"] = True
    save()  # Preserve intent before sending the one processing request.
    process_start = time.monotonic()
    response = requests.post(API+"/api/start-processing", json={
        "batch_id": state["batch_id"], "translate_from": "informix", "translate_to": "tsql"
    }, timeout=900)
    state["processing"] = {"http_status": response.status_code, "body": response.json(),
                           "elapsed_seconds": round(time.monotonic()-process_start, 3)}
    budget.set_enabled(False)
    state["summary"] = get("/api/batch-summary/"+state["batch_id"])
    state["story"] = get("/api/batch-story/"+state["batch_id"])
    state["files"] = []
    for item in state["uploads"]:
        file_id = item["body"].get("file", {}).get("file_id")
        if file_id:
            state["files"].append(get("/api/file/"+file_id))
    download = requests.get(API+"/api/download/"+state["batch_id"],
                            params={"batch_id": state["batch_id"]}, timeout=120)
    state["download"] = {"http_status": download.status_code}
    if download.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
            sqls = {name: archive.read(name).decode("utf-8-sig") for name in archive.namelist()}
        state["download"].update(members=list(sqls), sql=sqls)
        state["parser_tests"] = []
        for name, target in sqls.items():
            parsed = subprocess.run(["/app/sql_agents/tools/linux-x64/tsqlParser", "--string", target],
                                    capture_output=True, text=True, timeout=60)
            state["parser_tests"].append({"name": name, "exit_code": parsed.returncode,
                                           "errors": json.loads(parsed.stdout)})
            if "ptu-nvl" not in name:
                continue
            db = sqlite3.connect(":memory:")
            db.executescript(
                "CREATE TABLE orders(order_id INTEGER, customer_id INTEGER);"
                "CREATE TABLE orders_backup(customer_id INTEGER, order_total REAL);"
                "INSERT INTO orders VALUES(1,10),(2,10),(3,20),(4,30),(5,NULL);"
                "INSERT INTO orders_backup VALUES(10,2.5),(10,7.5),(20,NULL),(40,99);")
            # Never permit generated SQL to write, attach files, or change configuration.
            db.set_authorizer(lambda action, a, b, c, d: sqlite3.SQLITE_OK
                              if action in {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
                              else sqlite3.SQLITE_DENY)
            source = re.sub(r"\bNVL\s*\(", "COALESCE(", sources["ptu-nvl.sql"], flags=re.I)
            adapted = re.sub(r"\bISNULL\s*\(", "COALESCE(", target, flags=re.I)
            try:
                expected = db.execute(source).fetchall()
                actual = db.execute(adapted).fetchall()
                state["synthetic_result_check"] = {
                    "source_rows": expected, "target_rows": actual,
                    "passed": collections.Counter(expected) == collections.Counter(actual),
                    "engine": "SQLite "+sqlite3.sqlite_version,
                    "rewrites": "NVL / ISNULL -> COALESCE",
                    "limitation": "NOT execution-equivalence between Informix and SQL Server"}
            finally:
                db.close()
        state["tests"].append({
            "id": "real-api-zip", "expected": "Valid translated SQL included; malformed SQL not published",
            "actual": list(sqls),
            "passed": any("ptu-nvl" in n for n in sqls) and not any("ptu-malformed" in n for n in sqls)})
    state["history_after"] = get("/api/batch-history")
except Exception as exc:
    state["error"] = {"type": type(exc).__name__, "message": str(exc)[:1800]}
finally:
    try:
        budget.set_enabled(False)
        state["final_status"] = get("/eval/status")
        state["run_usage"] = get("/eval/usage")
        state["elapsed_seconds"] = round(time.monotonic()-started, 3)
        save()
    except Exception as exc:
        state["finalization_error_type"] = type(exc).__name__
    print(json.dumps(state))
