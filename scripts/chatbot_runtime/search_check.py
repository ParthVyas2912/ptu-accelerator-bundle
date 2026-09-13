"""Private DNS and keyless Search data authorization, without model traffic."""
import json
import os
import socket
from azure.identity import ManagedIdentityCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

host = "srch-ccptu1feb0911.search.windows.net"
addresses = sorted(set(socket.gethostbyname_ex(host)[2]))
print(json.dumps({"check": "search_private_dns", "addresses": addresses}), flush=True)
if not addresses or not all(ip.startswith("10.246.") for ip in addresses):
    raise SystemExit("Search DNS is not inside the approved VNet.")
credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
endpoint = f"https://{host}"
names = list(SearchIndexClient(endpoint, credential).list_index_names())
counts = {name: SearchClient(endpoint, name, credential).get_document_count() for name in names}
print(json.dumps({"check": "keyless_private_search", "document_counts": counts}), flush=True)
