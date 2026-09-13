#!/usr/bin/env python3
"""Local, standard-library-only credential gate; never executes application code.

Usage:
    python scripts/check_publication.py --paths scripts infra tests
    python scripts/check_publication.py --staged
    git --no-pager ls-files -z | python scripts/check_publication.py --paths-from-stdin

--paths reads explicit files/directories without following symlinks. --staged
reads added/changed Git INDEX blobs, not working-tree contents. Git is invoked
without a shell, external diff, textconv, hooks, or network operations. This
program does not initialize a repository or create files.
Staged reads use bounded cat-file batches, verify each blob's Git object hash,
and fail if index entries or the staged path list change during the scan.

--paths-from-stdin reads NUL-terminated, current-directory-relative file paths
from binary stdin (run at the repository root for git ls-files). It preserves
spaces/non-ASCII characters, reads only the listed working-tree files, and never
recurses into listed directories. Absolute paths, parent traversal, .git paths,
links, malformed NUL lists and path lists over 16 MiB fail closed. Empty input is
valid; use Bash `set -o pipefail` so an upstream git failure also fails CI.
No mode applies .gitignore itself: ignored files already tracked by Git are still
listed by git ls-files. --staged remains the gate for actual staged contents.

Output is PATH:LINE:RULE only (LINE=0 for coverage/configuration errors).
Exit 0: no unsuppressed high-confidence matches in the selected text.
Exit 1: credential-pattern matches. Exit 2: incomplete scan/configuration error.
Binaries, symlinks, files over 16 MiB and undecodable text fail closed with exit
2; they need separate review. This is NOT a personal-data detector, a credential
validity check, or clearance for public release. Unknown/encoded credentials
may evade pattern matching. Review data minimization and privacy separately.
The exact placeholder "notsecret" is recognized; arbitrary descriptive prose
in secret-named fields still requires the narrow reviewed allowlist below.

Optional --allowlist FILE uses this exact, narrow JSON schema:
    {"version": 1, "entries": [{
        "path": "tests/example.py", "line": 42, "rule": "LITERAL_SECRET",
        "file_sha256": "<64 lowercase hex characters>",
        "reason": "Reviewed synthetic fixture; not a live credential"
    }]}
Paths must be exact, relative, slash-separated paths from the current directory
(repository root for --staged). No globs/directory/rule-wide suppressions.
The digest covers the ENTIRE raw file/blob, so any edit invalidates suppression,
including a changed multiline private key. Review allowlist changes as carefully
as credentials; never allowlist a real credential. Compute hashes locally with
hashlib or Get-FileHash. No automatic allowlist generation or value logging.
"""

import argparse
import base64
import collections
import hashlib
import html
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
from urllib.parse import unquote, urlsplit


