"""Atomic, durable cross-container budget on OWN Entra Blob Storage.

ETag compare-and-swap admits at most the approved request count across all
replicas, multiprocessing workers and restarts. No secrets or prompts are stored.
"""
import json
import os
import random
import time
from azure.core import MatchConditions
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, ResourceNotFoundError, HttpResponseError
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobClient


def client():
    return BlobClient(
        "https://stptuvcontent260911.blob.core.windows.net",
        "ptu-content-configuration", "evaluation/content-call-budget.json",
        credential=ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"]),
        retry_total=2, connection_timeout=10, read_timeout=30)


def snapshot():
    stream = client().download_blob()
    return json.loads(stream.readall())


def transaction(change):
    blob = client()
    for _ in range(40):
        try:
            stream = blob.download_blob()
            etag = stream.properties.etag
            document = json.loads(stream.readall())
        except ResourceNotFoundError:
            initial = {"version": 1, "scope": "content-only", "requests": []}
            try:
                blob.upload_blob(json.dumps(initial), overwrite=False)
            except ResourceExistsError:
                pass
            continue
        if document.get("version") != 1 or document.get("scope") != "content-only":
            raise RuntimeError("CONTENT_GUARD: unrecognized durable budget; failing closed")
        result = change(document)
        try:
            blob.upload_blob(json.dumps(document), overwrite=True, etag=etag,
                             match_condition=MatchConditions.IfNotModified)
            return result
        except ResourceModifiedError:
            time.sleep(random.uniform(0.01, 0.1))
        except HttpResponseError as exc:
            if exc.status_code == 412:
                time.sleep(random.uniform(0.01, 0.1))
            else:
                raise
    raise RuntimeError("CONTENT_GUARD: durable budget contention; failing closed")


def reserve(record, cap):
    def change(document):
        rows = document["requests"]
        if record["kind"] == "model" and sum(x["kind"] == "model" for x in rows) >= cap:
            raise RuntimeError(f"CONTENT_GUARD: {cap}-request lifetime cap reached")
        if record.get("scopeKey") and any(x.get("scopeKey") == record["scopeKey"] for x in rows):
            raise RuntimeError("CONTENT_GUARD: scoped stage already attempted; no paid retry")
        row = dict(record)
        row["id"] = len(rows) + 1
        row["containerReplica"] = os.environ.get("CONTAINER_APP_REPLICA_NAME")
        row["containerRevision"] = os.environ.get("CONTAINER_APP_REVISION")
        rows.append(row)
        return row["id"]
    return transaction(change)


def finish(ticket_id, fields):
    def change(document):
        row = next(x for x in document["requests"] if x["id"] == ticket_id)
        row.update(fields)
    transaction(change)
