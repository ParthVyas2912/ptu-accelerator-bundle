"""Export minimal original API source plus bounded synthetic evaluation support."""
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

bundle = Path(__file__).resolve().parents[1]
repo = bundle.parents[1] / "repo/Conversation-Knowledge-Mining-Solution-Accelerator"
target = Path(os.environ["LOCALAPPDATA"]) / "ptu-eval/conversation/summary-eval-context"
if target.exists() and any(target.iterdir()):
    raise RuntimeError("Refusing to overwrite an existing summary evaluation build context")
sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
if sha != "8a00aa54bc25fd3624020648c63f2c069172d8ca":
    raise RuntimeError("Reinspect changed source before packaging")
target.mkdir(parents=True, exist_ok=True)
source = subprocess.check_output(["git", "-C", str(repo), "archive", "HEAD:src/api"])
with tarfile.open(fileobj=io.BytesIO(source)) as archive:
    archive.extractall(target, filter="data")
for path in target.rglob("*"):
    if path.is_file() and (path.name == ".env" or path.name.startswith(".env.")):
        path.unlink()
(target / ".dockerignore").write_text(
    ".env\n.env.*\n.azure\n.git\n__pycache__\n*.pyc\n*.log\ninternaldocs\n",
    encoding="utf-8",
)
shutil.copyfile(bundle / "scripts/ckm_summary_eval.py", target / "ckm_summary_eval.py")
shutil.copyfile(
    bundle / "test-data/conversation/support-conversations.json",
    target / "ckm-support-conversations.json",
)
print(json.dumps({
    "context": str(target),
    "source_sha": sha,
    "dockerfile": "ApiApp.Dockerfile",
    "original_dockerfile_source_unchanged": (target / "ApiApp.Dockerfile").read_bytes().replace(b"\r\n", b"\n")
        == subprocess.check_output(["git", "-C", str(repo), "show", "HEAD:src/api/ApiApp.Dockerfile"]).replace(b"\r\n", b"\n"),
    "archive_eol_note": "Git archive checkout conversion produced CRLF; verified identical to Git blob after newline normalization, with no authored Dockerfile change.",
    "new_files": ["ckm_summary_eval.py", "ckm-support-conversations.json"],
    "model_requests": 0,
}))
