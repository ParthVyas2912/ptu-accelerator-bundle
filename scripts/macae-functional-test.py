"""Small native API/WebSocket evaluation; never substitutes a model client."""
import argparse
import asyncio
import json
import os
import time
import uuid
from pathlib import Path

import httpx
import websockets

BUNDLE = Path(__file__).resolve().parent.parent
REPO = Path(json.loads((BUNDLE / "deployment-contract.json").read_text())["repoRoot"]) / "Multi-Agent-Custom-Automation-Engine-Solution-Accelerator"
OUT = BUNDLE / "evidence/macae"
BASE = "http://127.0.0.1:8111"
USER = "00000000-0000-0000-0000-000000000000"
HEADERS = {"x-ms-client-principal-id": USER}


def record(name, data):
    # All records are synthetic request/response data, never HTTP headers.
    with (OUT / (name + ".json")).open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


async def seed_hr():
    team = json.loads((REPO / "content_packs/hr_onboarding/agent_teams/hr.json").read_text(encoding="utf-8"))
    team["name"] = "PTU MACAE Human Resources Team"
    for agent in team["agents"]:
        agent["name"] = "ptu-macae-" + agent["name"]
    # Same trusted-pack upload API/explicit team_id path used by the official
    # post-provision upload_team_config.py. No untrusted upload or safety patch.
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(BASE + "/api/v4/upload_team_config",
            params={"team_id": "ptu-macae-hr"}, headers=HEADERS,
            files={"file": ("hr.json", json.dumps(team), "application/json")})
        body = response.json()
        result = {"http_status": response.status_code,
                  "response": {k: body[k] for k in ("status", "team_id", "name", "detail") if k in body}}
        record("hr-seed", result)
        print(json.dumps(result))
        response.raise_for_status()
        selected = await client.post(BASE + "/api/v4/select_team", headers=HEADERS,
                                     json={"team_id": "ptu-macae-hr"})
        result = {"http_status": selected.status_code, "response": selected.json()}
        record("hr-selection", result)
        print(json.dumps(result))
        selected.raise_for_status()


async def plan_hr():
    session = "ptu-macae-hr-" + uuid.uuid4().hex[:8]
    task = ("Please onboard synthetic employee Alex Example. Department: HR. Role: analyst. "
            "Start date: 2026-10-01. Manager: Morgan Example. Orientation: 2026-10-02 09:00. "
            "Salary: 70000. Mentor: Taylor Example. ID card: yes. Background check: Standard. "
            "Benefits: Standard. Email: alex@example.invalid. Laptop: standard issue. "
            "Operating system: Windows 11. VPN: yes, Standard. "
            "Use the HR and IT workflows and wait for my plan approval before execution.")
    events = []
    async with websockets.connect(BASE.replace("http", "ws") + "/api/v4/socket/" + session + "?user_id=" + USER) as socket:
        async def receive():
            try:
                async for raw in socket:
                    try:
                        item = json.loads(raw)
                    except ValueError:
                        item = {"text": raw}
                    events.append(item)
                    print("EVENT " + json.dumps(item), flush=True)
            finally:
                record("hr-events", events)
        reader = asyncio.create_task(receive())
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.post(BASE + "/api/v4/process_request", headers=HEADERS,
                                             json={"description": task, "session_id": session})
                result = {"session_id": session, "input": task, "http_status": response.status_code,
                          "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                          "response": response.json()}
                record("hr-process", result)
                print("HTTP " + json.dumps(result), flush=True)
            await asyncio.sleep(100)
        finally:
            reader.cancel()
            await asyncio.gather(reader, return_exceptions=True)
            record("hr-events", events)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("action", choices=["seed-hr", "plan-hr"])
    action = args.parse_args().action
    asyncio.run(seed_hr() if action == "seed-hr" else plan_hr())
