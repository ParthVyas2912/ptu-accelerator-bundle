"""Serve the original native API with durable data bindings and no inference."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import os

from src.api.ckm_serving_guard import STATE, ReadOnlyGate, install_transport_guard

if os.environ.get("CKM_INFERENCE_ARMED") != "false" or os.environ.get("CKM_READ_ONLY") != "true":
    raise RuntimeError("CKM requires explicit immutable read-only/inference-disarmed configuration")
install_transport_guard()

from src.api.config import get_settings
settings = get_settings()
required = {
    "azure_sql_server": "sql-ptu-conversation-7d804f70.database.windows.net",
    "azure_sql_database": "ptu-conversation",
    "azure_storage_account": "stptuconv7d804f70",
    "azure_storage_container": "ptu-conversation-documents",
    "azure_search_endpoint": "https://srch-ptu-conversation-7d804f70.search.windows.net",
    "azure_search_index_name": "ptu-conversation-index",
    "azure_openai_endpoint": "https://aif-ptu-conversation-7d804f70.openai.azure.com",
    "azure_client_id": "1b458b7e-1768-45a9-b676-9a3245a4dfbe",
}
if any(getattr(settings, name) != value for name, value in required.items()):
    raise RuntimeError("CKM durable native data/MI configuration does not match its owned resources")
if settings.azure_ai_agent_endpoint or settings.azure_foundry_endpoint or settings.azure_content_understanding_endpoint:
    raise RuntimeError("Hosted agents and CU must remain unset in the closed-budget serving deployment")
if settings.enable_auto_pipeline_selection or settings.enable_external_data_sources or settings.admin_api_key:
    raise RuntimeError("CKM automatic/external processing or secret authentication must not be enabled")

from src.api.storage.sql_service import sql_service
original_connection = sql_service._get_connection


def observed_connection():
    connection = original_connection()
    STATE["last_sql_access_at"] = datetime.now(timezone.utc).isoformat()
    return connection


sql_service._get_connection = observed_connection
from src.api.main import app
from src.api.modules.pipelines.engine import pipeline_engine
from src.api.modules.pipelines.models import AutoProcessingConfig
pipeline_engine.set_auto_config(AutoProcessingConfig(enabled=False, auto_select=False))


@asynccontextmanager
async def read_only_lifespan(application):
    # Original lifespan only starts/stops queue workers; no queue is needed for reads.
    logging.getLogger("ckm.serving").warning(
        "CKM native serving: durable private data bindings; inference9/9 closed; queue/automatic processing disabled"
    )
    yield


app.router.lifespan_context = read_only_lifespan
app.add_middleware(ReadOnlyGate)
