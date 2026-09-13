"""Create app-only, credential-free ACR contexts outside OneDrive; never upload the bundle."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("component", choices=["backend", "kernelmemory", "frontend", "retry-tests"])
parser.add_argument("--revision", default="")
args = parser.parse_args()
bundle = Path(__file__).resolve().parents[1]
repo = Path.home() / "OneDrive - Microsoft/Desktop/repo/Document-Knowledge-Mining-Solution-Accelerator"
if args.revision and not args.revision.replace("-", "").isalnum():
    raise SystemExit("Revision must contain only letters, digits and hyphens")
suffix = "-" + args.revision if args.revision else ""
dest = Path(os.environ["LOCALAPPDATA"]) / "ptu-eval/documents/remote-contexts" / (args.component + suffix)
if dest.exists():
    raise SystemExit(f"Context already exists; use a new version or inspect it first: {dest}")
dest.mkdir(parents=True)
manifest = []

def copy(source, relative):
    target = dest / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    manifest.append({"path": str(relative).replace("\\", "/"), "bytes": target.stat().st_size,
                     "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})

if args.component == "retry-tests":
    for name in ["Legacy.csproj", "Modern.csproj", "Program.cs", "task.yaml"]:
        copy(bundle / "tests/documents-retry" / name, Path(name))
    copy(repo / "App/backend-api/Microsoft.GS.DPS.Host/Helpers/EvaluationRetryConfiguration.cs", Path("BackendRetry.cs"))
    copy(repo / "App/kernel-memory/service/Abstractions/Configuration/EvaluationRetryConfiguration.cs", Path("KernelRetry.cs"))
else:
    relative_root = Path({"backend": "App/backend-api", "kernelmemory": "App/kernel-memory", "frontend": "App/frontend-app"}[args.component])
    component_root = repo / relative_root
    files = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "--cached", "--others", "--exclude-standard", "--", relative_root.as_posix()],
        text=True).splitlines()
    blocked_dirs = {".git", ".azure", "bin", "obj", "node_modules", ".vs", ".vscode", "logs", "coverage", "test-results"}
    for tracked in sorted(set(files)):
        relative = Path(tracked).relative_to(relative_root)
        lowered = [part.lower() for part in relative.parts]
        name = relative.name.lower()
        if any(part in blocked_dirs for part in lowered) or name.startswith(".env"):
            continue
        if name.endswith((".user", ".log", ".trx")) or (
            name.startswith("secret") and name.endswith((".json", ".yaml", ".yml", ".env"))
        ):
            continue
        source = component_root / relative
        if source.is_symlink():
            raise SystemExit("Refusing symlink in remote context: " + str(relative))
        if source.is_file():
            copy(source, relative)
    if args.component != "frontend":
        generated = Path("Microsoft.GS.DPS.Host/appsettings.Development.json") if args.component == "backend" else Path("service/Service/appsettings.Development.json")
        # Generated only from upstream templates: endpoint and retry/logging values, no fetched secrets.
        copy(component_root / generated, generated)
    if not (dest / "Dockerfile").is_file():
        raise SystemExit("Original Dockerfile missing")

output = {
    "component": args.component, "context_path": str(dest),
    "files": len(manifest), "bytes": sum(x["bytes"] for x in manifest),
    "selection": "Only app git-tracked/unignored source plus explicitly generated nonsecret development settings; no bundle/internal docs or credentials.",
    "manifest": manifest
}
(bundle / "evidence/documents" / f"remote-context-{args.component}{suffix}.json").write_text(
    json.dumps(output, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: output[k] for k in ["component", "context_path", "files", "bytes"]}))
