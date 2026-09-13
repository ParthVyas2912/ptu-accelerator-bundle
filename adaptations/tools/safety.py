"""Offline, value-suppressing checks for the scoped adaptation archive.

This is a conservative credential-pattern scan, not a guarantee that arbitrary
content is safe. Capture is additionally restricted to reviewed source paths.
"""

import re


PATTERNS = {
    "private-key": re.compile(
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"
        r"[\s\S]*?-----END (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"
    ),
    "github-token": re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b"
    ),
    "provider-token": re.compile(
        r"\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}"
        r"|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[A-Z0-9]{16})\b"
    ),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{16,}\b"),
    "connection-credential": re.compile(
        r"(?i)\b(?:AccountKey|SharedAccessKey|Password|Pwd)\s*=\s*"
        r"([A-Za-z0-9/+_.!%=-]{12,})(?=;|[\"'\s]|$)"
    ),
    "sas-signature": re.compile(
        r"(?i)(?:[?&]|&amp;)sig=([A-Za-z0-9/%+_-]{24,}={0,2})"
    ),
    "url-password": re.compile(r"(?i)\bhttps?://[^/\s:@]+:([^/\s@]{6,})@"),
    "literal-secret": re.compile(
        r"""(?ix)
        ["']?(?:[a-z0-9_]*(?:api_?key|access_?key|account_?key|client_?secret
        |subscription_?key|password|access_?token|refresh_?token))["']?
        \s*[:=]\s*["']([A-Za-z0-9/+_.!%=-]{16,})["']
        """
    ),
    "literal-connection-string": re.compile(
        r"""(?i)["']((?:DefaultEndpointsProtocol|Server|Data Source|AccountEndpoint|
        Endpoint)\s*=[^"'\r\n]*(?:AccountKey|SharedAccessKey|Password|Pwd)\s*=
        [^"'\r\n]+)["']""".replace("\n", "").replace("        ", "")
    ),
}


def findings(text):
    """Return rule and location metadata only; never return credential values."""
    result = []
    for name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            value = match.group(match.lastindex or 0)
            if any(marker in value.lower() for marker in (
                "placeholder", "redacted", "your_", "your-", "example", "changeme",
            )):
                continue
            result.append({
                "rule": name,
                "line": text.count("\n", 0, match.start()) + 1,
                "start": match.start(),
                "end": match.end(),
            })
    return result


def safe_preview(text):
    """Suppress entire suspect lines before any inspection output."""
    blocked = set()
    for item in findings(text):
        first = item["line"]
        last = first + text[item["start"]:item["end"]].count("\n")
        blocked.update(range(first, last + 1))
    return "\n".join(
        "[REDACTED: credential-pattern match]" if number in blocked else line
        for number, line in enumerate(text.splitlines(), 1)
    )
