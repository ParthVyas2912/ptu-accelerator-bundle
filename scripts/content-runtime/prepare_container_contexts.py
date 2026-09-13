"""Stage official source contexts outside OneDrive; no builds, uploads or deletes."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

BUNDLE = Path(__file__).resolve().parents[2]
REPO = Path.home() / "OneDrive - Microsoft/Desktop/repo/content-processing-solution-accelerator"
SHA = "659eaa1f503dd08b1e1aea1c72eab11c7c191d00"
ROOT = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/container-contexts" / SHA[:7]
services = {"api": "ContentProcessorAPI", "processor": "ContentProcessor",
            "workflow": "ContentProcessorWorkflow", "web": "ContentProcessorWeb"}
actual_sha = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                                     text=True).strip()
if actual_sha != SHA:
    raise RuntimeError("Source SHA changed; refusing to silently change evaluation image")
manifest = {"repositorySha": SHA, "contextRoot": str(ROOT),
            "imagesBuilt": False, "imagesPushed": False, "contexts": {}}
pattern = re.compile(rb"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
                     rb"gh[pousr]_[A-Za-z0-9]{30,}|"
                     rb"eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,})")
for label, service in services.items():
    prefix = f"src/{service}/"
    files = subprocess.check_output(["git", "-C", str(REPO), "ls-files", "-z", "--", prefix])
    copied, hashes = 0, hashlib.sha256()
    destination = ROOT / label
    if destination.exists():
        # Reproducibility: inspect the original staged files, never overwrite a
        # context silently. Use a new explicit revision for runtime overlays.
        raise RuntimeError(f"Context exists; preserve it rather than overwriting: {destination}")
    for path in files.decode("utf-8").split("\0"):
        if not path:
            continue
        relative = Path(path[len(prefix):])
        if any(part.startswith(".env") for part in relative.parts) or relative.suffix == ".env":
            continue
        source = REPO / path
        data = source.read_bytes()
        if pattern.search(data):
            raise RuntimeError(f"Credential-pattern candidate; context not safe to upload: {path}")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes.update(relative.as_posix().encode() + b"\0" + hashlib.sha256(data).digest())
        copied += 1
    dockerfile = destination / "Dockerfile"
    assert dockerfile.read_bytes() == (REPO / prefix / "Dockerfile").read_bytes()
    manifest["contexts"][label] = {
        "path": str(destination), "files": copied, "treeDigestSha256": hashes.hexdigest(),
        "officialDockerfileSha256": hashlib.sha256(dockerfile.read_bytes()).hexdigest(),
        "image": f"acrptubundle7d804f70.azurecr.io/content/official-{label}:{SHA[:7]}",
        "runtimeOverlayStillRequired": label != "web",
        "secretEnvironmentFilesExcluded": True}
path = BUNDLE / "evidence/content/container-contexts.json"
path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
