"""Fail-closed scope around native queue dispatch and inference; never replace outputs."""
import base64
import contextvars
import functools
import hashlib
import json
import os
import time
from pathlib import Path

from azure.core import MatchConditions
from azure.core.exceptions import ResourceModifiedError
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobClient

RUN = "missing-police-native"
CONTROL = "evaluation/isolated-missing-police-control.json"
CURRENT = contextvars.ContextVar("content_allowed_work", default=None)
QUEUES = {"claim-process-queue": "claim", **{
    f"content-pipeline-{stage}-queue": stage for stage in ("extract", "map", "evaluate", "save")}}
AGENTS = {"RAI Agent": "rai", "Claim Summarization Agent": "summary", "GAP Analysis Agent": "gaps"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(name=CONTROL, container="ptu-content-configuration"):
    return BlobClient("https://stptuvcontent260911.blob.core.windows.net", container, name,
                      credential=ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"]))


def read_control():
    value = json.loads(blob().download_blob().readall())
    if value.get("run") != RUN or value.get("approvedTotal") != 17 or len(value.get("expected", {})) != 3:
        raise RuntimeError("CONTENT_SCOPE: unrecognized run manifest")
    return value


def change_control(change):
    client = blob()
    for _ in range(20):
        stream = client.download_blob()
        value = json.loads(stream.readall())
        if value.get("run") != RUN:
            raise RuntimeError("CONTENT_SCOPE: refusing other control state")
        result = change(value)
        try:
            client.upload_blob(json.dumps(value), overwrite=True, etag=stream.properties.etag,
                               match_condition=MatchConditions.IfNotModified)
            return result
        except ResourceModifiedError:
            time.sleep(0.05)
    raise RuntimeError("CONTENT_SCOPE: control-state contention")


def event(kind, **fields):
    record = {"kind": kind, "utc": time.time(), "service": os.environ.get("CONTENT_SERVICE"), **fields}
    print("CONTENT_SCOPE_EVENT=" + json.dumps(record), flush=True)
    change_control(lambda state: state.setdefault("events", []).append(record))


def fail(message):
    def update(state):
        state["mode"] = "disarmed"
        state.setdefault("failures", []).append({"utc": time.time(), "message": message})
    change_control(update)
    raise RuntimeError("CONTENT_SCOPE: " + message)


def decode(content):
    text = content.decode() if isinstance(content, bytes) else content
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = json.loads(base64.b64decode(text, validate=True))
    if not isinstance(payload, dict):
        raise ValueError("Queue payload is not an object")
    return payload


def classify(queue_name, payload, state):
    if queue_name not in QUEUES:
        raise RuntimeError("CONTENT_SCOPE: unapproved receive queue")
    if queue_name == "claim-process-queue":
        if payload.get("claim_process_id") != state["claimId"]:
            return None
        return {"claimId": state["claimId"], "stage": "claim"}
    status = payload.get("pipeline_status", {})
    if status.get("metadata_id") != state["claimId"]:
        return None
    pid = payload.get("process_id")
    files = payload.get("files", [])
    sources = [item for item in files if item.get("artifact_type") == "source_content"]
    if not pid or status.get("process_id") != pid or len(sources) != 1 or any(
            item.get("process_id") != pid for item in files):
        raise RuntimeError("CONTENT_SCOPE: inconsistent pipeline identity")
    name = sources[0].get("name")
    expected = state["expected"].get(name)
    registered = state.get("documents", {}).get(name)
    if not expected or not registered or registered["processId"] != pid or status.get("schema_id") != expected["schemaId"]:
        raise RuntimeError("CONTENT_SCOPE: document is not explicitly bound")
    return {"claimId": state["claimId"], "processId": pid, "fileName": name, "stage": QUEUES[queue_name]}


def receive_scoped(original, client, *args, **kwargs):
    state = read_control()
    if state["mode"] != "armed":
        raise RuntimeError("CONTENT_SCOPE: queue consumers disarmed")
    for message in original(client, *args, **kwargs):
        state = read_control()
        if state["mode"] != "armed":
            client.update_message(message, visibility_timeout=3600)
            event("deferred-after-disarm", queue=client.queue_name, messageId=message.id)
            return
        try:
            scope = classify(client.queue_name, decode(message.content), state)
        except (ValueError, TypeError, KeyError, RuntimeError) as exc:
            client.update_message(message, visibility_timeout=3600)
            event("deferred-invalid", queue=client.queue_name, messageId=message.id, reason=str(exc))
            fail("Invalid or inconsistent queue payload; no dispatch")
        if scope is None:
            client.update_message(message, visibility_timeout=3600)
            event("deferred-unrelated", queue=client.queue_name, messageId=message.id,
                  payloadSha256=sha(message.content.encode()), seconds=3600)
            continue
        event("admitted-native-message", queue=client.queue_name, messageId=message.id, **scope)
        token = CURRENT.set(scope)
        try:
            yield message
        finally:
            CURRENT.reset(token)


def register_send(content):
    state = read_control()
    context = CURRENT.get()
    payload = decode(content)
    if state["mode"] != "armed" or not context or context["claimId"] != state["claimId"]:
        raise RuntimeError("CONTENT_SCOPE: no approved sending claim")
    status = payload["pipeline_status"]
    files = payload["files"]
    if status["metadata_id"] != state["claimId"] or len(files) != 1:
        raise RuntimeError("CONTENT_SCOPE: wrong submission metadata")
    name, pid = files[0]["name"], payload["process_id"]
    expected = state["expected"].get(name)
    if not expected or status["schema_id"] != expected["schemaId"] or status["process_id"] != pid:
        raise RuntimeError("CONTENT_SCOPE: wrong submitted document/schema")
    actual = blob(f"{pid}/{name}", "ptu-content-processes").download_blob().readall()
    if sha(actual) != expected["sha256"]:
        raise RuntimeError("CONTENT_SCOPE: submitted input hash mismatch")
    def bind(value):
        docs = value.setdefault("documents", {})
        if name in docs or any(item["processId"] == pid for item in docs.values()):
            raise RuntimeError("CONTENT_SCOPE: duplicate document submission")
        docs[name] = {"processId": pid, "sha256": sha(actual), "schemaId": expected["schemaId"]}
    change_control(bind)
    event("bound-native-document", claimId=state["claimId"], processId=pid, fileName=name, inputSha256=sha(actual))


def inference_scope(kind):
    state = read_control()
    context = CURRENT.get()
    if state["mode"] != "armed" or not context or context["claimId"] != state["claimId"]:
        raise RuntimeError("CONTENT_SCOPE: inference without an armed allowed claim")
    stage = context["stage"]
    if kind == "model":
        if stage not in ("map", "rai", "summary", "gaps"):
            raise RuntimeError("CONTENT_SCOPE: model outside a permitted native stage")
        key = f"{RUN}/{context['claimId']}/{stage}/{context.get('processId', 'claim')}"
    else:
        if stage != "extract":
            raise RuntimeError("CONTENT_SCOPE: CU outside allowed document extraction")
        key = f"{RUN}/{context['claimId']}/cu/{context['processId']}" if kind == "cu-analyze" else None
    if "processId" in context:
        document = state["documents"].get(context["fileName"])
        if not document or document["processId"] != context["processId"]:
            raise RuntimeError("CONTENT_SCOPE: model document binding changed")
    return {"scopeRun": RUN, **context, **({"scopeKey": key} if key else {})}


def assert_completed_documents():
    import certifi
    import pymongo
    state = read_control()
    if set(state["documents"]) != set(state["expected"]):
        fail("Tail blocked: not all three document IDs bound")
    with pymongo.MongoClient(os.environ["APP_COSMOS_CONNSTR"], tlsCAFile=certifi.where(),
                             serverSelectionTimeoutMS=15000) as client:
        for name, document in state["documents"].items():
            record = client["ptu-content-db"]["ptu-content-processes"].find_one({"process_id": document["processId"]})
            if record is None or record.get("status") != "Completed":
                fail("Tail blocked: document not Completed: " + name)


def install():
    from azure.storage.queue import QueueClient
    if getattr(QueueClient, "_content_scope_installed", False):
        return
    original_receive = QueueClient.receive_messages
    original_send = QueueClient.send_message
    original_delete = QueueClient.delete_message

    def receive(self, *args, **kwargs):
        return receive_scoped(original_receive, self, *args, **kwargs)

    def send(self, content, *args, **kwargs):
        if self.queue_name == "content-pipeline-extract-queue":
            register_send(content)
        elif self.queue_name in QUEUES:
            state = read_control()
            if classify(self.queue_name, decode(content), state) is None:
                raise RuntimeError("CONTENT_SCOPE: refusing unrelated stage enqueue")
        else:
            raise RuntimeError("CONTENT_SCOPE: no dead-letter or unrelated queue writes")
        return original_send(self, content, *args, **kwargs)

    def delete(self, *args, **kwargs):
        if not CURRENT.get():
            raise RuntimeError("CONTENT_SCOPE: no deletion outside admitted native work")
        return original_delete(self, *args, **kwargs)

    QueueClient.receive_messages = receive
    QueueClient.send_message = send
    QueueClient.delete_message = delete
    QueueClient._content_scope_installed = True
    if os.environ["CONTENT_SERVICE"] == "workflow":
        import agent_framework
        original_run = agent_framework.Agent.run

        @functools.wraps(original_run)
        async def scoped_agent(self, *args, **kwargs):
            stage = AGENTS.get(self.name)
            context = CURRENT.get()
            if not stage or not context or context.get("stage") != "claim":
                raise RuntimeError("CONTENT_SCOPE: unexpected native agent or caller")
            assert_completed_documents()
            token = CURRENT.set({**context, "stage": stage})
            try:
                response = await original_run(self, *args, **kwargs)
                blob(f"evaluation/{RUN}-{stage}.json").upload_blob(
                    json.dumps({"claimId": context["claimId"], "stage": stage, "text": response.text}),
                    overwrite=False)
                return response
            finally:
                CURRENT.reset(token)
        agent_framework.Agent.run = scoped_agent
