"""Offline verification only: never import or execute archived provider code."""

import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from safety import PATTERNS, findings


ROOT = Path(__file__).resolve().parents[1]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def scanner_self_test():
    # Synthetic samples are constructed only in memory, never saved or printed.
    samples = {
        "private-key": "-----BEGIN " + "PRIVATE KEY-----\ntest\n-----END " + "PRIVATE KEY-----",
        "github-token": "gh" + "p_" + "a" * 36,
        "provider-token": "s" + "k-" + "a" * 30,
        "jwt": "ey" + "J" + "a" * 20 + "." + "b" * 30 + "." + "c" * 30,
        "connection-credential": "Account" + "Key=" + "a" * 40 + ";",
        "sas-signature": "?s" + "ig=" + "a" * 40,
        "url-password": "".join(("https", "://", "user", ":", "a" * 24, "@", "example.invalid/")),
        "literal-secret": 'api_' + 'key = "' + "a" * 40 + '"',
        "literal-connection-string": '"' + "DefaultEndpointsProtocol=https;Account"
        + "Key=" + "a" * 40 + ';"',
    }
    for rule, sample in samples.items():
        # example.invalid is deliberately allowed only in the URL fixture:
        # the pattern itself must match even if placeholder filtering skips it.
        if not PATTERNS[rule].search(sample):
            raise RuntimeError(f"Scanner self-test failed: {rule}")
        if rule != "url-password" and not any(x["rule"] == rule for x in findings(sample)):
            raise RuntimeError(f"Scanner value-suppression self-test failed: {rule}")
    for sample in (
        'client_id="00000000-0000-0000-0000-000000000000"',
        'endpoint="https://sample.openai.azure.com/"',
        'api_key = os.environ["AZURE_OPENAI_API_KEY"]',
        'api_key = ""',
    ):
        if findings(sample):
            raise RuntimeError("Scanner rejected an allowed metadata/reference fixture")
    return len(samples)


def main():
    rules_tested = scanner_self_test()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    stats = []
    manifest_paths = set()
    for artifact in manifest["artifacts"]:
        rel = artifact["path"]
        if rel in manifest_paths:
            raise RuntimeError("Duplicate artifact path")
        manifest_paths.add(rel)
        path = ROOT / rel
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise RuntimeError(f"Unsafe artifact path: {rel}")
        data = path.read_bytes()
        if len(data) != artifact["bytes"] or sha256(data) != artifact["sha256"]:
            raise RuntimeError(f"Hash or length mismatch: {rel}")
        if artifact["kind"] == "tracked-patch":
            result = subprocess.run(
                ["git", "--no-pager", "apply", "--stat", str(path)],
                cwd=ROOT, capture_output=True, text=True,
            )
            if result.returncode:
                raise RuntimeError(f"Patch syntax validation failed: {rel}")
            entry = next(x for x in manifest["repositories"] if x["id"] == artifact["repo_id"])
            expected = {x["path"] for x in entry["tracked_changes"]}
            actual = {line[6:] for line in data.decode("utf-8").splitlines() if line.startswith("+++ b/")}
            if expected != actual:
                raise RuntimeError(f"Patch path allowlist mismatch: {rel}")
            stats.append({"path": rel, "exit_code": 0, "stat": result.stdout.strip()})
    allowed_admin = {
        "README.md", "manifest.json", "tools/capture.py", "tools/safety.py",
        "tools/verify.py", "verification.json",
    }
    files = []
    hits = []
    python_files = 0
    for path in sorted(ROOT.rglob("*")):
        if path.is_symlink():
            raise RuntimeError("Symlink in archive")
        if not path.is_file() or path.name == "verification.json":
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel not in manifest_paths and rel not in allowed_admin:
            raise RuntimeError(f"Unexpected archive file: {rel}")
        data = path.read_bytes()
        if b"\x00" in data:
            raise RuntimeError(f"Binary content refused: {rel}")
        text = data.decode("utf-8-sig")
        for hit in findings(text):
            hits.append({"path": rel, "rule": hit["rule"], "line": hit["line"]})
        if path.suffix == ".py":
            ast.parse(text, filename=rel)
            python_files += 1
        files.append({"path": rel, "bytes": len(data), "sha256": sha256(data)})
    if hits:
        # No matched values are printed or persisted.
        raise RuntimeError("Secret-pattern matches: " + json.dumps(hits))
    guards = {
        "continuation/stepfly/files/lab_instrument.py": [
            'os.environ.get("LAB_ATTEMPT_BUDGET", "0")',
            'os.environ.get("LAB_ALLOW_PROVIDER_CALLS") != "1"',
            "    BUDGET = 0",
        ],
        "continuation/stepfly/files/lab_run.py": [
            'os.environ.get("LAB_ATTEMPT_BUDGET", "0")',
            'raise SystemExit("Archived harness is disarmed;',
        ],
        "continuation/netaivideoanalyzer/files/src/ConsoleAOAI-Lab-VideoAnalyzer/Program.cs": [
            'Environment.GetEnvironmentVariable("LAB_ALLOW_PROVIDER_CALLS") != "1"',
            "|| approvedBudget <= 0",
        ],
        "continuation/ccv-lab/files/voicelive_probe.py": [
            'os.environ.get("VL_MAX_ATTEMPTS", "0")',
            'os.environ.get("LAB_ALLOW_PROVIDER_CALLS") != "1"',
            'raise SystemExit("Archived harness is disarmed;',
        ],
    }
    for rel, snippets in guards.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        if not all(snippet in text for snippet in snippets):
            raise RuntimeError(f"Missing static disarmed-harness guard: {rel}")
    result = {
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed",
        "manifest_counts": manifest["counts"],
        "patch_syntax": stats,
        "credential_scan": {
            "rules_tested": rules_tested, "files_scanned": len(files),
            "high_confidence_matches": 0, "matched_values_printed": False,
        },
        "python_ast_files_parsed": python_files,
        "provider_harness_guards_statically_checked": len(guards),
        "provider_code_imported_or_executed": False,
        "patches_applied_to_external_clones": False,
        "azure_or_inference_operations": 0,
        "file_hashes": files,
        "self_hash_note": "verification.json excludes itself from hashing; rerun verifier after any archive edit.",
    }
    output = json.dumps(result, indent=2) + "\n"
    if findings(output):
        raise RuntimeError("Verification metadata failed the value-suppressing scan")
    (ROOT / "verification.json").write_text(output, encoding="utf-8")
    print(json.dumps({
        "status": "passed", "counts": manifest["counts"], "files_hashed": len(files),
        "python_ast_files": python_files, "secret_pattern_matches": 0,
        "patch_stat_checks": len(stats), "static_disarmed_harnesses": len(guards),
    }, indent=2))


if __name__ == "__main__":
    main()
