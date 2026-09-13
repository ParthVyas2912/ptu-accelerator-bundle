"""Zero-model administrative/readiness batch. Never creates workflow events."""
import hashlib
import os
from pathlib import Path

from macae_cloud_test import ledger, probe, save
from macae_cosmos_budget import CosmosBudget

if os.environ.get("MACAE_LIVE_REQUESTS_ENABLED") != "false":
    raise RuntimeError("Second-pass preparation requires explicitly disabled inference")

probe()
save("cloud-budget-migration", CosmosBudget().authorize_second_pass())
ledger()
save("cloud-serialization-source", {
    "path": "/app/orchestration/connection_config.py",
    "sha256": hashlib.sha256(Path("/app/orchestration/connection_config.py").read_bytes()).hexdigest(),
    "component": "Patched native ConnectionConfig; source-hash verification only, not a fabricated workflow event",
    "modelCalls": 0,
})
