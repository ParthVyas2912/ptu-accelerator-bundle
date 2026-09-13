"""Capture the manually reviewed PTU evaluation source allowlist.

Run only with --capture and the explicitly scoped clone parent. All writes are
confined to this script's adaptations directory. No application code is imported,
no provider/network/Azure command is run, and external repositories are read-only.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone

from safety import findings


ROOT = Path(__file__).resolve().parents[1]
os.environ["GIT_OPTIONAL_LOCKS"] = "0"

# Exact origins and pinned heads inspected on 2026-09-13 UTC. GitHub's repository
# metadata API independently reported private=false and MIT for all 15 unique
# origins. The document-generation origin redirects to content-generation.
REPOS = [
    ("first-pass/cwyd", "chat-with-your-data-solution-accelerator", "Azure-Samples/chat-with-your-data-solution-accelerator", "0fce71307dfa76a82ac82ec73bdde3daa47e503d"),
    ("first-pass/content-processing", "content-processing-solution-accelerator", "microsoft/content-processing-solution-accelerator", "659eaa1f503dd08b1e1aea1c72eab11c7c191d00"),
    ("first-pass/conversation", "Conversation-Knowledge-Mining-Solution-Accelerator", "microsoft/Conversation-Knowledge-Mining-Solution-Accelerator", "8a00aa54bc25fd3624020648c63f2c069172d8ca"),
    ("first-pass/chatbot", "customer-chatbot-solution-accelerator", "microsoft/customer-chatbot-solution-accelerator", "cb86d1153df30a1bc6e744d74d3ff583764cd154"),
    ("first-pass/dkm", "Document-Knowledge-Mining-Solution-Accelerator", "microsoft/Document-Knowledge-Mining-Solution-Accelerator", "7df8ed33a86dd4f0f9e7417e882039fd38556e59"),
    ("first-pass/modernize", "Modernize-your-code-solution-accelerator", "microsoft/Modernize-your-code-solution-accelerator", "7592ea97550fb711d7d8b64186875967d574c5d5"),
    ("first-pass/macae", "Multi-Agent-Custom-Automation-Engine-Solution-Accelerator", "microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator", "8ac703a71f10b622bd3c82a9cc2b5dfe921c3025"),
    ("continuation/call-center-voice", "continuation/call-center-voice", "Azure-Samples/call-center-voice-agent-accelerator", "162cef590787b3bcc0a051608a7981f2a01daf41"),
    ("continuation/document-generation", "continuation/document-generation", "microsoft/document-generation-solution-accelerator", "fa956c9ec374f0f7e9b03ae2873d38e5269186fe"),
    ("continuation/ess-devkit", "continuation/ess-devkit", "microsoft/Employee-Self-Service-Agent-Developer-Kit", "3236a513b7312b13602326fbdf7778797174d45f"),
    ("continuation/macae", "continuation/macae", "microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator", "8ac703a71f10b622bd3c82a9cc2b5dfe921c3025"),
    ("continuation/netaivideoanalyzer", "continuation/netaivideoanalyzer", "Azure-Samples/netaivideoanalyzer", "1d8ed2ece3ee4c05441f98a0e06965c0207f21e7"),
    ("continuation/private-tenant-chat", "continuation/private-tenant-chat", "microsoft/Deploy-Your-AI-Application-In-Production", "1ed62d982f777b85f3fe281adfd7150921ccd9ce"),
    ("continuation/real-time-ops", "continuation/real-time-ops", "microsoft/real-time-intelligence-operations-solution-accelerator", "cfbdb91ee83ed31b5ccc5de7feca7a0b5b2e5f68"),
    ("continuation/stepfly", "continuation/stepfly", "microsoft/StepFly", "a6229192a69dd2eebc58d9b8f754dbc396029c4e"),
    ("continuation/unified-data-foundation", "continuation/unified-data-foundation", "microsoft/agentic-applications-for-unified-data-foundation-solution-accelerator", "28c25024e43884b0a23c996d5cc8d3419f4e448c"),
]

TRACKED = {
    "first-pass/chatbot": [
        "chat-app/backend/app/utils/azure_credential_utils.py",
        "chat-app/backend/app/utils/product_text_parser.py",
        "chat-app/frontend/startup.sh",
        "infra/scripts/post-provision/agent_scripts/01_create_agents.py",
        "infra/scripts/post-provision/data_scripts/01_create_products_search_index.py",
        "infra/scripts/post-provision/data_scripts/02_create_policies_search_index.py",
        "infra/scripts/post-provision/data_scripts/azure_credential_utils.py",
        "scenario-app/backend/app/utils/azure_credential_utils.py",
        "scenario-app/frontend/startup.sh",
        "scenarios/ecommerce/manifest.json",
    ],
    "first-pass/dkm": [
        "App/backend-api/.dockerignore",
        "App/backend-api/Microsoft.GS.DPS.Host/DependencyConfiguration/ServiceDependencies.cs",
        "App/frontend-app/.dockerignore",
        "App/kernel-memory/.dockerignore",
        "App/kernel-memory/extensions/AzureOpenAI/AzureOpenAITextEmbeddingGenerator.cs",
        "App/kernel-memory/service/Core/Handlers/KeywordExtractingHandler.cs",
        "infra/main.bicep",
    ],
    "first-pass/modernize": [
        "src/backend/sql_agents/convert_script.py",
        "src/tests/backend/sql_agents/convert_script_test.py",
    ],
    "first-pass/macae": [
        "src/backend/orchestration/connection_config.py",
        "src/tests/backend/orchestration/test_connection_config.py",
    ],
    "continuation/stepfly": ["config/config.json"],
}

SOURCES = {
    "first-pass/chatbot": [
        "infra/chatbot-cloud-identities.bicep",
        "infra/chatbot-cloud.bicep",
        "infra/chatbot-container-app.bicep",
        "infra/chatbot-local-access.bicep",
        "infra/chatbot-local-eval.bicep",
        "infra/chatbot-registry-access.bicep",
        "infra/chatbot-search-access.bicep",
        "infra/chatbot-search-approved.bicep",
        "infra/chatbot-search-retry.bicep",
    ],
    "first-pass/dkm": [
        "App/backend-api/Microsoft.GS.DPS.Host/Helpers/EvaluationRetryConfiguration.cs",
        "App/kernel-memory/service/Abstractions/Configuration/EvaluationRetryConfiguration.cs",
    ],
    "continuation/stepfly": ["lab_instrument.py", "lab_run.py", "requirements.lab.txt"],
    "continuation/netaivideoanalyzer": [
        "src/ConsoleAOAI-Lab-VideoAnalyzer/Program.cs",
        "src/ConsoleAOAI-Lab-VideoAnalyzer/ConsoleAOAI-Lab-VideoAnalyzer.csproj",
    ],
    "continuation/ccv-lab": ["voicelive_probe.py"],
}

SCOPE_BASIS = {
    "first-pass/chatbot": "Reviewed evaluation-specific catalog validation, bounded ingestion, managed identity, ACA DNS, scenario naming and lab-only Bicep composition.",
    "first-pass/dkm": "Reviewed evaluation retry opt-in helpers, image-context exclusions and explicitly documented AKS SKU availability adaptation.",
    "first-pass/modernize": "Reviewed migration failure/placeholder correctness fix and regression tests; recorded in prior evaluation session.",
    "first-pass/macae": "Reviewed structured WebSocket event serialization fix and matching synthetic regression tests.",
    "continuation/stepfly": "Explicitly requested lab harness, dependency pins and reduced executor/model configuration; prior continuation session recorded harness authorship.",
    "continuation/netaivideoanalyzer": "Explicitly requested Entra-auth video measurement harness and project; prior continuation session recorded authorship.",
    "continuation/ccv-lab": "Explicitly requested standalone Voice Live provider probe; prior continuation session recorded authorship.",
}

EXTRA_OMISSIONS = {
    "first-pass/dkm": [
        ("App/backend-api/Microsoft.GS.DPS.Host/appsettings.Development.json", "Local machine/application configuration; contents not read."),
        ("App/frontend-app/.env", "Environment/secrets file; contents not read."),
    ],
    "continuation/netaivideoanalyzer": [
        ("src/ConsoleAOAI-Lab-VideoAnalyzer/bin/", "Build binaries/dependencies; directory names only."),
        ("src/ConsoleAOAI-Lab-VideoAnalyzer/obj/", "Build intermediates; directory names only."),
        *[(f"src/ConsoleAOAI-Lab-VideoAnalyzer/data-{label}/", "Synthetic decoded frames/media; directory names only.")
          for label in ("v1-native-describe", "v2-absent-event", "v3-ordering", "v4-insurance", "v5-compare")],
    ],
    "continuation/ccv-lab": [
        (name, "Virtual environment or machine configuration; contents not read.")
        for name in ("Include/", "Lib/", "Scripts/", "pyvenv.cfg")
    ],
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    result = subprocess.run(
        ["git", "--no-pager", "-C", str(repo), *args],
        capture_output=True, check=False,
    )
    if result.returncode:
        # Do not echo stderr, which may include local credential/config values.
        raise RuntimeError(f"Read-only Git operation failed ({args[0]}), exit {result.returncode}")
    return result.stdout


def checked_source(repo, rel):
    path = repo / rel
    if path.is_symlink() or not path.resolve().is_relative_to(repo.resolve()):
        raise RuntimeError(f"Unsafe source path: {rel}")
    if not path.is_file() or path.stat().st_size > 250_000:
        raise RuntimeError(f"Source is missing or exceeds the 250 KB bound: {rel}")
    data = path.read_bytes()
    if b"\x00" in data:
        raise RuntimeError(f"Binary source refused: {rel}")
    data.decode("utf-8-sig")
    return data


def require_clean(text, label):
    hits = findings(text)
    if hits:
        locations = [{"rule": x["rule"], "line": x["line"]} for x in hits]
        raise RuntimeError(f"Credential-pattern scan blocked {label}: {locations}")


def status(repo):
    raw = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=normal")
    rows = []
    for record in raw.split(b"\x00"):
        if not record:
            continue
        text = record.decode("utf-8")
        code, path = text[:2], text[3:]
        if "R" in code or "C" in code:
            raise RuntimeError("Unexpected rename/copy status requires manual review")
        rows.append({"status": code, "path": path})
    if len(rows) > 100:
        raise RuntimeError("Dirty inventory exceeded the manually reviewed bound")
    return rows


def transform(repo_id, rel, raw):
    text = raw.decode("utf-8-sig").replace("\r\n", "\n")
    changes = []

    def replace(old, new, note):
        nonlocal text
        if text.count(old) != 1:
            raise RuntimeError(f"Safety edit needs re-review: {repo_id}/{rel}")
        text = text.replace(old, new, 1)
        changes.append(note)

    if repo_id == "first-pass/chatbot" and rel in (
        "infra/chatbot-cloud.bicep", "infra/chatbot-container-app.bicep",
    ):
        text, count = re.subn(
            r"param clientCidr string = '[^']+'", "param clientCidr string", text,
        )
        if count != 1:
            raise RuntimeError("Expected one machine-specific client CIDR default")
        changes.append("Removed machine-specific client CIDR default; an explicitly approved clientCidr parameter is now required.")
    if repo_id == "continuation/stepfly" and rel == "lab_instrument.py":
        replace(
            'BUDGET = int(os.environ.get("LAB_ATTEMPT_BUDGET", "20"))',
            'BUDGET = int(os.environ.get("LAB_ATTEMPT_BUDGET", "0"))\n'
            'if os.environ.get("LAB_ALLOW_PROVIDER_CALLS") != "1":\n'
            '    BUDGET = 0',
            "Changed default provider-attempt budget from 20 to 0; independent explicit opt-in is required.",
        )
    if repo_id == "continuation/stepfly" and rel == "lab_run.py":
        replace(
            "import lab_instrument\n",
            'if (os.environ.get("LAB_ALLOW_PROVIDER_CALLS") != "1"\n'
            '        or int(os.environ.get("LAB_ATTEMPT_BUDGET", "0")) <= 0):\n'
            '    raise SystemExit("Archived harness is disarmed; provider execution requires separate approval.")\n\n'
            "import lab_instrument\n",
            "Added fail-closed gate before importing the scheduler/instrumentation.",
        )
    if repo_id == "continuation/netaivideoanalyzer" and rel.endswith("/Program.cs"):
        replace(
            'string videoFile = GetArg("--video")',
            'if (Environment.GetEnvironmentVariable("LAB_ALLOW_PROVIDER_CALLS") != "1"\n'
            '    || !int.TryParse(Environment.GetEnvironmentVariable("LAB_ATTEMPT_BUDGET"), out var approvedBudget)\n'
            '    || approvedBudget <= 0)\n'
            '{\n'
            '    throw new InvalidOperationException("Archived harness is disarmed; provider execution requires separate approval.");\n'
            '}\n\n'
            'string videoFile = GetArg("--video")',
            "Added fail-closed opt-in and positive-budget gate before media decoding, credential creation or provider calls. This is not an aggregate/retry budget implementation.",
        )
    if repo_id == "continuation/ccv-lab":
        replace(
            'ENDPOINT = os.environ["AZURE_VOICE_LIVE_ENDPOINT"]',
            'if (os.environ.get("LAB_ALLOW_PROVIDER_CALLS") != "1"\n'
            '        or int(os.environ.get("VL_MAX_ATTEMPTS", "0")) <= 0):\n'
            '    raise SystemExit("Archived harness is disarmed; provider execution requires separate approval.")\n\n'
            'ENDPOINT = os.environ["AZURE_VOICE_LIVE_ENDPOINT"]',
            "Added explicit opt-in and positive-attempt gate before resolving endpoint or starting the provider probe.",
        )
        replace(
            'MAX_ATTEMPTS = int(os.environ.get("VL_MAX_ATTEMPTS", "4"))',
            'MAX_ATTEMPTS = int(os.environ.get("VL_MAX_ATTEMPTS", "0"))',
            "Changed default Voice Live attempt budget from 4 to 0.",
        )
    if changes and b"\r\n" in raw:
        changes.append("Normalized CRLF to LF in the safety-transformed archive copy.")
    # Preserve bytes exactly unless an explicit safety transformation was needed.
    return (text.encode("utf-8") if changes else raw), changes


def capture(clones):
    manifest_path = ROOT / "manifest.json"
    if manifest_path.exists():
        raise RuntimeError("Refusing to overwrite an existing capture; review/archive it first.")
    artifacts = []
    pending = {}
    entries = []
    snapshots = {}

    def queue(path, data, kind, **metadata):
        require_clean(data.decode("utf-8-sig"), path)
        destination = ROOT / path
        if not destination.resolve().is_relative_to(ROOT) or destination.exists():
            raise RuntimeError(f"Refusing an unsafe/existing output: {path}")
        if path in pending:
            raise RuntimeError(f"Duplicate artifact: {path}")
        pending[path] = data
        item = {"path": path, "kind": kind, "bytes": len(data), "sha256": digest(data), **metadata}
        artifacts.append(item)
        return item

    for repo_id, local, github_name, sha in REPOS:
        repo = clones / local
        origin = git(repo, "remote", "get-url", "origin").decode().strip()
        head = git(repo, "rev-parse", "HEAD").decode().strip()
        if origin != "https://github.com/" + github_name or head != sha:
            raise RuntimeError(f"Origin/base changed for {repo_id}; manual re-review required")
        rows = status(repo)
        snapshots[repo_id] = (head, rows)
        tracked = TRACKED.get(repo_id, [])
        sources = SOURCES.get(repo_id, [])
        omitted = []
        for row in rows:
            rel = row["path"]
            if rel in tracked and row["status"] != "??":
                row["disposition"] = "tracked-patch"
            elif row["status"] == "??" and (rel in sources or any(p.startswith(rel) for p in sources if rel.endswith("/"))):
                row["disposition"] = "allowlisted-source-only"
            else:
                reason = (
                    "Virtual environment; no contents captured." if rel.startswith(".venv/") else
                    "Run telemetry/log/counter artifact; bundle evidence is handled separately." if rel.endswith((".log", ".jsonl", ".counter", ".aborted")) else
                    "Not on the reviewed evaluation-source allowlist; ownership/scope not assumed."
                )
                row["disposition"] = "omitted"
                omitted.append({"path": rel, "reason": reason})
        for rel, reason in EXTRA_OMISSIONS.get(repo_id, []):
            omitted.append({"path": rel, "reason": reason})
        entry = {
            "id": repo_id,
            "kind": "git-clone",
            "source_relative_to_clone_parent": local,
            "origin_exact": origin,
            "base_sha": sha,
            "public_upstream_verified": True,
            "github_full_name": github_name.replace("document-generation-", "content-generation-"),
            "upstream_license_spdx": "MIT",
            "dirty_files": rows,
            "scope_basis": SCOPE_BASIS.get(repo_id, "No nonignored authored source changes observed; pinned metadata only."),
            "tracked_changes": [],
            "untracked_sources": [],
            "license_copies": [],
            "omissions": omitted,
        }
        for rel in tracked:
            if not any(x["path"] == rel and x["status"] != "??" for x in rows):
                raise RuntimeError(f"Reviewed tracked change disappeared: {repo_id}/{rel}")
            data = checked_source(repo, rel)
            base = git(repo, "show", f"{sha}:{rel}")
            entry["tracked_changes"].append({
                "path": rel, "base_sha256": digest(base),
                "working_tree_sha256": digest(data), "working_tree_bytes": len(data),
            })
        if tracked:
            patch = git(
                repo, "diff", "--no-ext-diff", "--no-textconv", "--no-renames",
                "--full-index", "--src-prefix=a/", "--dst-prefix=b/", sha, "--", *tracked,
            )
            if not patch or b"GIT binary patch" in patch:
                raise RuntimeError(f"Missing or binary patch: {repo_id}")
            require_clean(patch.decode("utf-8"), repo_id + "/tracked.patch")
            queue(repo_id + "/tracked.patch", patch, "tracked-patch", repo_id=repo_id,
                  tracked_file_count=len(tracked), transformations=[])
            entry["patch"] = repo_id + "/tracked.patch"
        for rel in sources:
            # Ensure a presumed authored/untracked copy is not upstream content.
            if git(repo, "ls-files", "--", rel).strip():
                raise RuntimeError(f"Expected untracked source is tracked: {repo_id}/{rel}")
            raw = checked_source(repo, rel)
            require_clean(raw.decode("utf-8-sig"), repo_id + "/" + rel)
            data, changes = transform(repo_id, rel, raw)
            item = queue(repo_id + "/files/" + rel, data, "authored-source",
                         repo_id=repo_id, source_path=rel, source_sha256=digest(raw),
                         transformations=changes)
            entry["untracked_sources"].append(item["path"])
        if tracked or sources:
            license_paths = ["LICENSE"]
            if repo_id == "first-pass/dkm":
                license_paths.append("App/kernel-memory/LICENSE")
            for rel in license_paths:
                data = git(repo, "show", f"{sha}:{rel}")
                item = queue(repo_id + "/upstream/" + rel, data, "upstream-license",
                             repo_id=repo_id, source_path=rel, upstream_base_sha=sha,
                             source_url=f"{origin}/blob/{sha}/{rel}")
                entry["license_copies"].append(item["path"])
        entries.append(entry)

    # ccv-lab is a standalone authored script inside a virtual-environment root,
    # NOT a clone; do not fabricate its own Git origin or SHA.
    repo_id = "continuation/ccv-lab"
    repo = clones / repo_id
    if (repo / ".git").exists():
        raise RuntimeError("Standalone probe unexpectedly became a Git repository")
    rel = "voicelive_probe.py"
    raw = checked_source(repo, rel)
    require_clean(raw.decode("utf-8-sig"), repo_id + "/" + rel)
    data, changes = transform(repo_id, rel, raw)
    item = queue(repo_id + "/files/" + rel, data, "authored-source", repo_id=repo_id,
                 source_path=rel, source_sha256=digest(raw), transformations=changes)
    related = next(x for x in entries if x["id"] == "continuation/call-center-voice")
    license_path = repo_id + "/upstream/call-center-voice/LICENSE.md"
    queue(license_path, git(clones / "continuation/call-center-voice", "show",
                           related["base_sha"] + ":LICENSE.md"),
          "upstream-license", repo_id=repo_id, source_path="LICENSE.md",
          upstream_base_sha=related["base_sha"],
          source_url=f'{related["origin_exact"]}/blob/{related["base_sha"]}/LICENSE.md',
          note="Related accelerator attribution; standalone probe has no separate upstream Git history.")
    entries.append({
        "id": repo_id, "kind": "standalone-authored-source",
        "source_relative_to_clone_parent": repo_id,
        "origin_exact": None, "base_sha": None,
        "related_upstream_repo_id": related["id"],
        "related_upstream_base_sha": related["base_sha"],
        "scope_basis": SCOPE_BASIS[repo_id],
        "dirty_files": [{"status": "not-a-git-repository", "path": rel, "disposition": "allowlisted-source-only"}],
        "tracked_changes": [], "untracked_sources": [item["path"]],
        "license_copies": [license_path],
        "omissions": [{"path": p, "reason": r} for p, r in EXTRA_OMISSIONS[repo_id]],
    })
    # Confirm no upstream working-tree changes raced the snapshot.
    for repo_id, local, _, sha in REPOS:
        repo = clones / local
        rows = status(repo)
        original_rows = [{"status": x["status"], "path": x["path"]} for x in snapshots[repo_id][1]]
        if git(repo, "rev-parse", "HEAD").decode().strip() != sha or rows != original_rows:
            raise RuntimeError(f"Source metadata changed while capturing: {repo_id}")
    for entry in entries:
        repo = clones / entry["source_relative_to_clone_parent"]
        for tracked in entry["tracked_changes"]:
            if digest(checked_source(repo, tracked["path"])) != tracked["working_tree_sha256"]:
                raise RuntimeError("Tracked source changed while capturing")
    for item in artifacts:
        if item["kind"] == "authored-source":
            local = next(x["source_relative_to_clone_parent"] for x in entries if x["id"] == item["repo_id"])
            if digest(checked_source(clones / local, item["source_path"])) != item["source_sha256"]:
                raise RuntimeError("Authored source changed while capturing")
    manifest = {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Only the 16 named accelerator clones and the standalone ccv-lab probe; no other repositories read.",
        "public_upstream_verification": {
            "method": "Read-only GitHub repository metadata API; private=false and MIT for all 15 unique upstreams.",
            "verified_on_utc": "2026-09-13",
            "content_uploaded": False,
        },
        "authorship_note": "Allowlist selected by explicit user scope, prior session file metadata where available, and direct diff/source review. Git dirtiness alone does not establish authorship.",
        "global_omissions": [
            "All unrelated repositories, including protected SpecSuite and Planetary repositories; directory names only were observed.",
            "All unchanged upstream source; retrieve using each exact origin and base SHA.",
            "All environments, node_modules, dependency caches, binaries, build outputs, synthetic DB/media and run telemetry.",
            "All .env variants, credential caches, user-secrets and local machine/application configuration; contents not read.",
            "Ignored artifact inventory is not exhaustive. Parent owns bundle evidence/source; this archive contains only external adaptations.",
        ],
        "safety": {
            "provider_calls_executed": 0, "azure_mutations_executed": 0,
            "deployment_executed": False, "external_clones_modified": False,
            "commits_or_pushes_executed": False,
            "archive_provider_defaults": "Disarmed; zero/missing attempt budget and explicit opt-in gates.",
            "account_endpoints_ids": "Retained as permitted private-repository metadata; not credentials.",
        },
        "counts": {
            "git_clones": len(REPOS), "standalone_sources": 1,
            "patches": sum(x["kind"] == "tracked-patch" for x in artifacts),
            "tracked_files": sum(len(x["tracked_changes"]) for x in entries),
            "authored_source_files": sum(x["kind"] == "authored-source" for x in artifacts),
            "license_copies": sum(x["kind"] == "upstream-license" for x in artifacts),
            "specific_omission_records": sum(len(x["omissions"]) for x in entries),
        },
        "repositories": entries,
        "artifacts": artifacts,
        "integrity": "All artifact bytes are SHA-256 hashed above; verification.json hashes every archive file except itself.",
    }
    # All source inspection/validation succeeds before any captured artifact write.
    for rel, data in pending.items():
        destination = ROOT / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true", required=True)
    parser.add_argument("--clone-parent", type=Path, required=True)
    args = parser.parse_args()
    capture(args.clone_parent.resolve())
