"""Fail-closed model budget persisted atomically in the app's OWN private Blob."""
from datetime import datetime, timezone
import json
import uuid
from azure.core import MatchConditions
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, ResourceNotFoundError

PRIOR = 4
CAP = 12  # Historical Blob schema; it is not the closed evaluation's current authorization.
EVALUATION_CLOSED = True
ALLOCATED_TOTAL = 10
BLOB_NAME = "evaluation/modernize-global-budget-v1.json"


def assert_evaluation_open():
    if EVALUATION_CLOSED:
        raise RuntimeError(
            f"Modernize evaluation is closed at {ALLOCATED_TOTAL}/{ALLOCATED_TOTAL}; explicit new parent budget is required. "
            "The historical ledger cap of 12 does not authorize the two attempts reallocated to MACAE.")


class DurableBudget:
    def __init__(self, blob):
        self.blob = blob

    def read(self):
        for _ in range(8):
            try:
                download = self.blob.download_blob()
                state = json.loads(download.readall())
                if state["prior_calls"] != PRIOR or state["total_cap"] != CAP:
                    raise RuntimeError("Unexpected durable budget baseline; refusing inference")
                return state, download.properties.etag
            except ResourceNotFoundError:
                state = {"prior_calls": PRIOR, "total_cap": CAP, "events": [],
                         "processing_enabled": False, "claimed_batch": None,
                         "prior_usage": {"input_tokens": 5054, "output_tokens": 1334, "cached_tokens": 0}}
                try:
                    self.blob.upload_blob(json.dumps(state), overwrite=False)
                except ResourceExistsError:
                    pass
        raise RuntimeError("Could not initialize durable budget safely")

    def mutate(self, change):
        for _ in range(12):
            state, etag = self.read()
            result = change(state)
            try:
                self.blob.upload_blob(json.dumps(state, default=str), overwrite=True, etag=etag,
                                      match_condition=MatchConditions.IfNotModified)
                return result
            except ResourceModifiedError:
                continue
        raise RuntimeError("Concurrent budget modification; refusing inference")

    def set_enabled(self, enabled, expected_total=None):
        if enabled:
            assert_evaluation_open()
        def change(state):
            total = PRIOR + len(state["events"])
            if expected_total is not None and total != expected_total:
                raise RuntimeError("Observed total changed; operator review required")
            state["processing_enabled"] = bool(enabled)
            return total
        return self.mutate(change)

    def claim_batch(self, batch_id):
        assert_evaluation_open()
        def change(state):
            if not state["processing_enabled"]:
                raise RuntimeError("Cloud evaluation has not been armed through authenticated exec")
            if state["claimed_batch"] is not None:
                raise RuntimeError("A batch has already been claimed; no automatic repeat")
            if not batch_id:
                raise RuntimeError("Missing batch ID")
            state["claimed_batch"] = batch_id
        self.mutate(change)

    def reserve(self, path):
        assert_evaluation_open()
        event = {"id": str(uuid.uuid4()), "path": path, "started": datetime.now(timezone.utc).isoformat()}
        def change(state):
            if not state["processing_enabled"]:
                raise RuntimeError("Cloud model processing is disarmed")
            total = PRIOR + len(state["events"])
            if total >= CAP:
                raise RuntimeError("Modernize total live model request cap reached (12)")
            state["events"].append(dict(event, number=total+1))
            return event["id"]
        return self.mutate(change)

    def finish(self, event_id, details):
        def change(state):
            event = next(e for e in state["events"] if e["id"] == event_id)
            event.update(details)
        self.mutate(change)

    def record(self, key, value):
        def change(state):
            if key == "current_agents" and state.get(key) and state[key] != value:
                previous = state.setdefault("previous_agent_sets", [])
                if state[key] not in previous:
                    previous.append(state[key])
            state[key] = value
        self.mutate(change)


def production_budget():
    import os
    from azure.identity import ManagedIdentityCredential
    from azure.storage.blob import BlobClient
    credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
    blob = BlobClient(
        account_url="https://stptumodernize0911pv.blob.core.windows.net",
        container_name="ptu-modernize-files", blob_name=BLOB_NAME,
        credential=credential, retry_total=0, connection_timeout=20, read_timeout=30)
    return DurableBudget(blob)
