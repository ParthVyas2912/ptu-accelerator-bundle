"""Export labeled, privacy-minimized copies without changing original evidence."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    r"continuation-preflight\ai-accounts.json",
    r"continuation-preflight\resource-groups.json",
    r"cwyd\model-calls.json",
    r"cwyd\result.json",
    r"preflight\account.json",
    r"preflight\eastus2-models.json",
    r"preflight\lab-client-address-verified.json",
    r"preflight\resource-groups.json",
)
IDENTITY_KEYS = {
    "user", "caller", "createdby", "lastmodifiedby", "modifiedby",
    "username", "userprincipalname", "preferred_username", "unique_name",
    "given_name", "family_name", "email", "emailaddress", "upn",
    "ipaddress", "clientip", "clientipaddress", "clientaddress",
}
EMAIL = re.compile(r"[\w.!#$%&'*+/=?^`{|}~-]+@[\w.-]+\.[A-Za-z]{2,}")
USER_PATH = re.compile(r"(?i)C:[\\/]+Users[\\/]+[^\\/]+")
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?(?![\w.])")


def minimize(value, changes):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key.lower() in IDENTITY_KEYS and item is not None:
                result[key] = "[REDACTED IDENTITY]"
                changes[0] += 1
            else:
                result[key] = minimize(item, changes)
        return result
    if isinstance(value, list):
        return [minimize(item, changes) for item in value]
    if isinstance(value, str):
        for pattern, replacement in (
            (EMAIL, "[REDACTED EMAIL]"),
            (USER_PATH, r"C:\\Users\\[REDACTED]"),
            (IPV4, "[REDACTED ADDRESS]"),
        ):
            value, count = pattern.subn(lambda _: replacement, value)
            changes[0] += count
        return value
    return value


def main():
    output = ROOT / "evidence" / "portable"
    entries = []
    for name in SOURCES:
        relative = Path(*name.split("\\"))
        source = ROOT / "evidence" / relative
        data = source.read_bytes()
        changes = [0]
        cleaned = minimize(json.loads(data.decode("utf-8-sig")), changes)
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        derivative = (json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        destination.write_bytes(derivative)
        entries.append({
            "originalLocalPath": "evidence\\" + name,
            "derivativePath": "evidence\\portable\\" + name,
            "originalSha256": hashlib.sha256(data).hexdigest(),
            "derivativeSha256": hashlib.sha256(derivative).hexdigest(),
            "replacements": changes[0],
        })
        assert not EMAIL.search(derivative.decode("utf-8")), name
    manifest = {
        "kind": "privacy-minimized derivatives, not original provider evidence",
        "method": "Remove identity fields, email addresses, local user paths and IPv4 strings.",
        "warning": "Broad minimization can remove synthetic identity/address values too. "
                   "Use original local evidence for exact forensic reproduction.",
        "originalsModified": False,
        "files": entries,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(entries)} labeled derivatives; original files unchanged.")


if __name__ == "__main__":
    main()
