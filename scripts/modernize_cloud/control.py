"""Run via authenticated Azure exec. Never resets a budget or deletes resources."""
import argparse
import ipaddress
import json
import socket
from pathlib import Path
import requests
from budget import assert_evaluation_open, production_budget

p = argparse.ArgumentParser()
p.add_argument("action", choices=["preflight", "arm", "disarm", "snapshot"])
p.add_argument("--expected-total", type=int)
args = p.parse_args()
if args.action == "arm":
    assert_evaluation_open()
budget = production_budget()
if args.action == "arm":
    if args.expected_total is None:
        raise SystemExit("--expected-total is mandatory")
    print(json.dumps({"total": budget.set_enabled(True, args.expected_total), "armed": True}))
elif args.action == "disarm":
    print(json.dumps({"total": budget.set_enabled(False), "armed": False}))
elif args.action == "snapshot":
    print(json.dumps(budget.read()[0]))
else:
    state = {"dns": {}, "api": {}}
    for host in ["cosmos-ptu-modernize-eus20911.documents.azure.com", "stptumodernize0911pv.blob.core.windows.net"]:
        addresses = sorted({info[4][0] for info in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
        state["dns"][host] = {"addresses": addresses,
                              "all_private": all(ipaddress.ip_address(ip).is_private for ip in addresses)}
    for path in ["/health", "/eval/status", "/api/batch-history"]:
        response = requests.get("http://127.0.0.1:8000"+path, timeout=120)
        state["api"][path] = {"status": response.status_code, "body": response.json()}
    snapshot = budget.read()[0]
    state["budget"] = {key: snapshot[key] for key in
                       ["prior_calls", "total_cap", "events", "processing_enabled", "claimed_batch"]}
    budget.record("cloud_preflight", state.copy())
    print(json.dumps(state))
