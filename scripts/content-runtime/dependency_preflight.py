"""Read-only native dependencies/auth preflight, with no model invocation."""
import json
from pathlib import Path
from azure.identity import AzureCliCredential
from azure.appconfiguration import AzureAppConfigurationClient
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueServiceClient
import requests

credential = AzureCliCredential()
results = {}
checks = {
    "appconfig": lambda: [x.key for x in AzureAppConfigurationClient(
        "https://appcs-ptuv-content-260911.azconfig.io", credential,
        credential_scopes=["https://azconfig.io/.default"]).list_configuration_settings()],
    "blobContainers": lambda: [x.name for x in BlobServiceClient(
        "https://stptuvcontent260911.blob.core.windows.net", credential).list_containers()],
    "queues": lambda: [x.name for x in QueueServiceClient(
        "https://stptuvcontent260911.queue.core.windows.net", credential).list_queues()],
}
for name, check in checks.items():
    try:
        value = check()
        if name == "appconfig":
            assert "APP_COSMOS_CONNSTR" not in value
        results[name] = {"status": "passed", "names": value}
    except Exception as exc:
        results[name] = {"status": "failed", "error": type(exc).__name__ + ": " + str(exc)[:1200]}
    print(name, results[name]["status"], flush=True)
try:
    token = credential.get_token("https://cognitiveservices.azure.com/.default").token
    response = requests.get(
        "https://aif-ptuv-content-260911.cognitiveservices.azure.com/"
        "contentunderstanding/analyzers/prebuilt-layout?api-version=2025-11-01",
        headers={"Authorization": "Bearer " + token}, timeout=60)
    results["cuMetadata"] = {"status": response.status_code, "body": response.json(),
                             "billableAnalysis": False}
except Exception as exc:
    results["cuMetadata"] = {"status": "failed", "error": type(exc).__name__ + ": " + str(exc)[:1200],
                             "billableAnalysis": False}
print("CU prebuilt-layout metadata", results["cuMetadata"]["status"], flush=True)
path = Path(__file__).resolve().parents[2] / "evidence/content/native-dependency-preflight.json"
path.write_text(json.dumps(results, indent=2), encoding="utf-8")
