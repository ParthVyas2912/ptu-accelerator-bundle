"""Baked diagnostic for authenticated container exec; prints no credential values."""
import json
import os
import socket
from azure.identity import ManagedIdentityCredential
from azure.appconfiguration import AzureAppConfigurationClient
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueServiceClient
from cloud_entry import mongo_connection
import pymongo
import certifi

result = {"service": os.environ["CONTENT_SERVICE"], "dns": {}, "checks": {}}
hosts = ["stptuvcontent260911.blob.core.windows.net",
         "stptuvcontent260911.queue.core.windows.net",
         "cosmos-ptuv-content-260911.mongo.cosmos.azure.com",
         "aif-ptuv-content-260911.cognitiveservices.azure.com",
         "aif-ptuv-content-260911.openai.azure.com"]
for host in hosts:
    try:
        result["dns"][host] = sorted({x[4][0] for x in socket.getaddrinfo(host, None)})
    except Exception as exc:
        result["dns"][host] = type(exc).__name__
credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
checks = {
    "blob": lambda: [x.name for x in BlobServiceClient(
        "https://stptuvcontent260911.blob.core.windows.net", credential).list_containers()],
    "queue": lambda: [x.name for x in QueueServiceClient(
        "https://stptuvcontent260911.queue.core.windows.net", credential).list_queues()],
    "appconfig": lambda: [x.key for x in AzureAppConfigurationClient(
        "https://appcs-ptuv-content-260911.azconfig.io", credential,
        credential_scopes=["https://azconfig.io/.default"]).list_configuration_settings()],
    "mongo": lambda: pymongo.MongoClient(mongo_connection(), tlsCAFile=certifi.where(),
                                         serverSelectionTimeoutMS=15000)["ptu-content-db"].command("ping")
}
for name, check in checks.items():
    try:
        result["checks"][name] = {"status": "passed", "result": check()}
    except Exception as exc:
        result["checks"][name] = {"status": "failed", "type": type(exc).__name__}
print("CONTENT_PROBE_JSON=" + json.dumps(result), flush=True)
