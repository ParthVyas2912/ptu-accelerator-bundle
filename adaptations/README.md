# PTU bundle — external source adaptations

This archive preserves the **reviewed evaluation adaptations**, not entire
accelerator repositories. `manifest.json` records exact origins, pinned base
commits, dirty-path dispositions, source/artifact SHA-256 hashes, omissions,
license locations, and archive-only safety transformations.

## Scope and layout

| Archive directory | Preserved work |
|---|---|
| `first-pass/chatbot/` | Catalog validation; bounded ingestion; managed identity and container DNS adaptations; scenario names; nine evaluation Bicep sources |
| `first-pass/dkm/` | Retry-configuration opt-ins and helper classes; Docker context exclusions; AKS SKU parameter |
| `first-pass/modernize/` | Failed/placeholder migration handling and regression tests |
| `first-pass/macae/` | Structured WebSocket event serialization and regression tests |
| `continuation/stepfly/` | Model/executor configuration patch; `lab_instrument.py`, `lab_run.py`, `requirements.lab.txt` |
| `continuation/netaivideoanalyzer/` | `src/ConsoleAOAI-Lab-VideoAnalyzer/Program.cs` and its `.csproj` |
| `continuation/ccv-lab/` | Standalone `voicelive_probe.py`; this directory was **not a Git clone** |

CWYD, Content Processing, Conversation, and the remaining continuation clones
have origin/base metadata but no selected dirty source to copy. The continuation
MACAE clone is clean; the first-pass MACAE clone carries the patch, although both
have the same base SHA. Do not mistake them for duplicate dirty snapshots.

Within each adaptation directory:

- `tracked.patch`: combined staged/unstaged tracked changes against the recorded
  base. Only reviewed paths are included.
- `files/`: selected authored untracked source, preserving paths relative to its
  original clone. Unmodified copies retain their original bytes.
- `upstream/`: upstream license copies taken from the exact pinned commit.

`tools/capture.py` documents the reviewed allowlist and archive transformations.
It is an archival utility, not a deployment or model-execution script. It refuses
to overwrite an existing manifest.

## Reproduce the source tree safely

Work in **new, dedicated directories**. Do not apply patches to the original
evaluation clones or to a checkout containing other work.

1. Run the offline archive verification from the bundle root:

   ```powershell
   $env:PYTHONDONTWRITEBYTECODE = '1'
   python adaptations/tools/verify.py
   ```

2. Choose a Git-clone entry from `manifest.json`. Clone its `origin_exact` into
   a new destination and detach at its **full `base_sha` before applying**:

   ```powershell
   # Set these from the chosen manifest entry; do not use a current branch tip.
   git clone --no-checkout $origin $newCheckout
   git -C $newCheckout checkout --detach $baseSha
   git -C $newCheckout rev-parse HEAD
   ```

   Check each command's exit code before continuing, and confirm the printed SHA
   exactly matches the manifest. If the pinned commit was not fetched, fetch that
   commit from the recorded origin; do not substitute `main`.

3. If the entry has `patch`, use its absolute archive path:

   ```powershell
   git -C $newCheckout apply --stat $patchPath
   git -C $newCheckout apply --check $patchPath
   # Only after successful checks, in the NEW checkout:
   git -C $newCheckout apply $patchPath
   ```

4. Copy each explicitly listed `untracked_sources` file from `files/` to its
   original relative path in the new checkout. Create required parent
   directories; refuse to overwrite existing files. Do **not** copy `upstream/`
   into application source, and do not copy arbitrary directories.

5. Compare copied files to the manifest artifact hashes. Use the pinned
   upstream's dependency/build instructions for any later, separately approved
   build. This capture did not install packages, build applications, apply
   patches to external clones, or execute source tests that could call providers.

For `ccv-lab`, create a new standalone source directory and copy only
`files/voicelive_probe.py`. Its origin and base are intentionally `null`; the
manifest points to the related Call Center Voice accelerator's exact origin and
SHA rather than fabricating a Git history for the probe.

## Disarmed provider harnesses

**No inference or deployment was executed during this capture.** No commits,
pushes, Azure mutations, environment activation, or external clone edits were
performed. The archive does not grant permission to execute the preserved Bicep
templates, indexing scripts, agent-creation scripts, or application entry points.

The copied provider harnesses have explicit archive-only changes:

- StepFly defaults `LAB_ATTEMPT_BUDGET` to **0**, forces it to zero without
  `LAB_ALLOW_PROVIDER_CALLS`, and stops its runner before scheduler import unless
  both explicit opt-in and a positive budget are present.
