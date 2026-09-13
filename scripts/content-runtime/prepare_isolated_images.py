import ast
import json
import os
from pathlib import Path
import shutil

scripts = Path(__file__).parent
root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval" / "isolated-missing-police"
bases = {
    "api": "c7a3183f6c88a34a63296e71d2763cd62796a10d9c48e97322738a8b3823b2fb",
    "processor": "fe0f073563841b7b9dd6f5c7faf204129dc05af2d7f977ecc4c46bff55b535a9",
    "workflow": "1f57f269a79d3f1dec916673bb8e229e04577e5e43d3f857837a5b7c16ae0e66",
}
manifest = {}
for service, digest in bases.items():
    context = root / service
    context.mkdir(parents=True, exist_ok=True)
    names = ["content_guard.py", "cloud_budget.py", "isolated_scope.py", "isolated_runtime.py",
             "test_isolated_scope.py", "test_inference_disarm.py"]
    if service == "api":
        names += ["exercise_app.py", "isolated_driver.py"]
    for name in names:
        ast.parse((scripts / name).read_text(encoding="utf-8"))
        shutil.copy2(scripts / name, context / name)
    entry = "cloud_entry.py" if service == "api" else "isolated_runtime.py"
    (context / "Dockerfile").write_text(
        f"FROM acrptubundle7d804f70.azurecr.io/content/eval-{service}@sha256:{digest}\n"
        f"COPY {' '.join(names)} /opt/content_eval/\n"
        "ENV CONTENT_INFERENCE_DISARMED=1 CONTENT_NATIVE_GUARD=1\n"
        "RUN CONTENT_NATIVE_GUARD=0 /app/.venv/bin/python -m unittest discover -s /opt/content_eval -p 'test_isolated_scope.py' -v\n"
        "RUN CONTENT_NATIVE_GUARD=0 /app/.venv/bin/python /opt/content_eval/test_inference_disarm.py\n"
        f'ENTRYPOINT ["/app/.venv/bin/python", "/opt/content_eval/{entry}"]\nCMD []\n',
        encoding="utf-8")
    revision = "r2" if service == "processor" else "r1"
    manifest[service] = {"context": str(context), "image": f"content/eval-{service}:659eaa1-scope-{revision}",
                         "baseDigest": digest, "files": names}
(scripts.parents[1] / "evidence" / "content" / "isolated-images.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
