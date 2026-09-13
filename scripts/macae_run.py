"""Run unchanged native MACAE services with evaluation metering and loopback."""
import importlib.util
import os
import sys
from pathlib import Path

import uvicorn

repo = Path(os.environ["MACAE_REPO"])
state = Path(os.environ["MACAE_STATE_DIR"])
state.mkdir(parents=True, exist_ok=True)
component = sys.argv[1]
if component not in {"backend", "mcp"}:
    raise SystemExit("Expected backend or mcp")
(state / f"{component}.pid").write_text(str(os.getpid()), encoding="ascii")

if component == "backend":
    from macae_model_guard import install
    install()
    os.chdir(repo / "src/backend")
    sys.path.insert(0, str(repo / "src/backend"))
    from app import app
    # ASGI composition only: preserve the repository frontend_server.py and
    # backend routes while respecting the two-port evaluation allocation.
    frontend = Path(os.environ["MACAE_FRONTEND_DIR"])
    if (frontend / "build/index.html").exists():
        spec = importlib.util.spec_from_file_location("macae_native_frontend", frontend / "frontend_server.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        app.mount("/", module.app)
    uvicorn.run(app, host="127.0.0.1", port=8111, access_log=False)
else:
    os.chdir(repo / "src/mcp_server")
    sys.path.insert(0, str(repo / "src/mcp_server"))
    from mcp_server import app
    uvicorn.run(app, host="127.0.0.1", port=5111, access_log=False)