MAX_BYTES = 16 * 1024 * 1024
MAX_BATCH_BYTES = 32 * 1024 * 1024
RULES = {
    "PRIVATE_KEY", "PROVIDER_TOKEN", "SIGNED_JWT", "BEARER_TOKEN",
    "BASIC_AUTH", "SAS_SIGNATURE", "CONNECTION_CREDENTIAL",
    "URL_PASSWORD", "LITERAL_SECRET",
}
PLACEHOLDERS = {
    "secret", "password", "password123", "password123!", "changeme",
    "change_me", "replace_me", "replace-me", "placeholder", "redacted",
    "dummy", "example", "sample", "test", "fake", "none", "null",
    "your-api-key", "your_api_key", "your-secret", "your_secret",
    "your-token", "your_token", "test-token", "test-secret", "test-password",
    "fake-token", "fake-secret", "not-a-real-token", "not-a-real-secret",
    "not-a-real-key", "not-a-real-password", "synthetic-token", "notsecret",
}
SECRET_NAME = (
    r"(?:(?:[A-Za-z][A-Za-z0-9]*[_-])*)"
    r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|"
    r"client[_-]?secret|client[_-]?secret[_-]?value|secret[_-]?access[_-]?key|"
    r"aws[_-]?secret[_-]?access[_-]?key|aws[_-]?session[_-]?token|"
    r"storage[_-]?(?:account[_-]?)?key|account[_-]?key|shared[_-]?access[_-]?key|"
    r"password|passwd|pwd|secret|token)"
)
QUOTED_SECRET = re.compile(
    r"""(?<![\w-])["']?(?P<name>""" + SECRET_NAME
    + r""")["']?\s*[:=]\s*(?P<quote>["'])(?P<value>[^"'\r\n]{1,4096})(?P=quote)""",
    re.I,
)
ENV_SECRET = re.compile(
    r"^\s*(?:export\s+)?(?P<name>" + SECRET_NAME
    + r")\s*=\s*(?![A-Za-z_][\w.]*\s*\()"
    r"(?P<value>[^\s;#\"']{1,4096})\s*(?:#.*)?$", re.I,
)
CONNECTION = re.compile(
    r"(?:^|[;\"'])\s*(?P<name>Password|Pwd|AccountKey|SharedAccessKey)\s*=\s*"
    r"(?P<value>[^;\r\n\"'<>]+)", re.I,
)
PROVIDER = re.compile(
    r"(?<![\w-])(?:gh[pousr]_[A-Za-z0-9]{36}|"
    r"github_pat_[A-Za-z0-9_]{50,}|"
    r"sk-(?:(?:proj|svcacct|ant-api03)-)?[A-Za-z0-9_-]{24,}|"
    r"xox[baprs]-[0-9]{8,}-[0-9]{8,}-[A-Za-z0-9]{16,})(?![\w-])"
)
JWT = re.compile(
    r"(?<![\w-])(eyJ[A-Za-z0-9_-]{8,}\."
    r"[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{20,})(?![\w-])"
)
PEM = re.compile(
    r"-----BEGIN (?:(?:RSA|EC|DSA|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
    r"\s+([A-Za-z0-9+/=\s]{64,})"
)
BEARER = re.compile(r"\bBearer\s+([A-Za-z0-9._~+/=-]{24,})", re.I)
BASIC = re.compile(r"\bBasic[ \t]+([A-Za-z0-9+/]{12,}={0,2})", re.I)
SAS = re.compile(r"(?:[?&]|^)sig=([^&\s\"'<>]+)", re.I)
SAS_CONTEXT = re.compile(r"(?:[?&]|^)(?:sv|sp|se|sr|ss|srt)=", re.I)
URL_PASSWORD = re.compile(
    r"\b(?:https?|postgres(?:ql)?|mysql|mariadb|mssql|mongodb(?:\+srv)?|"
    r"rediss?|amqps?)://[^/\s:@]+:([^/@\s]+)@", re.I,
)


class ScanError(Exception):
    def __init__(self, path, rule):
        self.path = str(path)
        self.rule = rule


def emit(path, line, rule):
    # Escape control characters and non-ASCII filenames; never emit file contents.
    safe_path = json.dumps(str(path), ensure_ascii=True)[1:-1]
    print(f"{safe_path}:{line}:{rule}")


def placeholder(value):
    value = unquote(value.strip())
    if value.lower() in PLACEHOLDERS or len(set(value.lower())) <= 1:
        return True
    return bool(re.fullmatch(
        r"(?:<[^<>]+>|\$\{[^{}]+\}|\$\([^()]+\)|\{\{[^{}]+\}\}|"
        r"\{[A-Za-z_][\w.]*\}|\$(?:env:)?[A-Za-z_][\w:]*)", value
    ))


def entropy(value):
    frequencies = collections.Counter(value)
    return -sum((n / len(value)) * math.log2(n / len(value))
                for n in frequencies.values()) if value else 0


def plausible_secret(value, password=False):
    if placeholder(value):
        return False
    if password:
        return len(value) >= 8 and not any(c.isspace() for c in value)
    return len(value) >= 24 and entropy(value) >= 3.5


def password_field(name):
    return bool(re.search(r"(?:^|[_-])(?:password|passwd|pwd)$", name, re.I))


def nonsecret_token_endpoint(name, value):
    """Azure discovery's Token endpoint is a URL, not an issued token."""
    if name.casefold() != "token" or any(char.isspace() for char in value):
        return False
    try:
        endpoint = urlsplit(value)
        host = endpoint.hostname or ""
        return (
            endpoint.scheme == "https"
            and endpoint.username is None and endpoint.password is None
            and endpoint.port in (None, 443)
            and endpoint.path in ("", "/")
            and not endpoint.query and not endpoint.fragment
            and (
                host.endswith(".cognitiveservices.azure.com")
                or host.endswith(".api.cognitive.microsoft.com")
                or host == "api.cognitive.microsoft.com"
            )
        )
    except ValueError:
        return False


