# Privacy-minimized evidence derivatives

The eight source files listed in `manifest.json` contained authentic tenant identity information during publication review. Their **original files remain unchanged in the local workspace and are excluded from Git**.

These copies are labeled derivatives, not byte-identical provider records. `scripts/export_reviewed_evidence.py` removes identity fields, email addresses, local user paths and IPv4 address strings. This deliberately broad process can also remove synthetic identity/address values; the original must be used for exact forensic reproduction.

The manifest records each original and derivative path, both SHA-256 hashes and replacement count. It does not contain the removed identities. Tests and reports elsewhere may refer to the original paths; use the corresponding derivative here for private-repository review.

This minimization is not permission to publish these files on the public website. No private evidence is an input to the website build.
