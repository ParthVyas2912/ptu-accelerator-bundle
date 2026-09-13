"""Runs the native API unchanged behind an evaluation-only voice safety gate."""
import os
import uvicorn
from approved_environment import CONFIG

for key in ("AZURE_OPENAI_API_KEY", "AZURE_VOICELIVE_API_KEY", "AZURE_CLIENT_SECRET"):
    if os.getenv(key):
        raise RuntimeError("Service-key or client-secret configuration is forbidden.")
for key, value in CONFIG.items():
    if key not in ("APP_ENV", "ALLOWED_ORIGINS_STR"):
        os.environ.setdefault(key, value)
os.environ["APP_ENV"] = "prod"
os.environ["PYTHON_DOTENV_DISABLED"] = "1"
from app.main import app


class EvaluationGate:
    def __init__(self, native):
        self.native = native

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            # Realtime is not deployed and websocket billing is not metered yet.
            await send({"type": "websocket.close", "code": 1008})
            return
        await self.native(scope, receive, send)


uvicorn.run(EvaluationGate(app), host="0.0.0.0", port=8001)
