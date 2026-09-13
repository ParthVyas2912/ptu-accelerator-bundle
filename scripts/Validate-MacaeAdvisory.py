"""Validate the exact native pure parser and advisory budget offline."""
import ast
import asyncio
import hashlib
import json
import logging
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

B = Path(__file__).resolve().parent.parent
repo = Path(r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\Multi-Agent-Custom-Automation-Engine-Solution-Accelerator")
sys.path.insert(0, str(repo / "src" / "backend"))
from common.models.messages import StartingTask, TeamAgent, TeamConfiguration

source = (repo / "src" / "backend" / "services" / "team_service.py").read_text(encoding="utf-8-sig")
tree = ast.parse(source)
original_class = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "TeamService")
methods = {"validate_and_parse_team_config", "_validate_and_parse_agent", "_validate_and_parse_task"}
original_class.body = [n for n in original_class.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in methods]
namespace = dict(globals(), DatabaseBase=object)
exec(compile(ast.fix_missing_locations(ast.Module(body=[original_class], type_ignores=[])),
             "native-team-parser-offline", "exec"), namespace)
team_file = B / "test-data" / "macae" / "advisory-team.json"
request_file = team_file.with_name("advisory-request.txt")
service = namespace["TeamService"]()
service.logger = logging.getLogger("macae.offline.native-parser")
config = asyncio.run(service.validate_and_parse_team_config(
    json.loads(team_file.read_text()), "00000000-0000-0000-0000-000000000000"))
names = {a.name for a in config.agents}
assert names == {"HRComplianceReviewer", "ITReadinessReviewer"}
assert all(a.deployment_name == "gpt-5.4-mini" for a in config.agents)
assert all(not any((a.use_toolbox, a.use_file_search, a.use_knowledge_base, a.user_responses, a.coding_tools)) for a in config.agents)
assert len(request_file.read_text()) < 5000
for required in ("2026-10-01", "2026-10-02", "NOT yet recorded", "MFA enrollment is pending"):
    assert required in request_file.read_text()
driver_tree = ast.parse((B / "scripts" / "macae_advisory.py").read_text())
functions = [n for n in driver_tree.body if isinstance(n, ast.FunctionDef) and n.name in {"specialist_outputs", "terminal_data"}]
scope = {"re": re, "NAMES": names}
exec(compile(ast.Module(body=functions, type_ignores=[]), "advisory-parser-offline", "exec"), scope)
assert scope["terminal_data"]({"data": {"data": {"status": "completed"}}}) == {"status": "completed"}
assert scope["specialist_outputs"]([
    {"type": "agent_message_streaming", "data": {"agent_name": "HR Compliance Reviewer", "content": "real text"}},
    {"type": "agent_message", "data": {"agent_name": "HR Compliance Reviewer", "content": ""}},
]) == {"hrcompliancereviewer": "real text"}
breakdown = {"new_team_rai": 1, "request_rai": 1, "scope": 1, "facts": 1, "plan": 1,
             "routing": 2, "specialist_responses": 2, "completion_check": 1, "final_synthesis": 1}
assert sum(breakdown.values()) == 11
result = {
    "nativeParserPassed": True, "specialists": sorted(names), "allToolAndClarificationFlagsFalse": True,
    "newConfigRaiRetained": True, "expectedMinimumNewCalls": 11, "available": 12, "retryBuffer": 1,
    "threeSpecialistsIncludingNewConfigRaiMinimum": 13, "breakdown": breakdown,
    "modelCalls": 0, "driverParserChecksPassed": 2,
    "teamSha256": hashlib.sha256(team_file.read_bytes()).hexdigest(),
    "requestSha256": hashlib.sha256(request_file.read_bytes()).hexdigest(),
    "scope": "Two-specialist read-only HR/compliance and IT advisory review; no enterprise actions",
}
(B / "evidence" / "macae" / "advisory-offline.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result))
