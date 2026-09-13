"""Foreground launcher for the four native applications; no substitute services."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from approved_environment import CONFIG

parser = argparse.ArgumentParser()
parser.add_argument("component", choices=("backend", "frontend", "scenario-backend", "scenario-frontend"))
parser.add_argument("--repo", type=Path, required=True)
parser.add_argument("--enable-approved-cloud", action="store_true")
args = parser.parse_args()
runtime = Path(os.environ["LOCALAPPDATA"]) / "ptu-chatbot"

# Native settings also read .env files. Refuse them rather than risk loading
# inherited or synced credentials from another environment.
for relative in (".env", "chat-app/.env", "chat-app/backend/.env",
                 "scenario-app/.env", "scenario-app/backend/.env"):
    if (args.repo / relative).exists():
        raise RuntimeError(f"Refusing local .env configuration: {relative}")

for name in tuple(os.environ):
    if name.startswith(("AZURE_OPENAI_", "AZURE_FOUNDRY_", "AZURE_AI_", "AZURE_SEARCH_",
                        "AZURE_VOICELIVE_", "FOUNDRY_", "COSMOS_DB_", "APPLICATIONINSIGHTS_")):
        os.environ.pop(name, None)
for name in ("AZURE_CLIENT_SECRET", "AZURE_CLIENT_CERTIFICATE_PATH", "AZURE_CLIENT_ID",
             "AZURE_TENANT_ID", "AZURE_KEY_VAULT_URL", "AZURE_TOKEN_CREDENTIALS"):
    os.environ.pop(name, None)
os.environ.update({
    "APP_ENV": "dev", "DEPLOYMENT_SCENARIO": "ecommerce",
    "ALLOWED_ORIGINS_STR": "http://127.0.0.1:5116,http://127.0.0.1:15116",
    "PYTHON_DOTENV_DISABLED": "1",
    "CHAT_API_URL": "http://127.0.0.1:8116",
    # Supported by the native recent Azure Identity package; no service keys.
    "AZURE_TOKEN_CREDENTIALS": "AzureCliCredential",
})
if args.enable_approved_cloud:
    os.environ.update(CONFIG)

backend = args.component.endswith("backend")
scenario = args.component.startswith("scenario")
if backend:
    path = args.repo / ("scenario-app" if scenario else "chat-app") / "backend"
    os.chdir(path)
    sys.path.insert(0, str(path))
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=18116 if scenario else 8116)
else:
    path = runtime / ("scenario-frontend" if scenario else "chat-frontend")
    if scenario:
        # This is the native production widget artifact, not a replacement UI.
        shutil.copyfile(runtime / "chat-frontend/dist/widget.js", path / "dist/widget.js")
        shutil.copyfile(Path(__file__).parent / "scenario-runtime-config.js", path / "dist/runtime-config.js")
    os.chdir(path)
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is not available.")
    completed = subprocess.run([
        node, str(path / "node_modules/vite/bin/vite.js"),
        "preview", "--host", "127.0.0.1",
        "--port", "15116" if scenario else "5116", "--strictPort",
    ], check=False)
    sys.exit(completed.returncode)
