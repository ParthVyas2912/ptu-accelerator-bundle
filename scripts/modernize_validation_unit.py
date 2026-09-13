"""Execute the repository's exact validation function in an isolated unit harness."""
import ast
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

B = Path(__file__).resolve().parents[1]
R = B.parent.parent / "repo" / "Modernize-your-code-solution-accelerator"
path = R / "src/backend/sql_agents/convert_script.py"
source = path.read_text(encoding="utf-8-sig")
tree = ast.parse(source)
node = next(x for x in tree.body if isinstance(x, ast.AsyncFunctionDef) and x.name == "validate_migration")
module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), node],
                    type_ignores=[])
ast.fix_missing_locations(module)
events = []
scope = {
    "send_status_update": lambda status: events.append(vars(status)),
    "FileProcessUpdate": lambda *args, **kw: SimpleNamespace(**kw),
    "ProcessStatus": SimpleNamespace(COMPLETED="completed"),
    "FileResult": SimpleNamespace(ERROR="error", SUCCESS="success"),
    "AgentType": SimpleNamespace(SEMANTIC_VERIFIER="semantic_verifier", ALL="agents"),
    "AuthorRole": SimpleNamespace(ASSISTANT="assistant"),
    "LogType": SimpleNamespace(ERROR="error", SUCCESS="success"),
    "logger": MagicMock(),
}
exec(compile(module, str(path), "exec"), scope)


class Recorder:
    async def create_file_log(self, *args, **kwargs):
        self.last_log = {"args": args, "kwargs": kwargs}


results = {"scope": "isolated original validation-function unit test, not E2E",
           "source": str(path.relative_to(R)), "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
           "tests": []}
for candidate, expected in [("", False), ("SELECT 1;", True), ("No migration", False)]:
    service = Recorder()
    result = asyncio.run(scope["validate_migration"](
        candidate, None, SimpleNamespace(batch_id="synthetic-batch", file_id="synthetic-file"), service))
    results["tests"].append({"candidate": candidate, "expected_accept": expected,
                             "actual_accept": result, "passed": result == expected,
                             "last_log": service.last_log})
filename = "validation-unit-after-fix.json" if "--after-fix" in sys.argv else "validation-unit.json"
(B/"evidence/modernize"/filename).write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
