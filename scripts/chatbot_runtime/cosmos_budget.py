"""Durable bounded evaluation ledger, in the existing native Cosmos container.

One fixed document/partition survives replica scale-to-zero and image revisions.
ETag conditional writes reserve attempts BEFORE model traffic. Never reset it.
"""
import os
import uuid
from azure.core import MatchConditions
from azure.cosmos.exceptions import CosmosHttpResponseError

LIMIT = 12
DOCUMENT_ID = "ptu-chatbot-eval-cb86d11"
PARTITION = "__ptu_chatbot_evaluation_budget__"
_store = None


class CosmosBudget:
    def __init__(self, container=None):
        if container is None:
            from azure.cosmos import CosmosClient
            from azure.identity import ManagedIdentityCredential
            self.client = CosmosClient(
                "https://cosmos-ccptu1feb0911.documents.azure.com:443/",
                credential=ManagedIdentityCredential(client_id=os.getenv("AZURE_CLIENT_ID")),
                logging_enable=False,
            )
            container = self.client.get_database_client("ecommerce_db").get_container_client("chat_sessions")
        self.container = container

    def snapshot(self):
        try:
            return self.container.read_item(item=DOCUMENT_ID, partition_key=PARTITION)
        except CosmosHttpResponseError as exc:
            if exc.status_code != 404:
                raise
            try:
                return self.container.create_item({
                    "id": DOCUMENT_ID, "user_id": PARTITION,
                    "type": "bounded_evaluation_usage", "limit": LIMIT, "requests": [],
                })
            except CosmosHttpResponseError as conflict:
                if conflict.status_code != 409:
                    raise
                return self.container.read_item(item=DOCUMENT_ID, partition_key=PARTITION)

    def mutate(self, operation):
        for _ in range(8):
            doc = self.snapshot()
            if doc.get("closed"):
                raise RuntimeError("Chatbot allowance is closed; a new explicit operator allowance is required.")
            if doc.get("limit") != LIMIT:
                raise RuntimeError("Unexpected cloud budget limit; refusing model traffic.")
            result = operation(doc)
            try:
                self.container.replace_item(
                    item=DOCUMENT_ID, body=doc, etag=doc["_etag"],
                    match_condition=MatchConditions.IfNotModified,
                )
                return result
            except CosmosHttpResponseError as exc:
                if exc.status_code not in (409, 412):
                    raise
        raise RuntimeError("Cloud budget contention; no model request was authorized.")

    def reserve(self, metadata):
        request_id = str(uuid.uuid4())
        def reserve(doc):
            used = sum(row["units"] for row in doc["requests"])
            if used + metadata["units"] > LIMIT:
                raise RuntimeError(f"Chatbot request budget exhausted: {used}/{LIMIT} conservative units already used.")
            doc["requests"].append({"id": request_id, **metadata})
            return request_id
        return self.mutate(reserve)

    def finish(self, request_id, fields):
        def finish(doc):
            for row in doc["requests"]:
                if row["id"] == request_id:
                    row.update(fields)
                    return
            raise RuntimeError("Missing reserved cloud request; refusing to rewrite budget history.")
        self.mutate(finish)


def store():
    global _store
    if _store is None:
        _store = CosmosBudget()
    return _store
