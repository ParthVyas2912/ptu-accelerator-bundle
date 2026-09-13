"""Independent native parser and SQLite result check; no model calls or credentials."""
import collections
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import time

B = Path(__file__).resolve().parents[1]
R = B.parent.parent / "repo" / "Modernize-your-code-solution-accelerator"
OUT = B / "evidence" / "modernize"
PARSER = R / "src/backend/sql_agents/tools/win-x64/tsqlParser.exe"


def parse(sql):
    start = time.monotonic()
    p = subprocess.run([str(PARSER), "--string", sql], capture_output=True, text=True, timeout=60)
    return {"exit_code": p.returncode, "errors": json.loads(p.stdout),
            "elapsed_seconds": round(time.monotonic()-start, 4)}


results = {
    "scope": "independent SQL validation, not application deployment",
    "engine": {"name": "SQLite", "version": sqlite3.sqlite_version,
               "informix_engine_available": False, "sql_server_engine_available": False},
    "parser_tests": [], "equivalence_tests": [],
}
for name, sql, expected_valid in [
    ("native-valid", "SELECT TOP 5 * FROM employees;", True),
    ("native-malformed", "SELEC FROM WHERE;", False),
    ("native-placeholder", "No migration", False),
    ("native-demographic-schema", "SELECT customer_id, gender, age_group FROM customers WHERE active=1;", True),
]:
    actual = parse(sql)
    results["parser_tests"].append({"id": name, "sql": sql, "expected_valid": expected_valid,
                                    "actual": actual,
                                    "passed": (actual["errors"] == []) == expected_valid})

for path in sorted((R / "data/informix/simple").glob("*_tsql.sql")):
    sql = path.read_text(encoding="utf-8-sig")
    results["parser_tests"].append({
        "id": "repo-reference-"+path.name, "expected": "Repository target reference parses",
        "actual": parse(sql), "not_ai_generated_this_run": True,
    })

component_path = OUT / "component-evaluation.json"
cases = []
if component_path.exists():
    cases.extend(json.loads(component_path.read_text(encoding="utf-8")).get("tests", []))
protocol_path = OUT / "migrator-protocol.json"
if protocol_path.exists():
    for case in json.loads(protocol_path.read_text(encoding="utf-8")).get("tests", []):
        for index, candidate in enumerate(case.get("response", {}).get("candidates", [])):
            parsed = parse(candidate["candidate_query"])
            results["parser_tests"].append({
                "id": case["id"]+"-candidate-"+str(index+1), "actual": parsed,
                "scope": "Migrator protocol output, not full-pipeline output",
            })
            if case["id"] == "repo-nvl":
                cases.append({"id": "repo-nvl", "source": case["source"],
                              "target": candidate["candidate_query"], "candidate": index+1,
                              "scope": "Migrator protocol reproduction"})
native_path = OUT / "native-e2e.json"
if native_path.exists():
    native = json.loads(native_path.read_text(encoding="utf-8"))
    for name, target in native.get("download", {}).get("sql", {}).items():
        if not name.lower().endswith(".sql"):
            continue
        results["parser_tests"].append({
            "id": "native-download-"+name, "actual": parse(target),
            "scope": "actual original native batch workflow ZIP download",
        })
        if "ptu-nvl" in name:
            cases.append({
                "id": "repo-nvl",
                "source": (B/"test-data/modernize/ptu-nvl.sql").read_text(encoding="utf-8"),
                "target": target,
                "scope": "actual original native batch workflow ZIP download",
            })
if cases:
    for case in cases:
        if case["id"] != "repo-nvl" or not case.get("target"):
            continue
        target = case["target"]
        # Deliberately a limited cross-engine check. Record every compatibility rewrite.
        source = re.sub(r"\bNVL\s*\(", "COALESCE(", case["source"], flags=re.I)
        sqlite_target = re.sub(r"\bISNULL\s*\(", "COALESCE(", target, flags=re.I)
        db = sqlite3.connect(":memory:")
        db.executescript(
            "CREATE TABLE orders(order_id INTEGER, customer_id INTEGER);"
            "CREATE TABLE orders_backup(customer_id INTEGER, order_total REAL);"
            "INSERT INTO orders VALUES(1,10),(2,10),(3,20),(4,30),(5,NULL);"
            "INSERT INTO orders_backup VALUES(10,2.5),(10,7.5),(20,NULL),(40,99);"
        )
        try:
            source_rows = db.execute(source).fetchall()
            target_rows = db.execute(sqlite_target).fetchall()
            equal = collections.Counter(source_rows) == collections.Counter(target_rows)
            results["equivalence_tests"].append({
                "id": "repo-nvl-synthetic", "candidate": case.get("candidate"),
                "scope": case.get("scope", "original SDK pipeline"),
                "expected": "Same multiset across duplicate/null/no-match cases",
                "source_rows": source_rows, "target_rows": target_rows, "passed": equal,
                "source_rewrite": "NVL -> COALESCE", "target_rewrite": "ISNULL -> COALESCE if present",
                "limitation": "SQLite comparison with documented function rewrite is NOT Informix/SQL Server equivalence.",
            })
        except Exception as exc:
            results["equivalence_tests"].append({"id": "repo-nvl-synthetic", "passed": False,
                                                  "error": str(exc), "target": target})
        finally:
            db.close()

if not results["equivalence_tests"]:
    results["equivalence_tests"].append({
        "id": "source-target-real-translation",
        "status": "not_run_no_generated_target_available",
        "limitation": "No LLM semantic assurance is counted as result equivalence.",
    })
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "sql-validation.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
