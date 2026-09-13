"""Run through authenticated Azure exec. Does not expose a diagnostic HTTP API."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from time import perf_counter

parser = argparse.ArgumentParser()
parser.add_argument("stage", choices=("readiness", "cosmos", "products", "policies", "agents", "usage"))
args = parser.parse_args()
root = Path("/opt/chatbot-native/infra/scripts/post-provision")
if args.stage in ("readiness", "usage"):
    from cosmos_budget import store
    if args.stage == "readiness":
        start = perf_counter()
        addresses = sorted(set(socket.gethostbyname_ex("cosmos-ccptu1feb0911.documents.azure.com")[2]))
        private = bool(addresses) and all(ipaddress.ip_address(ip) in ipaddress.ip_network("10.246.0.0/16") for ip in addresses)
        print(json.dumps({"check": "cosmos_private_dns", "addresses": addresses, "inside_approved_vnet": private}), flush=True)
        if not private:
            raise SystemExit("Private DNS not ready; refusing data/model tests.")
        from azure.cosmos import CosmosClient
        from azure.identity import ManagedIdentityCredential
        client = CosmosClient(
            "https://cosmos-ccptu1feb0911.documents.azure.com:443/",
            credential=ManagedIdentityCredential(client_id=os.getenv("AZURE_CLIENT_ID")),
            logging_enable=False,
        )
        container = client.get_database_client("ecommerce_db").get_container_client("products")
        count = list(container.query_items("SELECT VALUE COUNT(1) FROM c", enable_cross_partition_query=True))[0]
        print(json.dumps({"check": "keyless_private_cosmos_query", "product_count": count,
                          "elapsed_ms": round((perf_counter()-start)*1000, 3)}), flush=True)
    doc = store().snapshot()
    print(json.dumps({"ledger_id": doc["id"], "limit": doc["limit"],
                      "reserved_units": sum(x["units"] for x in doc["requests"]),
                      "requests": doc["requests"]}), flush=True)
else:
    python = "/opt/seedenv/bin/python"
    directory = root / "data_scripts"
    if args.stage == "cosmos":
        script = directory / "03_write_products_to_cosmos.py"
        arguments = ["--cosmosdb_account", "cosmos-ccptu1feb0911"]
    elif args.stage == "agents":
        python = sys.executable
        script = root / "agent_scripts/01_create_agents.py"
        arguments = [
            "--ai_project_endpoint", "https://aif-ccptu1feb0911.services.ai.azure.com/api/projects/proj-ccptu1feb0911",
            "--solution_name", "eval", "--gpt_model_name", "gpt-5.4-mini",
            "--ai_search_endpoint", "https://srch-ccptu1feb0911.search.windows.net",
        ]
    else:
        script = directory / ("01_create_products_search_index.py" if args.stage == "products" else "02_create_policies_search_index.py")
        arguments = [
            "--ai_search_endpoint", "https://srch-ccptu1feb0911.search.windows.net",
            "--azure_openai_endpoint", "https://aif-ccptu1feb0911.openai.azure.com/",
            "--embedding_model_name", "text-embedding-3-small",
        ]
    result = subprocess.run([python, str(script), *arguments, "--scenario", "ecommerce"], check=False)
    sys.exit(result.returncode)