- The video harness stops before media processing or credential creation unless
  explicit opt-in and a positive `LAB_ATTEMPT_BUDGET` are present.
- The voice probe defaults `VL_MAX_ATTEMPTS` to **0** and has the same independent
  opt-in requirement before starting a session.

Do not set the opt-in variable or positive budgets as part of source restoration.
The manifest records the original source hash, archived hash, and each change;
the external originals were left untouched. No historical inference output is
represented as newly reproduced.

These gates are **not** a new cross-process/provider retry-accounting system.
The video harness's historical single-call telemetry does not by itself account
for SDK transport retries; the voice probe counts sessions, not every provider
event. StepFly uses a shared counter file for its wrapper attempts. Review these
limitations and the existing bundle measurement contract before any future
separately approved execution. DKM's retry setting is not a model-call budget.

## Portability and intentional omissions

- Azure account endpoints, resource names, IDs, role IDs, regions, lab tags,
  scenario index names and image-registry names are retained as permitted
  **private-repository metadata**. They are not credentials and must be reviewed
  for a different environment. This archive is not suitable for publication
  without an additional metadata review.
- Two Chatbot Bicep files had a machine-specific client CIDR default removed.
  `clientCidr` is now a required parameter; no personal IP address is preserved
  in those copied sources. Hard-coded lab infrastructure references remain
  historical evidence, not an instruction to deploy.
- Local DKM `appsettings.Development.json`, `.env` variants, credential caches,
  user-secrets, machine configuration and virtual environments are omitted
  without reading their contents. Create new approved configuration separately.
- StepFly needs its upstream database/schema and suitable synthetic input before
  any later execution. Synthetic databases, memory state, ledgers, counters and
  logs are not part of this source capture. Use fresh paths for `LAB_LEDGER`,
  `LAB_COUNTER`, and output files. Its config patch retains the historical
  `gpt-4.1-mini` model choice and single-executor limit; it contains no key.
- The video project targets **.NET 8** and pins the **Windows** OpenCvSharp native
  runtime. It links `../PromptsHelper.cs` and `../VideosHelper.cs` from the pinned
  public upstream. Supply appropriate local media paths only for an approved
  future run; binary videos and generated frame directories are not copied.
- `ccv-lab` originally shared a directory with a Windows Python virtual
  environment. Only its authored probe is preserved. Its imports require
  `azure-identity` and `azure-ai-voicelive`; no dependency lock was present among
  the requested standalone source, and the original environment was not copied.
- All `node_modules`, Python caches, `.venv`, `bin`, `obj`, build output,
  synthetic media, and run telemetry are omitted. Ignored-file enumeration is
  not an exhaustive inventory. Parent bundle source/evidence is a separate scope.
- Other repositories, including protected SpecSuite and Planetary code, were
  not inspected beyond the user-authorized top-level directory-name inventory.
  Dirtiness alone was not treated as evidence of evaluation authorship.
  Unselected paths and reasons are recorded in the manifest; no unrelated
  tracked change was found within the reviewed tracked diffs.

## Attribution and license preservation

All 15 unique GitHub origins were independently confirmed public and MIT-licensed
through read-only repository metadata on **2026-09-13 UTC**. Exact recorded
origins are retained even where GitHub redirects an old repository name
(`document-generation-solution-accelerator` now resolves to
`content-generation-solution-accelerator`).

Patches and adapted excerpts derive from the Microsoft and Azure-Samples
repositories identified per entry. Their MIT notices are copied from the pinned
commits, including the nested Kernel Memory license for DKM. Keep those notices
with any redistribution and retain existing copyright headers.

The Call Center Voice notice is included as related accelerator attribution for
the standalone probe; it does not assert that the probe had its own upstream
Git history. Upstream license metadata does not independently determine ownership
or grant a new license for newly authored evaluation material.

## Verification scope

`tools/verify.py` checks all manifest hashes, parses each patch using read-only
`git apply --stat`, verifies its exact path allowlist, parses archived Python
source without importing it, and scans archive text for high-confidence
credential patterns. It records path/rule/line metadata only, never credential
values. `verification.json` records the latest successful verification and hashes
every archive file except itself.

Passing regex checks is not a guarantee that arbitrary content is secret-free.
The reviewed source allowlist, explicit omissions and manual diff review provide
additional controls. Patch syntax validation is not compilation or proof of
runtime correctness; applicability must be checked in a new pinned checkout.
