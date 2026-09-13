"""Prepare only the five nonsecret serving files for the approved small ACR layer."""
import json
import os
from pathlib import Path
import shutil

bundle = Path(__file__).resolve().parents[1]
target = Path(os.environ["LOCALAPPDATA"]) / "ptu-eval" / "conversation" / "serving-context-v1"
target.mkdir(parents=True, exist_ok=False)
for name in ["ckm_serving.py", "ckm_serving_guard.py", "ckm_serving_probe.py", "ckm_sql_identity.py"]:
    shutil.copyfile(bundle / "scripts" / name, target / name)
shutil.copyfile(bundle / "infra" / "conversation-serving.Dockerfile", target / "Dockerfile")
shutil.copyfile(bundle / "test-data" / "conversation" / "support-conversations.json", target / "ckm-serving-expected.json")
assert len(list(target.iterdir())) == 6
print(json.dumps({"context": str(target), "files": [file.name for file in target.iterdir()],
                  "bytes": sum(file.stat().st_size for file in target.iterdir())}))
