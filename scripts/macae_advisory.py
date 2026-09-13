"""Genuine native API/WS advisory flow; no direct model client or fake events."""
import argparse
import asyncio
import json
import os
import re
import time
import uuid
from pathlib import Path

import httpx
import websockets

from macae_cloud_test import BASE, HEADERS, OUT, USER, ledger, probe, save
from macae_cosmos_budget import CosmosBudget, DOCUMENT_ID, PARTITION

STATE = OUT / "advisory-state.json"
NAMES = {"HRComplianceReviewer", "ITReadinessReviewer"}


def current_budget():
    return CosmosBudget().container.read_item(DOCUMENT_ID, partition_key=PARTITION)


def persist_state(state):
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def terminal_data(event):
    data = event.get("data", {})
    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        return data["data"]
    return data


def specialist_outputs(events):
    streamed, final = {}, {}
    for event in events:
        data = event.get("data", {})
        if not isinstance(data, dict):
            continue
        name = data.get("agent_name", "")
        key = re.sub(r"[^a-z]", "", name.lower())
        if key not in {n.lower() for n in NAMES}:
            continue
        text = data.get("content", "")
        if event.get("type") == "agent_message_streaming":
            streamed[key] = streamed.get(key, "") + text
        elif event.get("type") == "agent_message":
            final[key] = text
    return {key: final.get(key) or streamed.get(key, "") for key in streamed.keys() | final.keys()}


def prepare():
    if os.environ.get("MACAE_LIVE_REQUESTS_ENABLED") != "false":
        raise RuntimeError("Preparation requires explicitly disabled inference")
    probe()
    save("cloud-budget-final-migration", CosmosBudget().authorize_final_pass())
    ledger()


async def start_plan():
    if STATE.exists():
        raise RuntimeError("Advisory already started in this replica; do not spend on a duplicate run")
    budget = current_budget()
    if budget["limit"] != 24 or budget["used"] != 12:
        raise RuntimeError("Expected24 ceiling and twelve unspent continuation slots")
    if os.environ.get("MACAE_LIVE_REQUESTS_ENABLED") != "true":
        raise RuntimeError("Native inference is not enabled")
    task = Path("/eval/advisory-request.txt").read_text(encoding="utf-8")
    team = json.loads(Path("/eval/advisory-team.json").read_text(encoding="utf-8"))
    state = {"sessionId": "ptu-macae-advisory-" + uuid.uuid4().hex[:8], "stage": "uploading"}
    persist_state(state)
    async with httpx.AsyncClient(timeout=180) as client:
        # No team_id query parameter: retain the native new-configuration RAI check.
        response = await client.post(
            BASE + "/api/v4/upload_team_config", headers=HEADERS,
            files={"file": ("advisory-team.json", json.dumps(team), "application/json")},
        )
        save("cloud-advisory-upload", {"httpStatus": response.status_code, "response": response.json(),
                                      "newConfigurationRaiRetained": True})
        response.raise_for_status()
        state["teamId"] = response.json()["team_id"]
        response = await client.post(BASE + "/api/v4/select_team", headers=HEADERS,
                                     json={"team_id": state["teamId"]})
        save("cloud-advisory-selection", {"httpStatus": response.status_code, "response": response.json()})
        response.raise_for_status()
        events = []
        async with websockets.connect(
            BASE.replace("http", "ws") + "/api/v4/socket/" + state["sessionId"] + "?user_id=" + USER
        ) as socket:
            started = time.perf_counter()
            response = await client.post(BASE + "/api/v4/process_request", headers=HEADERS,
                                         json={"description": task, "session_id": state["sessionId"]})
            save("cloud-advisory-request", {"httpStatus": response.status_code, "response": response.json(),
                 "input": task, "sessionId": state["sessionId"], "teamId": state["teamId"],
                 "elapsedMs": round((time.perf_counter() - started) * 1000, 2)})
            response.raise_for_status()
            state["planId"] = response.json()["plan_id"]
            deadline = time.monotonic() + 180
            try:
                while time.monotonic() < deadline:
                    event = json.loads(await asyncio.wait_for(socket.recv(), deadline - time.monotonic()))
                    events.append(event)
                    if event.get("type") == "plan_approval_request":
                        data = event["data"]
                        if not isinstance(data, dict) or not isinstance(data.get("plan"), dict):
                            raise RuntimeError("Native plan event is not structured JSON")
                        steps = data["plan"]["steps"]
                        if {s["agent"] for s in steps} != NAMES or len(steps) != 2:
                            raise RuntimeError("Plan does not match the two approved advisory specialists")
                        state["mplanId"] = data["plan"]["id"]
                        state["plan"] = data["plan"]
                        state["stage"] = "awaiting-explicit-approval"
                        break
                    if event.get("type") in ("final_result_message", "error_message", "timeout_notification"):
                        raise RuntimeError("Native flow ended before the required advisory approval")
                else:
                    raise TimeoutError("No native approval event within180seconds")
            finally:
                persist_state(state)
                save("cloud-advisory-plan", {"state": state, "events": events})
                ledger()
    if state["stage"] != "awaiting-explicit-approval":
        raise RuntimeError("No live plan ready for explicit approval")


