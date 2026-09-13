# Private repository / public website boundary

## Private does not mean secret storage

The GitHub repository is intended to preserve reusable engineering work, reviewed reports, synthetic fixtures, bounded-test evidence and upstream adaptations. Environment identifiers may appear in private operational records; these records must never be bundled into the public site.

Do not commit:

- Tokens, API keys, passwords, SAS signatures, private keys or credential caches.
- Original internal research/playbook/continuation source documents.
- Authentic customer or personnel data.
- Virtual environments, dependency directories, build caches or local machine state.

Generated Word exports and original input PDFs remain local. The initial source of record in Git is the Markdown reports, with historical qualifications preserved. Operational `.log` files are excluded by default; preserve a reviewed diagnostic extract or structured result instead when needed.

The initial text review found no confirmed credentials, but eight records contained authentic tenant identity information. Their originals are excluded and preserved locally; labeled privacy-minimized copies and hash provenance are in `evidence/portable/`. These are derivatives, not silently altered original results. Unreviewed binary screenshots and fixtures, generated ARM output and machine-local build-context records are also excluded. Useful reviewed evidence is retained rather than blanket-excluding the evidence tree.

## Public site

Only curated content authored under `site/` is eligible for publication. Its generated `site/dist` directory must contain only the website artifact and static hosting configuration/assets.

Public content may include:

- The proposed business outcomes, portfolio names and public Microsoft documentation.
- Honest, generalized evidence status, without private trace identifiers or environment details.
- Planned workflows clearly marked as planned.
- A link to the private repository labeled as contributor access.

Public content must not include:

- Reports, raw evidence, original research inputs or private deployment configuration.
- Subscription/tenant/resource IDs, account endpoints, internal hostnames or local paths.
- Personal contact information, internal owners, customer success claims without publication approval.
- Credentials, APIs that trigger paid operations, live environment administration or upload features.

## Verification

The staged-file publication scanner checks for high-confidence credential patterns without printing matched values. It is a guardrail, not a certification that all possible confidential content has been detected. Human review and the separate public-content tests remain necessary.

`scripts/publication_allowlist.json` contains one reviewed, credential-free deployment-description annotation at a fixed path/line/rule, bound to the complete file SHA-256 (both historical line-ending representations). This is not a wildcard exception for secret fields. Changed content must be reviewed again.

All private report artifacts retain their evidence limitations. Sanitization or omission must be documented rather than silently rewriting an original response to appear successful.

Git line-ending normalization is disabled for `adaptations/`, `evidence/` and `test-data/` so that captured hashes and fixture bytes survive Windows/Linux checkouts. Ordinary application and documentation source retains conventional text normalization.
