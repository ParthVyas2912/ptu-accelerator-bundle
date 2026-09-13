"""Stage a guarded, idle-by-default overlay with an exact claim/input manifest."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil

bundle = Path(__file__).resolve().parents[2]
source = json.loads((bundle / "evidence/content/batch-run-complete-recovery.json").read_text())
claim = source["evidence"]["functional-results.json"]["cases"]["complete-recovery"]
assert claim["claimId"] == "9f9b9c98-2d6e-440f-9a67-099ffea26f51"
scope = {"claimId": claim["claimId"],
         "modelRecordSha256": "e8028913511c9377a114de8eb3100a5ebfe94d36d3dba4bffc73ef8840a8b272",
         "documents": []}
for item in claim["lastDetail"]["data"]["processed_documents"]:
    path = bundle / "test-data/content/complete" / item["file_name"]
    scope["documents"].append({"processId": item["process_id"], "fileName": item["file_name"],
                               "inputSha256": hashlib.sha256(path.read_bytes()).hexdigest()})
assert len(scope["documents"]) == 4
root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/zero-processor-r1"
root.mkdir(parents=True, exist_ok=True)
for name in ("zero_model_recovery.py", "content_guard.py", "test_inference_disarm.py"):
    path = Path(__file__).parent / name
    ast.parse(path.read_text())
    shutil.copy2(path, root / name)
(root / "zero_recovery_scope.json").write_text(json.dumps(scope, indent=2), encoding="utf-8")
(root / "Dockerfile").write_text(
    "FROM acrptubundle7d804f70.azurecr.io/content/eval-processor@sha256:"
    "8a9a254663ee525d843f8b5a7d670ff2b9facf0fdf0cd6af0ce1ef7cbc8ee39a\n"
    "COPY content_guard.py zero_model_recovery.py zero_recovery_scope.json /opt/content_eval/\n"
    "COPY test_inference_disarm.py /opt/content_eval/test_inference_disarm.py\n"
    "ENV CONTENT_INFERENCE_DISARMED=1 CONTENT_NATIVE_GUARD=1\n"
    "RUN CONTENT_NATIVE_GUARD=0 /app/.venv/bin/python /opt/content_eval/test_inference_disarm.py\n"
    'ENTRYPOINT ["/app/.venv/bin/python", "/opt/content_eval/zero_model_recovery.py", "idle"]\n'
    "CMD []\n", encoding="utf-8")
(bundle / "evidence/content/zero-recovery-build-context.json").write_text(
    json.dumps({"context": str(root), "scope": scope,
                "image": "content/eval-processor:659eaa1-zero-r1"}, indent=2), encoding="utf-8")
print(root)
