"""Durable evaluation ledger in the already-approved Cosmos memory container.

No model client, prompts or credentials. Missing ledger, CAS exhaustion and any
data-path/auth failure deny inference. The ledger is never reset automatically.
"""
import os
import hashlib
import json

from azure.core import MatchConditions
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.identity import ManagedIdentityCredential

DOCUMENT_ID = "__ptu_macae_model_budget_v1"
PARTITION = "__ptu_macae_evaluation__"
LIMIT = 24


class CosmosBudget:
    def __init__(self, container=None):
        self._container = container

    @property
    def container(self):
        if self._container is None:
            credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
            client = CosmosClient(os.environ["COSMOSDB_ENDPOINT"], credential=credential)
            self._container = client.get_database_client(
                os.environ["COSMOSDB_DATABASE"]
            ).get_container_client(os.environ["COSMOSDB_CONTAINER"])
        return self._container

    def initialize_once(self, previous_live_calls):
        if type(previous_live_calls) is not int or not 0 <= previous_live_calls <= LIMIT:
            raise ValueError(f"Explicit verified previous total in [0,{LIMIT}] is required")
        # create_item, never upsert: an existing ledger cannot be reset here.
        return self.container.create_item({
            "id": DOCUMENT_ID, "session_id": PARTITION, "limit": LIMIT,
            "used": previous_live_calls, "previous_live_calls": previous_live_calls,
            "records": {},
        })

    def authorize_second_pass(self):
        """Apply the exact parent-approved +10 once, preserving every spent slot."""
        approval = "2026-09-11T22:14:42.859-04:00"
        doc = self.container.read_item(DOCUMENT_ID, partition_key=PARTITION)
        history = doc.get("allowance_changes", [])
        if doc.get("limit") == 22 and history and history[-1].get("approval") == approval:
            if type(doc.get("used")) is not int or not 12 <= doc["used"] <= 22:
                raise RuntimeError("Invalid already-migrated ledger")
            return {"changed": False, "used": doc["used"], "limit": 22, "approval": approval}
        if (doc.get("limit") != 12 or doc.get("used") != 12
                or doc.get("previous_live_calls") != 0
                or set(doc.get("records", {})) != {str(i) for i in range(1, 13)}):
            raise RuntimeError("Expected the verified twelve-call first-pass ledger; migration refused")
        before_hash = hashlib.sha256(json.dumps(doc["records"], sort_keys=True).encode()).hexdigest()
        body = {k: v for k, v in doc.items() if not k.startswith("_")}
        body["limit"] = 22
        body["allowance_changes"] = history + [{
            "approval": approval, "from_limit": 12, "to_limit": 22,
            "used_at_change": 12, "increment": 10, "prior_records_sha256": before_hash,
        }]
        self.container.replace_item(
            DOCUMENT_ID, body, etag=doc["_etag"], match_condition=MatchConditions.IfNotModified,
        )
        saved = self.container.read_item(DOCUMENT_ID, partition_key=PARTITION)
        after_hash = hashlib.sha256(json.dumps(saved["records"], sort_keys=True).encode()).hexdigest()
        if saved["used"] != 12 or saved["limit"] != 22 or after_hash != before_hash:
            raise RuntimeError("Budget migration readback differs; inference must remain disabled")
        return {"changed": True, "used": saved["used"], "limit": saved["limit"],
                "approval": approval, "beforeRecordsSha256": before_hash,
                "afterRecordsSha256": after_hash, "priorRecordsPreserved": True}

    def authorize_final_pass(self):
        """Apply the two explicitly reclaimed attempts, without spending/resetting any."""
        approval = "2026-09-11T22:42:56.511-04:00"
        doc = self.container.read_item(DOCUMENT_ID, partition_key=PARTITION)
        history = doc.get("allowance_changes", [])
        if doc.get("limit") == LIMIT and history and history[-1].get("approval") == approval:
            if type(doc.get("used")) is not int or not 12 <= doc["used"] <= LIMIT:
                raise RuntimeError("Invalid final-pass ledger")
            return {"changed": False, "used": doc["used"], "limit": LIMIT, "approval": approval}
        if (doc.get("limit") != 22 or doc.get("used") != 12
                or doc.get("previous_live_calls") != 0
                or set(doc.get("records", {})) != {str(i) for i in range(1, 13)}
                or not history or history[-1].get("to_limit") != 22):
            raise RuntimeError("Expected approved22 ceiling with unchanged twelve used records")
        before = hashlib.sha256(json.dumps(doc["records"], sort_keys=True).encode()).hexdigest()
        body = {k: v for k, v in doc.items() if not k.startswith("_")}
        body["limit"] = LIMIT
        body["allowance_changes"] = history + [{
            "approval": approval, "from_limit": 22, "to_limit": LIMIT, "used_at_change": 12,
            "increment": 2, "reclaimed_from": "Completed/disarmed Modernize",
            "prior_records_sha256": before,
        }]
        self.container.replace_item(
            DOCUMENT_ID, body, etag=doc["_etag"], match_condition=MatchConditions.IfNotModified,
        )
        saved = self.container.read_item(DOCUMENT_ID, partition_key=PARTITION)
        after = hashlib.sha256(json.dumps(saved["records"], sort_keys=True).encode()).hexdigest()
        if saved["used"] != 12 or saved["limit"] != LIMIT or before != after:
            raise RuntimeError("Final-pass migration readback differs; keep inference disabled")
        return {"changed": True, "used": saved["used"], "limit": LIMIT, "approval": approval,
                "beforeRecordsSha256": before, "afterRecordsSha256": after,
                "priorRecordsPreserved": True}

    def _change(self, update):
        for _ in range(12):
            doc = self.container.read_item(DOCUMENT_ID, partition_key=PARTITION)
            if doc.get("limit") != LIMIT or type(doc.get("used")) is not int or not 0 <= doc["used"] <= LIMIT:
                raise RuntimeError("Unexpected evaluation ledger; refusing inference")
            etag = doc["_etag"]
            body = {k: v for k, v in doc.items() if not k.startswith("_")}
            result = update(body)
            try:
                self.container.replace_item(
                    DOCUMENT_ID, body, etag=etag,
                    match_condition=MatchConditions.IfNotModified,
                )
                return result
            except CosmosHttpResponseError as exc:
                if exc.status_code != 412:
                    raise
        raise RuntimeError("Evaluation ledger contention; inference denied")

    def reserve(self, record):
        def increment(doc):
            if doc["used"] >= LIMIT:
                raise RuntimeError(f"MACAE live inference allowance exhausted: {LIMIT} including retries")
            ident = doc["used"] + 1
            doc["used"] = ident
            record["call_number"] = ident
            doc["records"][str(ident)] = dict(record)
            return ident
        return self._change(increment)

    def persist(self, ident, record):
        def complete(doc):
            if str(ident) not in doc["records"]:
                raise RuntimeError("Missing reservation; do not invent inference evidence")
            doc["records"][str(ident)] = dict(record)
        self._change(complete)
