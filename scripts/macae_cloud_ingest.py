"""Native post-provision indexer, with only its credential constructor adapted."""
import hashlib
import json
import os
import sys
from pathlib import Path

from azure.core.exceptions import ResourceExistsError
from azure.identity import ManagedIdentityCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient

credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
account = "ptumacae7d804f70st"
endpoint = "https://ptu-macae-7d804f70-srch.search.windows.net"
blob = BlobServiceClient(f"https://{account}.blob.core.windows.net/", credential=credential)
original = Path("/eval/index_datasets.py").read_text(encoding="utf-8")
needle = "credential = AzureCliCredential()"
assert original.count(needle) == 1
adapted = original.replace(needle, "credential = EVALUATION_MANAGED_IDENTITY")
result = {"modelCalls": 0, "sourceCommit": "8ac703a71f10b622bd3c82a9cc2b5dfe921c3025",
          "nativeScriptSha256": hashlib.sha256(original.encode()).hexdigest(),
          "adaptation": "Only AzureCliCredential constructor replaced by supplied runtime ManagedIdentityCredential",
          "datasets": []}
for kind in ("rfp", "contract"):
    container = "ptu-macae-" + kind
    filename = container + ".txt"
    payload = Path("/eval/data", filename).read_bytes()
    try:
        blob.get_blob_client(container, filename).upload_blob(payload, overwrite=False)
    except ResourceExistsError:
        assert blob.get_blob_client(container, filename).download_blob().readall() == payload
    index = container + "-index"
    sys.argv = ["/eval/index_datasets.py", account, container, endpoint, index]
    exec(compile(adapted, "/eval/index_datasets.py", "exec"),
         {"__name__": "__main__", "EVALUATION_MANAGED_IDENTITY": credential})
    client = SearchClient(endpoint, index, credential)
    matches = list(client.search("Canada", top=2, select=["id", "title"]))
    result["datasets"].append({"container": container, "blob": filename, "bytes": len(payload),
        "index": index, "documentCount": client.get_document_count(),
        "keyword": "Canada", "matches": [dict(m) for m in matches],
        "sha256": hashlib.sha256(payload).hexdigest()})
print("MACAE_RESULT " + json.dumps({"name": "cloud-ingestion", "data": result}), flush=True)
