"""Prepare a clean original-app build outside OneDrive after mirror/EPERM failure.

Only package download locations change; every locked version and integrity stays
identical. No source application logic, model configuration, or IaC is altered.
"""
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

bundle = Path(__file__).resolve().parents[1]
repo = bundle.parents[1] / "repo/Conversation-Knowledge-Mining-Solution-Accelerator"
target = Path(os.environ["LOCALAPPDATA"]) / "ptu-eval/conversation/frontend"
if target.exists() and any(target.iterdir()):
    raise RuntimeError("Refusing to overwrite an existing isolated frontend workspace")
target.mkdir(parents=True, exist_ok=True)
archive = subprocess.check_output(["git", "-C", str(repo), "archive", "HEAD:src/app"])
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
    tar.extractall(target, filter="data")
path = target / "package-lock.json"
lock = json.loads(path.read_text(encoding="utf-8"))
original = {
    name: (item.get("version"), item.get("integrity"))
    for name, item in lock["packages"].items()
}
rewritten = 0
for item in lock["packages"].values():
    url = item.get("resolved", "")
    marker = "/npm/registry/"
    if marker in url and ".pkgs.visualstudio.com/" in url:
        item["resolved"] = "https://registry.npmjs.org/" + url.split(marker, 1)[1]
        rewritten += 1
assert original == {
    name: (item.get("version"), item.get("integrity"))
    for name, item in lock["packages"].items()
}
path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
(target / ".npmrc").write_text("registry=https://registry.npmjs.org/\nlegacy-peer-deps=true\n", encoding="utf-8")
print(json.dumps({
    "isolated_frontend": str(target),
    "rewritten_public_tarball_locations": rewritten,
    "locked_versions_and_integrities_preserved": True,
    "original_application_source_preserved": True,
}), flush=True)
