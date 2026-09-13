"""Prepare tiny guarded overlays on official SHA-tagged images; no build/upload."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil

BUNDLE = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/cloud-overlays/r2"
REPO = Path.home() / "OneDrive - Microsoft/Desktop/repo/content-processing-solution-accelerator"
files = ["sitecustomize.py", "content_guard.py", "cloud_budget.py", "cloud_entry.py",
         "cloud_probe.py", "cloud_export.py", "exercise_app.py"]
manifest = {"revision": "659eaa1-r2", "contexts": {}}
for service in ("api", "processor", "workflow"):
    folder = ROOT / service
    runtime = folder / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    for name in files:
        source = Path(__file__).parent / name
        ast.parse(source.read_text())
        shutil.copy2(source, runtime / name)
    shutil.copytree(BUNDLE / "test-data/content", runtime / "fixtures/content", dirs_exist_ok=True)
    schemas = REPO / "src/ContentProcessorAPI/samples/schemas"
    target = runtime / "fixtures/schemas"
    target.mkdir(parents=True, exist_ok=True)
    for path in schemas.glob("*.json"):
        shutil.copy2(path, target / path.name)
    dockerfile = (
        f"FROM acrptubundle7d804f70.azurecr.io/content/official-{service}:659eaa1\n"
        "USER root\nCOPY runtime/ /opt/content_eval/\n"
        "ENV PYTHONPATH=/opt/content_eval CONTENT_NATIVE_GUARD=1 CONTENT_BUDGET_BACKEND=blob "
        "APP_ENV=prod PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 "
        f"CONTENT_SERVICE={service} CONTENT_FIXTURE_ROOT=/opt/content_eval/fixtures "
        "CONTENT_EVIDENCE_ROOT=/tmp/content-evidence CONTENT_API_BASE_URL=http://127.0.0.1:80\n"
    )
    if service != "api":
        dockerfile += "USER gsauser\n"
    dockerfile += 'ENTRYPOINT ["/app/.venv/bin/python", "/opt/content_eval/cloud_entry.py"]\nCMD []\n'
    (folder / "Dockerfile").write_text(dockerfile, encoding="utf-8")
    manifest["contexts"][service] = {
        "path": str(folder),
        "image": f"acrptubundle7d804f70.azurecr.io/content/eval-{service}:659eaa1-r2",
        "dockerfileSha256": hashlib.sha256(dockerfile.encode()).hexdigest(),
        "fileCount": len(list(folder.rglob("*")))}
(BUNDLE / "evidence/content/cloud-overlays.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
