"""Run original CKM persistent routes with a strict remaining model budget."""
import argparse
import base64
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import secrets
import socket
import threading
import time
import uuid

REPORT = Path("/tmp/ckm-data-pass.json")
HERE = Path(__file__).parent
AI_HOST = "aif-ptu-conversation-7d804f70.openai.azure.com"
SQL_HOST = "sql-ptu-conversation-7d804f70.database.windows.net"
SEARCH_HOST = "srch-ptu-conversation-7d804f70.search.windows.net"
BLOB_HOST = "stptuconv7d804f70.blob.core.windows.net"
INDEX = "ptu-conversation-index"
CONTAINER = "ptu-conversation-documents"
ALREADY_USED = 7
REMAINING = 5


def now():
    return datetime.now(timezone.utc).isoformat()


def save(report):
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def export(report):
    encoded = base64.b64encode(json.dumps(report).encode()).decode()
    print("CKM_DATA_RESULT_BASE64=" + encoded)


class ModelGate:
    def __init__(self, report):
        self.report = report
        self.enabled = False
        self.lock = threading.Lock()
        self.case = "ingestion"

    def install(self):
        import httpx
        import openai
        original_init = openai.AzureOpenAI.__init__
        original_send = httpx.Client.send
        gate = self

        def init(client, *args, **kwargs):
            kwargs["max_retries"] = 0
            original_init(client, *args, **kwargs)

        def send(client, request, *args, **kwargs):
            if request.url.host != AI_HOST or request.method != "POST":
                return original_send(client, request, *args, **kwargs)
            body = json.loads(request.content)
            if "/chat/completions" not in request.url.path or body.get("stream"):
                raise RuntimeError("Only bounded native chat-completion operations are enabled")
            if body.get("model") != "gpt-5.2":
                raise RuntimeError("Unexpected deployment; request not sent")
            with gate.lock:
                if not gate.enabled:
                    gate.report["blocked_before_dispatch"] += 1
                    raise RuntimeError("AI disabled during pre-enriched persistence phase")
                if len(gate.report["requests"]) >= REMAINING:
                    raise RuntimeError("Global12-request allowance exhausted; request not sent")
                entry = {
                    "sequence": ALREADY_USED + len(gate.report["requests"]) + 1,
                    "case": gate.case, "started_at": now(), "status": "dispatching",
                    "deployment": "gpt-5.2", "usage": None,
                }
                gate.report["requests"].append(entry)
                save(gate.report)
            started = time.perf_counter()
            try:
                response = original_send(client, request, *args, **kwargs)
                response.read()
                entry["http_status"] = response.status_code
                payload = response.json()
                entry["returned_model"] = payload.get("model")
                entry["usage"] = payload.get("usage")
                entry["status"] = "completed" if response.is_success else "failed"
                return response
            except Exception as exc:
                entry["status"] = "failed"
                entry["error_type"] = type(exc).__name__
                raise
            finally:
                entry["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
                save(gate.report)

        openai.AzureOpenAI.__init__ = init
        httpx.Client.send = send


def configure():
    os.environ.update({
        "APP_ENV": "development",
        "AZURE_SQL_SERVER": SQL_HOST,
        "AZURE_SQL_DATABASE": "ptu-conversation",
        "AZURE_STORAGE_ACCOUNT": "stptuconv7d804f70",
        "AZURE_STORAGE_CONTAINER": CONTAINER,
        "AZURE_SEARCH_ENDPOINT": "https://" + SEARCH_HOST,
        "AZURE_SEARCH_INDEX_NAME": INDEX,
        "AZURE_OPENAI_ENDPOINT": "https://" + AI_HOST,
        "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-5.2",
        "AZURE_AI_AGENT_ENDPOINT": "",
        "AZURE_FOUNDRY_ENDPOINT": "",
        "AZURE_CONTENT_UNDERSTANDING_ENDPOINT": "",
        "AZURE_COSMOS_ENDPOINT": "",
        "AGENT_NAME_CHAT": "",
        "AGENT_NAME_TITLE": "",
        "ENABLE_EXTERNAL_DATA_SOURCES": "false",
        "ADMIN_API_KEY": secrets.token_urlsafe(48),
    })


def record(report, case, expected, actual, passed):
    report["tests"].append({
        "id": case, "expected": expected, "actual": actual,
        "status": "passed" if passed else "failed",
    })
    save(report)
    if not passed:
        raise RuntimeError("Native verification failed: " + case)


def probe():
    configure()
    result = {"scope": "CKM private data authorization preflight", "model_requests": 0, "checked_at": now()}
    try:
        result["private_dns"] = {
            host: sorted({row[4][0] for row in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
            for host in [AI_HOST, SQL_HOST, SEARCH_HOST, BLOB_HOST]
        }
        from src.api.storage.sql_service import sql_service
        result["native_sql_schema_available"] = sql_service.available
        if not result["native_sql_schema_available"]:
            raise RuntimeError("Native SQL initialization unavailable")
        from azure.identity import ManagedIdentityCredential
        from azure.search.documents.indexes import SearchIndexClient
        from azure.storage.blob import BlobServiceClient
        credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
        SearchIndexClient("https://" + SEARCH_HOST, credential).get_service_statistics()
        result["search_service_authorized"] = True
        container = BlobServiceClient("https://" + BLOB_HOST, credential=credential).get_container_client(CONTAINER)
        result["blob_container_exists"] = container.exists()
        result["status"] = "authorized"
    except Exception as exc:
        result["status"] = "blocked"
        result["error_type"] = type(exc).__name__
        result["error_message"] = str(exc)[:1200]
    export(result)
    return 0 if result["status"] == "authorized" else 2


def run():
    with REPORT.open("x", encoding="utf-8") as handle:
        handle.write("{}\n")
    report = {
        "scope": "CKM native pre-enriched ingestion, persistence, Search and SQL dashboard",
        "started_at": now(), "requests": [], "tests": [], "blocked_before_dispatch": 0,
        "prior_model_requests": ALREADY_USED, "remaining_pass_limit": REMAINING,
        "sdk_retries": 0, "status": "running", "full_explore": False,
        "adaptations": [
            "Original routes through TestClient in a short-lived cloud process; serving API remains unconfigured.",
            "Pre-enriched JSON includes the three real previous native summaries, not new/mock summaries.",
            "AI dispatch disabled during persistence; native heuristic fallback is explicitly not model enrichment.",
            "Original Search fields/HNSW/semantic configuration retained; unused query-time vectorizer omitted to prevent hidden server-side model calls.",
            "No hosted agent, CU, embedding or cleanup operation.",
        ],
    }
    save(report)
    configure()
    gate = ModelGate(report)
    gate.install()
    api = None
    try:
        report["private_dns"] = {
            host: sorted({row[4][0] for row in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
            for host in [AI_HOST, SQL_HOST, SEARCH_HOST, BLOB_HOST]
        }
        record(report, "own-private-dns", "All four targets resolve to10.246.2.x", report["private_dns"],
               all(all(ip.startswith("10.246.2.") for ip in values) for values in report["private_dns"].values()))
        from src.api.storage.sql_service import sql_service
        if not sql_service.available:
            raise RuntimeError("Native SQL unavailable; refusing an in-memory success fallback")
        connection = sql_service._get_connection()
        cursor = connection.cursor()
        count = cursor.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        record(report, "fresh-own-database", "Zero existing documents before a one-pass run", count, count == 0)
        sid = uuid.UUID("1b458b7e-1768-45a9-b676-9a3245a4dfbe").bytes_le.hex()
        cursor.execute(f"""
            IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name=N'id-ptu-conversation')
            CREATE USER [id-ptu-conversation] WITH SID=0x{sid}, TYPE=E
        """)
        for role in ["db_datareader", "db_datawriter", "db_ddladmin"]:
            cursor.execute(f"ALTER ROLE [{role}] ADD MEMBER [id-ptu-conversation]")
        connection.commit()
        connection.close()
        report["contained_sql_identity_created"] = True

        from azure.identity import ManagedIdentityCredential
        from azure.search.documents.indexes import SearchIndexClient
        from azure.storage.blob import BlobServiceClient
        credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
        from ckm_create_search_index import create_search_index
        original_create = SearchIndexClient.create_or_update_index

        def without_remote_vectorizer(client, index, *args, **kwargs):
            index.vector_search.vectorizers = []
            for profile in index.vector_search.profiles:
                profile.vectorizer_name = None
            return original_create(client, index, *args, **kwargs)

        SearchIndexClient.create_or_update_index = without_remote_vectorizer
        try:
            schema = create_search_index("https://" + SEARCH_HOST, INDEX, "https://" + AI_HOST,
                                         "text-embedding-3-small", credential)
        finally:
            SearchIndexClient.create_or_update_index = original_create
        record(report, "native-search-schema-basic", "Native14-field vector/semantic schema, no remote vectorizer",
               {"fields": len(schema.fields), "vectorizers": len(schema.vector_search.vectorizers or [])},
               len(schema.fields) == 14 and not schema.vector_search.vectorizers)

        from fastapi.testclient import TestClient
        from src.api.main import app
        api = TestClient(app, headers={"X-Admin-Api-Key": os.environ["ADMIN_API_KEY"]})
        config = api.put("/api/pipelines/automation/config", json={"enabled": False, "auto_select": False})
        record(report, "disable-native-auto-pipeline", "Original API disabled", config.json(), config.status_code == 200 and not config.json()["enabled"])
        docs = json.loads((HERE / "ckm-support-conversations.json").read_text(encoding="utf-8"))
        prior = json.loads((HERE / "ckm-prior-summaries.json").read_text(encoding="utf-8"))
        summaries = {item["id"]: item["actual"]["summary"] for item in prior["tests"][:3]}
        for doc in docs:
            doc["summary"] = summaries[doc["id"]]
        uploaded = api.post("/api/ingestion/upload/json", files={
            "file": ("support-conversations.json", json.dumps(docs).encode(), "application/json"),
        })
        record(report, "native-json-upload", "Exactly3 accepted", uploaded.json(), uploaded.status_code == 200 and uploaded.json().get("total_loaded") == 3)
        persisted = sql_service.load_all_documents()
        record(report, "native-sql-persistence", "Three exact IDs and original summaries persisted",
               [{"id": doc["id"], "summary_present": bool(doc.get("summary"))} for doc in persisted],
               {doc["id"] for doc in persisted} == set(summaries) and all(doc.get("summary") == summaries[doc["id"]] for doc in persisted))
        from src.api.modules.ingestion.service import IngestionService
        reloaded = IngestionService()
        record(report, "native-fresh-service-reload", "Three records loaded from SQL without memory reuse",
               reloaded.get_stats().model_dump(), reloaded.get_stats().total_documents == 3)
        blob = BlobServiceClient("https://" + BLOB_HOST, credential=credential)
        for doc in docs:
            value = json.loads(blob.get_blob_client(CONTAINER, doc["id"] + ".json").download_blob().readall())
            record(report, "blob-" + doc["id"], "Original text and measured summary", {"id": value["id"], "text_matches": value["text"] == doc["text"], "summary_matches": value["summary"] == summaries[doc["id"]]},
                   value["text"] == doc["text"] and value["summary"] == summaries[doc["id"]])
        from azure.search.documents import SearchClient
        search_client = SearchClient("https://" + SEARCH_HOST, INDEX, credential)
        for attempt in range(12):
            if search_client.get_document_count() == 3:
                break
            time.sleep(5)
        connected = api.post("/api/ingestion/external/connect", json={
            "name": "Own CKM persisted index", "endpoint": "https://" + SEARCH_HOST, "index_name": INDEX,
            "text_field": "text", "title_field": "source_file", "metadata_fields": ["id", "category", "summary"],
        })
        record(report, "native-byoi-connect", "Original connector reads3 indexed records", connected.json(),
               connected.status_code == 200 and connected.json().get("doc_count") == 3)
        index_id = connected.json()["id"]
        found = api.post(f"/api/ingestion/external/{index_id}/search", params={"query": "VPN", "top_k": 5})
        hits = found.json().get("results", [])
        record(report, "native-cross-call-search-evidence", "Only calls001/002 retrieved with original IDs/text",
               hits, found.status_code == 200 and {hit["doc_id"] for hit in hits} == {docs[0]["id"], docs[1]["id"]})
        report["persistence_phase_model_requests"] = len(report["requests"])
        if report["persistence_phase_model_requests"] != 0:
            raise RuntimeError("Persistence unexpectedly consumed model requests")
        gate.enabled = True
        for case, route in [
            ("native-model-planned-sql-dashboard", "/api/insights/dashboard?refresh=true"),
            ("native-processing-insights", "/api/processing/insights?file_ids=support-conversations&refresh=true"),
        ]:
            gate.case = case
            before = len(report["requests"])
            response = api.get(route)
            actual = response.json() if response.status_code == 200 else {"http_status": response.status_code}
            passed = response.status_code == 200 and len(report["requests"]) == before + 1 and report["requests"][-1]["http_status"] == 200
            if case.endswith("dashboard"):
                passed = passed and actual.get("data_context", {}).get("total_records") == 3 and bool(actual.get("kpis"))
            record(report, case, "Original route succeeds with one measured model call; SQL dashboard has3 records and real KPIs", actual, passed)
        report["status"] = "completed_pending_manual_review"
    except Exception as exc:
        report["status"] = "stopped_after_failure"
        report["error_type"] = type(exc).__name__
        report["error_message"] = str(exc)[:1200]
    finally:
        if api is not None:
            api.close()
        report["finished_at"] = now()
        report["actual_additional_model_requests"] = len(report["requests"])
        report["cumulative_model_requests"] = ALREADY_USED + len(report["requests"])
        save(report)
    export(report)
    return 0 if report["status"] == "completed_pending_manual_review" else 2


if __name__ == "__main__":
    logging.getLogger("azure").setLevel(logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["run", "export", "probe"])
    args = parser.parse_args()
    if args.mode == "export":
        export(json.loads(REPORT.read_text(encoding="utf-8")))
    elif args.mode == "probe":
        raise SystemExit(probe())
    else:
        raise SystemExit(run())