async def approve(args):
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if (state.get("stage") != "awaiting-explicit-approval"
            or args.mplan != state["mplanId"] or args.plan != state["planId"]
            or args.approved != "true"):
        raise RuntimeError("Explicit inspected plan IDs and approved=true are required")
    events, terminal = [], None
    async with websockets.connect(
        BASE.replace("http", "ws") + "/api/v4/socket/" + state["sessionId"] + "?user_id=" + USER
    ) as socket:
        payload = {"m_plan_id": args.mplan, "plan_id": args.plan, "approved": True,
                   "feedback": "Explicit synthetic evaluator approval of the inspected two-specialist advisory plan only. No enterprise action or access approval is granted."}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(BASE + "/api/v4/plan_approval", headers=HEADERS, json=payload)
            save("cloud-advisory-approval", {"submitted": payload, "httpStatus": response.status_code,
                                           "response": response.json()})
            response.raise_for_status()
        state["stage"] = "approved-running"
        persist_state(state)
        deadline = time.monotonic() + 600
        try:
            while time.monotonic() < deadline:
                event = json.loads(await asyncio.wait_for(socket.recv(), deadline - time.monotonic()))
                events.append(event)
                if event.get("type") == "final_result_message":
                    terminal = terminal_data(event)
                    break
                if event.get("type") in ("error_message", "timeout_notification"):
                    terminal = {"status": "error", "event": event}
                    break
            else:
                raise TimeoutError("No terminal native event within600seconds")
        finally:
            outputs = specialist_outputs(events)
            content = terminal.get("content", "") if isinstance(terminal, dict) else ""
            complete = (
                isinstance(terminal, dict) and terminal.get("status") == "completed"
                and len(content.strip()) > 80 and "terminated" not in content.lower()
                and all(len(outputs.get(n.lower(), "").strip()) > 40 for n in NAMES)
            )
            state["stage"] = "terminal-completed" if complete else "terminal-unverified-or-failed"
            persist_state(state)
            save("cloud-advisory-final", {
                "state": state, "events": events, "terminal": terminal, "specialistOutputs": outputs,
                "nativeTerminalAndBothSpecialistsVerified": complete,
                "scope": "Two-specialist read-only HR/compliance and IT advisory checklist; no provisioning",
            })
            ledger()
    if not complete:
        raise RuntimeError("Native completed synthesis and both specialist responses were not verified")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "plan", "approve"])
    parser.add_argument("--mplan")
    parser.add_argument("--plan")
    parser.add_argument("--approved")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "plan":
        asyncio.run(start_plan())
    else:
        asyncio.run(approve(args))