def signed_jwt(value):
    try:
        header, payload, signature = value.split(".")
        decode = lambda part: base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
        header, payload = json.loads(decode(header)), json.loads(decode(payload))
        return (
            isinstance(header, dict) and isinstance(payload, dict)
            and isinstance(header.get("alg"), str)
            and header["alg"].lower() != "none"
            and bool({"exp", "iat", "iss", "aud", "sub"} & payload.keys())
            and len(decode(signature)) >= 16
        )
    except (ValueError, TypeError, UnicodeError):
        return False


def findings(text):
    results = set()
    for match in PEM.finditer(text):
        body = re.sub(r"\s", "", match.group(1))
        if len(body) >= 64 and entropy(body) >= 3.0:
            results.add((text.count("\n", 0, match.start()) + 1, "PRIVATE_KEY"))
    for number, original in enumerate(text.splitlines(), 1):
        line = html.unescape(original)
        if any(plausible_secret(m.group()) for m in PROVIDER.finditer(line)):
            results.add((number, "PROVIDER_TOKEN"))
        if any(signed_jwt(m.group(1)) for m in JWT.finditer(line)):
            results.add((number, "SIGNED_JWT"))
        if any(plausible_secret(m.group(1)) for m in BEARER.finditer(line)):
            results.add((number, "BEARER_TOKEN"))
        for match in BASIC.finditer(line):
            try:
                decoded = base64.b64decode(match.group(1), validate=True).decode("utf-8")
                username, separator, password = decoded.partition(":")
                if username and separator and plausible_secret(password, password=True):
                    results.add((number, "BASIC_AUTH"))
            except (ValueError, UnicodeError):
                pass
        if SAS_CONTEXT.search(line):
            for match in SAS.finditer(line):
                if plausible_secret(unquote(match.group(1))):
                    results.add((number, "SAS_SIGNATURE"))
        for match in CONNECTION.finditer(line):
            is_password = match.group("name").lower() in {"password", "pwd"}
            if plausible_secret(match.group("value").strip(), password=is_password):
                results.add((number, "CONNECTION_CREDENTIAL"))
        for match in URL_PASSWORD.finditer(line):
            if plausible_secret(unquote(match.group(1)), password=True):
                results.add((number, "URL_PASSWORD"))
        named = list(QUOTED_SECRET.finditer(line))
        env_match = ENV_SECRET.fullmatch(line)
        if env_match:
            named.append(env_match)
        for match in named:
            if nonsecret_token_endpoint(match.group("name"), match.group("value")):
                continue
            is_password = password_field(match.group("name"))
            if plausible_secret(match.group("value"), password=is_password):
                results.add((number, "LITERAL_SECRET"))
    return sorted(results)


def decode_text(path, data):
    try:
        if data.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
            text = data.decode("utf-32")
        elif data.startswith((b"\xff\xfe", b"\xfe\xff")):
            text = data.decode("utf-16")
        else:
            text = data.decode("utf-8-sig")
        if "\x00" in text or any(ord(c) < 32 and c not in "\t\r\n\f" for c in text):
            raise ScanError(path, "UNREVIEWED_BINARY")
        return text
    except UnicodeError:
        raise ScanError(path, "UNDECODABLE_TEXT") from None


def relative_path(path, root):
    return Path(os.path.relpath(path, root)).as_posix()


def read_regular(path, label):
    try:
        mode = path.lstat().st_mode
        if path.is_symlink() or not stat.S_ISREG(mode):
            raise ScanError(label, "UNREVIEWED_NONREGULAR_FILE")
        if path.stat().st_size > MAX_BYTES:
            raise ScanError(label, "FILE_TOO_LARGE")
        with path.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ScanError(label, "FILE_TOO_LARGE")
        return data
    except OSError:
        raise ScanError(label, "READ_ERROR") from None


def walk_explicit(path, root):
    label = relative_path(path, root)
    # Avoid Windows junctions as well as symlinks and special files.
    try:
        info = path.lstat()
        if (stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & 0x400):
            raise ScanError(label, "UNREVIEWED_LINK")
        if stat.S_ISDIR(info.st_mode):
            for child in sorted(path.iterdir(), key=lambda item: item.name):
                if child.name == ".git":
                    continue
                yield from walk_explicit(child, root)
        else:
            yield label, read_regular(path, label)
    except OSError:
        raise ScanError(label, "READ_ERROR") from None


