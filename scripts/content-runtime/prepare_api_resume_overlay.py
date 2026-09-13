"""Two-file API-only patch context, built remotely on the verified r2 image."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil

bundle = Path(__file__).resolve().parents[2]
root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/api-resume-r3"
root.mkdir(parents=True, exist_ok=True)
source = Path(__file__).parent / "exercise_app.py"
ast.parse(source.read_text())
shutil.copy2(source, root / source.name)
base = ("acrptubundle7d804f70.azurecr.io/content/eval-api@sha256:"
        "5ccff2fc0df5bd31323bc5bd6d76195ee1bb0adfd40dae16bfd50b09f7e08224")
dockerfile = f"FROM {base}\nCOPY exercise_app.py /opt/content_eval/exercise_app.py\n"
(root / "Dockerfile").write_text(dockerfile, encoding="utf-8")
manifest = {
    "service": "api", "image": "acrptubundle7d804f70.azurecr.io/content/eval-api:659eaa1-r3",
    "context": str(root), "files": ["Dockerfile", "exercise_app.py"],
    "baseImage": base, "originalApplicationSourceModified": False,
    "originalDockerfileBase": "Original API Dockerfile -> guarded r2 -> driver-only patch",
    "driverSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "localCompilationOrDockerBuild": False}
(bundle / "evidence/content/api-resume-overlay.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
