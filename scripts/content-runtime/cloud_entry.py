"""Container adapter around the real upstream entrypoints; no fake service data."""
import os
import signal
import subprocess
import sys
from urllib.parse import urlsplit
import requests
from azure.identity import ManagedIdentityCredential
from content_guard import redact

COSMOS_ID = (
    "/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/"
    "rg-ptu-content-demo/providers/Microsoft.DocumentDB/databaseAccounts/"
    "cosmos-ptuv-content-260911")


def mongo_connection():
    identity = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
    token = identity.get_token("https://management.azure.com/.default").token
    # Azure's documented read action uses POST, but does not modify the account.
    response = requests.post(
        "https://management.azure.com" + COSMOS_ID +
        "/listConnectionStrings?api-version=2025-04-15",
        headers={"Authorization": "Bearer " + token}, json={}, timeout=45)
    if response.status_code != 200:
        raise RuntimeError(f"Runtime Mongo connection read returned HTTP{response.status_code}; body suppressed")
    value = response.json()["connectionStrings"][0]["connectionString"]
    if urlsplit(value).hostname != "cosmos-ptuv-content-260911.mongo.cosmos.azure.com":
        raise RuntimeError("Unapproved Mongo endpoint; refusing startup")
    return value


def main():
    if os.environ.get("CONTENT_NATIVE_GUARD") != "1" or os.environ.get("CONTENT_BUDGET_BACKEND") != "blob":
        raise RuntimeError("Mandatory durable cloud request guard not configured")
    os.environ["APP_COSMOS_CONNSTR"] = mongo_connection()
    commands = {
        "api": ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app",
                "--host", "0.0.0.0", "--port", "80", "--workers", "1", "--no-access-log"],
        "processor": ["/app/.venv/bin/python", "/app/src/main.py"],
        "workflow": ["/app/.venv/bin/python", "/app/src/main_service.py"],
    }
    service = os.environ["CONTENT_SERVICE"]
    command = commands[service]
    proc = subprocess.Popen(command, cwd="/app", stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, errors="replace")
    def terminate(signum, frame):
        proc.terminate()
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    for line in iter(proc.stdout.readline, ""):
        print(redact(line.rstrip()), flush=True)
    return proc.wait()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("CONTENT_CLOUD_STARTUP_ERROR: " + redact(str(exc)), flush=True)
        sys.exit(1)