def stdin_files(root):
    raw_paths = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(raw_paths) > MAX_BYTES:
        raise ScanError("--paths-from-stdin", "STDIN_PATH_LIST_TOO_LARGE")
    if not raw_paths:
        return
    if not raw_paths.endswith(b"\0") or any(not name for name in raw_paths[:-1].split(b"\0")):
        raise ScanError("--paths-from-stdin", "INVALID_NUL_PATH_LIST")
    for raw_name in raw_paths[:-1].split(b"\0"):
        path = Path(os.fsdecode(raw_name))
        if path.anchor or not path.parts or any(part in {"..", ".git"} for part in path.parts):
            raise ScanError("--paths-from-stdin", "INVALID_STDIN_PATH")
        label = path.as_posix()
        target = root
        try:
            # Check each component before descending through a possible link.
            for part in path.parts:
                target = target / part
                info = target.lstat()
                if (stat.S_ISLNK(info.st_mode)
                        or getattr(info, "st_file_attributes", 0) & 0x400):
                    raise ScanError(label, "UNREVIEWED_LINK")
            yield label, read_regular(target, label)
        except OSError:
            raise ScanError(label, "READ_ERROR") from None


def git_bytes(root, *args, input_data=None):
    try:
        environment = os.environ.copy()
        environment.update({
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0",
        })
        result = subprocess.run(
            ["git", "--no-pager", "--no-replace-objects", "--literal-pathspecs",
             "-C", str(root), *args],
            input=input_data, env=environment,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            timeout=60,
        )
        if result.returncode:
            raise ScanError("--staged", "GIT_READ_ERROR")
        return result.stdout
    except (OSError, subprocess.TimeoutExpired):
        raise ScanError("--staged", "GIT_READ_ERROR") from None


def nul_records(data):
    if not data:
        return []
    if not data.endswith(b"\0") or any(not entry for entry in data[:-1].split(b"\0")):
        raise ScanError("--staged", "INVALID_GIT_PATH_LIST")
    return data[:-1].split(b"\0")


def staged_snapshot(root):
    entries = git_bytes(root, "ls-files", "--stage", "-z", "--")
    # Disable rename detection: a rename's new path is scanned as an addition.
    names = git_bytes(
        root, "diff", "--cached", "--name-only", "--diff-filter=ACMRTU",
        "--no-renames", "--no-ext-diff", "--no-textconv", "-z", "--",
    )
    return entries, names


def batch_blobs(root, object_ids, sizes):
    """Read one size-bounded batch; validate framing, type, size, and content."""
    data = git_bytes(root, "cat-file", "--batch", input_data=b"\n".join(object_ids) + b"\n")
    offset = 0
    for object_id in object_ids:
        size = sizes[object_id]
        header = object_id + b" blob " + str(size).encode("ascii") + b"\n"
        if data[offset:offset + len(header)] != header:
            raise ScanError("--staged", "INVALID_GIT_BATCH_HEADER")
        start = offset + len(header)
        end = start + size
        if len(data) < end + 1 or data[end:end + 1] != b"\n":
            raise ScanError("--staged", "INVALID_GIT_BATCH_BODY")
        body = data[start:end]
        digest = hashlib.new("sha1" if len(object_id) == 40 else "sha256")
        digest.update(b"blob " + str(size).encode("ascii") + b"\0")
        digest.update(body)
        if digest.hexdigest().encode("ascii") != object_id:
            raise ScanError("--staged", "GIT_BLOB_HASH_MISMATCH")
        offset = end + 1
        yield object_id, body
    if offset != len(data):
        raise ScanError("--staged", "INVALID_GIT_BATCH_TRAILER")


