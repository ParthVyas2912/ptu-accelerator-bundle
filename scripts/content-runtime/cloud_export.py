"""Read only synthetic results and request metadata through authenticated exec."""
import json
import os
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobClient
from azure.core.exceptions import ResourceNotFoundError

result = {}
credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
for name in ("content-call-budget.json", "functional-results.json"):
    blob = BlobClient("https://stptuvcontent260911.blob.core.windows.net",
                      "ptu-content-configuration", "evaluation/" + name,
                      credential=credential)
    try:
        result[name] = json.loads(blob.download_blob().readall())
    except ResourceNotFoundError:
        result[name] = None
print("CONTENT_EVIDENCE_JSON=" + json.dumps(result), flush=True)
