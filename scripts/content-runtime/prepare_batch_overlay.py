"""Stage only the batch script on already-built original-app/guard images."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil

source = Path(__file__).parent / "cloud_batch.py"
ast.parse(source.read_text())
root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/claim-batch"
images = {
    "api": ("659eaa1-r4", "bcf6c4910140b9c8750262144cd6f2a1bcd179904155cfdf6ecfd031e10424d9"),
    "processor": ("659eaa1-r3", "205246a928aca318399a6849e99827a5b8723bc2abc7442724eed3b6239ee4ae")}
manifest = {}
for service, (tag, digest) in images.items():
    context = root / service
    context.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, context / source.name)
    base = f"acrptubundle7d804f70.azurecr.io/content/eval-{service}@sha256:{digest}"
    (context / "Dockerfile").write_text(
        f"FROM {base}\nCOPY cloud_batch.py /opt/content_eval/cloud_batch.py\n", encoding="utf-8")
    manifest[service] = {"context": str(context), "base": base,
                         "image": f"content/eval-{service}:{tag}"}
manifest["scriptSha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
(Path(__file__).resolve().parents[2] / "evidence/content/batch-overlays.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
