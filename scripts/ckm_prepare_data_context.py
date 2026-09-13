"""Prepare a clean remote context before starting billable SQL compute."""
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

bundle = Path(__file__).resolve().parents[1]
repo = bundle.parents[1] / "repo" / "Conversation-Knowledge-Mining-Solution-Accelerator"
target = Path(os.environ["LOCALAPPDATA"]) / "ptu-eval" / "conversation" / "data-eval-context-v2"
if target.exists():
    raise RuntimeError("Refusing to overwrite an existing build context")
assert subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip() == "8a00aa54bc25fd3624020648c63f2c069172d8ca"
target.mkdir(parents=True)
archive_bytes = subprocess.check_output(["git", "-C", str(repo), "archive", "HEAD:src/api"])
with tarfile.open(fileobj=io.BytesIO(archive_bytes)) as archive:
    archive.extractall(target, filter="data")
for path in target.rglob("*"):
    if path.is_file() and (path.name == ".env" or path.name.startswith(".env.")):
        path.unlink()
(target / ".dockerignore").write_text(".env\n.env.*\n.azure\n.git\n__pycache__\n*.pyc\n*.log\n", encoding="utf-8")
for source, name in [
    (bundle / "scripts" / "ckm_data_eval.py", "ckm_data_eval.py"),
    (bundle / "test-data" / "conversation" / "support-conversations.json", "ckm-support-conversations.json"),
    (bundle / "evidence" / "conversation" / "summary-results.json", "ckm-prior-summaries.json"),
    (repo / "infra" / "scripts" / "post-provision" / "create_search_index.py", "ckm_create_search_index.py"),
]:
    shutil.copyfile(source, target / name)
print(json.dumps({"context": str(target), "original_api_dockerfile": True, "source_sha": "8a00aa54bc25fd3624020648c63f2c069172d8ca"}))