def staged_files(root):
    before = staged_snapshot(root)
    index = {}
    for entry in nul_records(before[0]):
        try:
            metadata, name = entry.split(b"\t", 1)
            mode, object_id, stage = metadata.split()
        except ValueError:
            raise ScanError("--staged", "INVALID_GIT_INDEX_METADATA") from None
        index.setdefault(name, []).append((mode, object_id, stage))
    names = nul_records(before[1])
    if len(names) != len(set(names)):
        raise ScanError("--staged", "INVALID_GIT_PATH_LIST")
    paths_by_object = {}
    for name in names:
        records = index.get(name, [])
        if len(records) != 1:
            raise ScanError(os.fsdecode(name), "UNREVIEWED_INDEX_ENTRY")
        mode, object_id, stage = records[0]
        if (mode not in {b"100644", b"100755"} or stage != b"0"
                or not re.fullmatch(rb"(?:[0-9a-f]{40}|[0-9a-f]{64})", object_id)):
            raise ScanError(os.fsdecode(name), "UNREVIEWED_INDEX_ENTRY")
        paths_by_object.setdefault(object_id, []).append(os.fsdecode(name))
    if paths_by_object:
        object_ids = list(paths_by_object)
        metadata = git_bytes(
            root, "cat-file", "--batch-check",
            input_data=b"\n".join(object_ids) + b"\n",
        ).splitlines()
        if len(metadata) != len(object_ids):
            raise ScanError("--staged", "INVALID_GIT_BATCH_METADATA")
        sizes = {}
        for object_id, record in zip(object_ids, metadata):
            fields = record.split()
            if (len(fields) != 3 or fields[0] != object_id or fields[1] != b"blob"
                    or not re.fullmatch(rb"[0-9]+", fields[2])):
                raise ScanError("--staged", "INVALID_GIT_BATCH_METADATA")
            size = int(fields[2])
            if size > MAX_BYTES:
                raise ScanError(paths_by_object[object_id][0], "FILE_TOO_LARGE")
            sizes[object_id] = size
        group = []
        group_bytes = 0
        for object_id in object_ids:
            cost = sizes[object_id] + len(object_id) + 32
            if group and group_bytes + cost > MAX_BATCH_BYTES:
                for oid, body in batch_blobs(root, group, sizes):
                    for name in paths_by_object[oid]:
                        yield name, body
                group = []
                group_bytes = 0
            group.append(object_id)
            group_bytes += cost
        if group:
            for oid, body in batch_blobs(root, group, sizes):
                for name in paths_by_object[oid]:
                    yield name, body
    if staged_snapshot(root) != before:
        raise ScanError("--staged", "GIT_INDEX_CHANGED_DURING_SCAN")


def load_allowlist(path):
    if path is None:
        return set()
    try:
        document = json.loads(read_regular(Path(path), path).decode("utf-8-sig"))
        if set(document) != {"version", "entries"} or document["version"] != 1:
            raise ValueError()
        if not isinstance(document["entries"], list):
            raise ValueError()
        allowed = set()
        for entry in document["entries"]:
            if set(entry) != {"path", "line", "rule", "file_sha256", "reason"}:
                raise ValueError()
            name = entry["path"]
            if not isinstance(name, str) or not name:
                raise ValueError()
            if (PurePosixPath(name).is_absolute() or "\\" in name or ":" in name
                    or any(part in {"", ".", ".."} for part in name.split("/"))
                    or any(char in name for char in "*?[]")):
                raise ValueError()
            if type(entry["line"]) is not int or entry["line"] < 1:
                raise ValueError()
            if entry["rule"] not in RULES:
                raise ValueError()
            if not re.fullmatch(r"[0-9a-f]{64}", entry["file_sha256"]):
                raise ValueError()
            if not isinstance(entry["reason"], str) or not entry["reason"].strip():
                raise ValueError()
            allowed.add((name, entry["line"], entry["rule"], entry["file_sha256"]))
        return allowed
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise ScanError(path, "INVALID_ALLOWLIST") from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--paths", nargs="+", metavar="PATH")
    mode.add_argument("--paths-from-stdin", action="store_true")
    parser.add_argument("--allowlist", metavar="FILE")
    args = parser.parse_args(argv)
    found = False
    incomplete = False
    try:
        allowlist = load_allowlist(args.allowlist)
        root = Path.cwd()
        if args.staged:
            root = Path(os.fsdecode(git_bytes(root, "rev-parse", "--show-toplevel")).strip())
            sources = [staged_files(root)]
        elif args.paths_from_stdin:
            sources = [stdin_files(root)]
        else:
            sources = [walk_explicit(Path(os.path.abspath(path)), root) for path in args.paths]
        seen = set()
        for source in sources:
            try:
                for name, data in source:
                    if name in seen:
                        continue
                    seen.add(name)
                    try:
                        text = decode_text(name, data)
                        digest = hashlib.sha256(data).hexdigest()
                        for line, rule in findings(text):
                            if (name, line, rule, digest) not in allowlist:
                                emit(name, line, rule)
                                found = True
                    except ScanError as error:
                        emit(error.path, 0, error.rule)
                        incomplete = True
            except ScanError as error:
                emit(error.path, 0, error.rule)
                incomplete = True
    except ScanError as error:
        emit(error.path, 0, error.rule)
        incomplete = True
    except (OSError, ValueError, UnicodeError):
        selected_mode = "--staged" if args.staged else "--paths-from-stdin" if args.paths_from_stdin else "--paths"
        emit(selected_mode, 0, "SCAN_ERROR")
        incomplete = True
    return 2 if incomplete else 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
