# Contributing

## Small, reviewable changes

Use a branch and pull request. Describe the business outcome, evidence, tested scope, limitations and operating cost. Do not describe a planned feature as deployed or equate HTTP success with task success.

Keep these layers separate:

1. **Private evidence and engineering:** evaluation records, environment-specific scripts, traces and reports.
2. **Public stakeholder content:** curated, non-sensitive explanations in `site/`.
3. **Operations:** explicit deployment and inference permissions; never implied by a code change.

## Before opening a pull request

- Build and test the website when changing it.
- Run `python scripts/check_publication.py --staged --allowlist scripts/publication_allowlist.json` after staging changes.
- Verify there are no credentials, original internal briefing inputs, local environment files or dependency/build caches.
- Public site content must not contain tenant/subscription/resource identifiers, private URLs, personal contact information or unapproved customer stories.
- Update provenance and retain upstream licenses for accelerator patches.
- Do not reset historical attempt budgets or automatically execute old lab scripts.

## Public publishing

The repository is private, but website deployments are public. A maintainer must review public content as publication, not just code. The deploy workflow uploads only `site/dist`, never the repository root.

Pull requests run validation only. Production deployment runs only from `main` or an authorized manual workflow. No fork or pull-request deployment gets the production deployment credential.

## Reporting a suspected credential

Do not put the value in an issue, pull request or screenshot. Stop publication, notify the owner privately and rotate/revoke the credential through the owning system. Deleting it from a later commit is not sufficient if it reached Git history.
