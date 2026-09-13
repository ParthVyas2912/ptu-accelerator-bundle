"""Stage only Modernize source for official Dockerfile builds; no Azure operations."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

B = Path(__file__).resolve().parents[1]
R = B.parent.parent/"repo/Modernize-your-code-solution-accelerator"
ROOT = Path(os.environ["LOCALAPPDATA"])/"ptu-modernize-container-build"
ROOT.mkdir(parents=True, exist_ok=True)
commit = subprocess.check_output(["git", "-C", str(R), "rev-parse", "HEAD"], text=True).strip()
assert commit == "7592ea97550fb711d7d8b64186875967d574c5d5"
manifest = {"commit": commit, "root": str(ROOT), "contexts": {}, "cloud_deployed": False}
for service in ["backend", "frontend"]:
    target = ROOT/service
    if target.exists():
        raise SystemExit(f"Build context already exists; inspect rather than overwrite: {target}")
    shutil.copytree(R/"src"/service, target, ignore=shutil.ignore_patterns(
        ".env", ".env.*", ".venv", "venv", "__pycache__", ".pytest_cache",
        "node_modules", "dist", "*.log", ".git", ".azure", ".ssh", ".aws",
        ".npmrc", ".pypirc", "pip.ini"
    ))
    dockerfile = (target/"Dockerfile").read_bytes()
    adapted = dockerfile.decode().replace(
        "FROM python:3.11-slim",
        "FROM python:3.11-slim\nARG PIP_INDEX_URL=https://packagefeedproxy.microsoft.io/pypi/simple/")
    (target/"Dockerfile").write_text(adapted, encoding="utf-8")
    manifest["contexts"][service] = {
        "path": str(target), "source_dockerfile": f"src/{service}/Dockerfile",
        "dockerfile_sha256": hashlib.sha256(dockerfile).hexdigest(),
        "adapted_dockerfile_sha256": hashlib.sha256(adapted.encode()).hexdigest(),
        "build_adaptation": "Microsoft package mirror; TLS verification remains enabled",
        "production_source_fix_included": service == "backend",
    }
    forbidden = [str(p) for p in target.rglob("*")
                 if p.name in {".env", ".azure", ".ssh", ".aws"} or p.suffix in {".pem", ".pfx", ".key"}]
    if forbidden:
        raise SystemExit("Unexpected credential-like file in isolated build context; inspect without printing content.")
(B/"evidence/modernize/container-build-contexts.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
