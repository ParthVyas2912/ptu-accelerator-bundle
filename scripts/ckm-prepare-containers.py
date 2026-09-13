"""Export secret-free CKM container contexts; never copy an azd/.env workspace.

API uses the repository Dockerfile and exact requirements unchanged. UI reuses
the already-verified original production build and the official nginx runtime
stage, avoiding a second large npm installation. No application logic changes.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

bundle = Path(__file__).resolve().parents[1]
repo = bundle.parents[1] / "repo/Conversation-Knowledge-Mining-Solution-Accelerator"
local = Path(os.environ["LOCALAPPDATA"]) / "ptu-eval/conversation"
target = local / "containers"
sha = subprocess.check_output(
    ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
).strip()
if sha != "8a00aa54bc25fd3624020648c63f2c069172d8ca":
    raise RuntimeError("Source SHA changed; reinspect before packaging")
if target.exists() and any(target.iterdir()):
    raise RuntimeError("Refusing to overwrite existing container build contexts")
api = target / "api"
api.mkdir(parents=True)
archive = subprocess.check_output(["git", "-C", str(repo), "archive", "HEAD:src/api"])
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
    tar.extractall(api, filter="data")
for path in api.rglob("*"):
    if path.is_file() and (path.name == ".env" or path.name.startswith(".env.")):
        path.unlink()  # build-context exclusion only, never Azure cleanup
(api / ".dockerignore").write_text(
    ".env\n.env.*\n.azure\n.git\n__pycache__\n*.pyc\n*.log\n", encoding="utf-8"
)

frontend = local / "frontend"
build = frontend / "build"
if not (build / "index.html").exists():
    raise RuntimeError("The previously verified original frontend build is missing")
for subdir in ("src", "public"):
    for original in (repo / "src/app" / subdir).rglob("*"):
        if original.is_file():
            relative = original.relative_to(repo / "src/app")
            if original.read_bytes() != (frontend / relative).read_bytes():
                raise RuntimeError(f"Frontend source changed: {relative}")
ui = target / "ui"
ui.mkdir()
shutil.copytree(build, ui / "build")
shutil.copyfile(repo / "src/app/nginx.conf", ui / "nginx.conf")
(ui / "public").mkdir()
shutil.copyfile(repo / "src/app/public/startup.sh", ui / "public/startup.sh")
official_web = (repo / "src/app/WebApp.Dockerfile").read_text(encoding="utf-8")
runtime = official_web[official_web.index("FROM nginx:alpine"):]
runtime = runtime.replace(
    "COPY --from=build /home/node/app/build /usr/share/nginx/html",
    "COPY build /usr/share/nginx/html",
)
(ui / "WebApp.Runtime.Dockerfile").write_text(runtime, encoding="utf-8")

record = {
    "source_sha": sha,
    "workspace": str(target),
    "api": {
        "context": str(api),
        "dockerfile": "ApiApp.Dockerfile",
        "source_dockerfile_unchanged": True,
        "python_base": "python:3.13-slim",
        "odbc": "Official Dockerfile installs msodbcsql18 inside Linux image",
        "target_port": 8000,
        "tag": "ptu-conversation/api:8a00aa5-base",
    },
    "ui": {
        "context": str(ui),
        "dockerfile": "WebApp.Runtime.Dockerfile",
        "adaptation": "Official nginx runtime stage packages previously verified original build; npm build stage not repeated",
        "application_source_unchanged": True,
        "index_sha256": hashlib.sha256((build / "index.html").read_bytes()).hexdigest(),
        "target_port": 80,
        "upstream_expose_metadata_is_3000_but_nginx_listens_on_80": True,
        "runtime_environment": {
            "APP_API_BASE_URL": "/api",
            "BACKEND_API_HOST": "<internal API Container App FQDN after deployment>",
        },
        "tag": "ptu-conversation/ui:8a00aa5-runtime",
    },
    "builder": {"name": "ptu-conversation-eval", "memory_limit_bytes": 2147483648, "cpu_limit": 1, "parallel_builds": 1},
    "azure_actions": [],
    "images_built": False,
    "image_push_performed": False,
    "live_model_requests": 0,
}
(bundle / "evidence/conversation/container-build-preparation.json").write_text(
    json.dumps(record, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(record, indent=2))
