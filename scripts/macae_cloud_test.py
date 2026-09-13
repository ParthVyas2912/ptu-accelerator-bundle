"""Evaluation driver for native HTTP/WebSocket routes inside the ACA replica.

No direct model client. Run through authenticated Azure exec. All prompts and
saved payloads are synthetic. Readiness is explicitly separate from workflows.
"""
import argparse
import asyncio
import ipaddress
import json
import os
import socket
import time
import uuid
from pathlib import Path

import httpx
import websockets

OUT = Path("/tmp/macae-evidence")
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://127.0.0.1:3000"
USER = "00000000-0000-0000-0000-000000000000"
HEADERS = {"x-ms-client-principal-id": USER}
TASK = (
    "This is a synthetic onboarding evaluation, not a real business transaction. "
    "Onboard Alex Example, HR analyst, starting 2026-10-01. Manager Morgan Example. "
    "Orientation 2026-10-02 09:00. Mentor Taylor Example. Benefits Standard. "
    "Background check Standard. ID card required. Salary 70000. "
    "Email alex@example.invalid. Laptop standard Windows 11. VPN Standard required. "
    "Use HR and IT onboarding workflows. Present your plan for approval before execution. "
    "Do not invent completion of any action before its tool is executed."
)


def save(name, data):
    (OUT / (name + ".json")).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("MACAE_RESULT " + json.dumps({"name": name, "data": data}), flush=True)


def probe():
    from azure.cosmos import CosmosClient
    from azure.identity import ManagedIdentityCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.storage.blob import BlobServiceClient

    result = {"modelCalls": 0, "checks": []}
    credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
    for host in [
        "ptu-macae-7d804f70-cosmos.documents.azure.com",
        "ptumacae7d804f70st.blob.core.windows.net",
        "ptu-macae-7d804f70-srch.search.windows.net",
    ]:
        try:
            ips = sorted({a[4][0] for a in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
            private = all(ipaddress.ip_address(ip).is_private for ip in ips)
            result["checks"].append({"name": "dns", "host": host, "addresses": ips, "private": private})
        except Exception as exc:
            result["checks"].append({"name": "dns", "host": host, "error": type(exc).__name__})
    def check(name, operation):
        started = time.perf_counter()
        try:
            data = operation()
            result["checks"].append({"name": name, "ok": True, "result": data,
                                     "elapsedMs": round((time.perf_counter() - started) * 1000, 2)})
        except Exception as exc:
            result["checks"].append({"name": name, "ok": False, "error": type(exc).__name__,
                                     "httpStatus": getattr(exc, "status_code", None),
                                     "detail": str(exc)[:1600]})
    def cosmos():
        client = CosmosClient(os.environ["COSMOSDB_ENDPOINT"], credential=credential)
        properties = client.get_database_client("ptu-macae").get_container_client("memory").read()
        return {"containerId": properties["id"], "partitionKey": properties["partitionKey"]}
    check("cosmos-container-metadata", cosmos)
    blobs = BlobServiceClient("https://ptumacae7d804f70st.blob.core.windows.net/", credential=credential)
    for container in ["ptu-macae-rfp", "ptu-macae-contract"]:
        check(container, lambda c=container: {"blobNames": [b.name for b in blobs.get_container_client(c).list_blobs()]})
    check("search-index-list", lambda: {"indexes": list(SearchIndexClient(
        os.environ["AZURE_AI_SEARCH_ENDPOINT"], credential=credential).list_index_names())})
    check("native-frontend-config", lambda: httpx.get(BASE + "/config", timeout=15).json())
    result["success"] = all(c.get("ok", c.get("private", False)) for c in result["checks"])
    save("cloud-readiness", result)
    if not result["success"]:
        raise SystemExit(2)


async def seed_hr():
    team = json.loads(Path("/eval/hr.json").read_text(encoding="utf-8"))
    team["name"] = "PTU MACAE Human Resources Team"
    # Keep official agent names/prompts intact within the dedicated new account.
    async with httpx.AsyncClient(timeout=150) as client:
        response = await client.post(
            BASE + "/api/v4/upload_team_config", params={"team_id": "ptu-macae-hr"},
            headers=HEADERS, files={"file": ("hr.json", json.dumps(team), "application/json")},
        )
        save("cloud-hr-seed", {"httpStatus": response.status_code, "response": response.json()})
        response.raise_for_status()
        selected = await client.post(BASE + "/api/v4/select_team", headers=HEADERS,
                                     json={"team_id": "ptu-macae-hr"})
        save("cloud-hr-selection", {"httpStatus": selected.status_code, "response": selected.json()})
        selected.raise_for_status()


async def plan():
    session = "ptu-macae-cloud-" + uuid.uuid4().hex[:8]
    events = []
    async with websockets.connect(
        BASE.replace("http", "ws") + "/api/v4/socket/" + session + "?user_id=" + USER
    ) as socket:
        async with httpx.AsyncClient(timeout=180) as client:
            started = time.perf_counter()
            response = await client.post(BASE + "/api/v4/process_request", headers=HEADERS,
                                         json={"description": TASK, "session_id": session})
            save("cloud-hr-request", {"sessionId": session, "input": TASK,
                 "httpStatus": response.status_code, "response": response.json(),
                 "elapsedMs": round((time.perf_counter() - started) * 1000, 2)})
            response.raise_for_status()
        deadline = time.monotonic() + 240
        try:
            while time.monotonic() < deadline:
                raw = await asyncio.wait_for(socket.recv(), timeout=max(1, deadline - time.monotonic()))
                event = json.loads(raw)
                events.append(event)
                kind = str(event.get("type", ""))
                print("MACAE_EVENT " + json.dumps(event), flush=True)
                if kind in ("plan_approval_request", "final_result_message", "error_message", "timeout_notification"):
                    break
        except asyncio.TimeoutError:
            events.append({"type": "evaluation_observer_timeout", "seconds": 240})
        finally:
            save("cloud-hr-events", {"sessionId": session, "events": events})


async def approve(args):
    payload = {"m_plan_id": args.mplan, "plan_id": args.plan, "approved": args.approved == "true",
               "feedback": "Synthetic evaluator action after inspecting the proposed plan."}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(BASE + "/api/v4/plan_approval", headers=HEADERS, json=payload)
        save("cloud-approval", {"submitted": payload, "httpStatus": response.status_code, "response": response.json()})


def ledger():
    from macae_cosmos_budget import CosmosBudget, DOCUMENT_ID, PARTITION
    doc = CosmosBudget().container.read_item(DOCUMENT_ID, partition_key=PARTITION)
    save("cloud-model-ledger", {k: doc[k] for k in ("id", "used", "previous_live_calls", "limit", "records")})


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["probe", "seed-hr", "plan", "approve", "ledger"])
    p.add_argument("--mplan")
    p.add_argument("--plan")
    p.add_argument("--approved", choices=["true", "false"], default="false")
    args = p.parse_args()
    if args.action == "probe":
        probe()
    elif args.action == "ledger":
        ledger()
    else:
        asyncio.run(seed_hr() if args.action == "seed-hr" else plan() if args.action == "plan" else approve(args))
