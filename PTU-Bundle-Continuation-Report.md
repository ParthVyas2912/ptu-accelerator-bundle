# MCAPS PTU Accelerator Bundle — Continuation Evaluation Report (Solutions 1–10)

**Report ID:** PTU-BUNDLE-CONT-2026-09-12
**Prepared:** 2026-09-12 (UTC)
**Instruction source:** `continuation\mcaps_ptu_bundle_10_app_continuation_review_20260912_172447.docx`
**Subscription:** `1feb53b2-854a-4ea7-b5a6-709b7d804f70` (ME-MngEnvMCAP687593-partvyas-1)
**Tenant:** `a600acd0-…` — non-production MCAPS lab
**Scope:** The 10 remaining portfolio ideas in the continuation instruction set.

---

## 0. How to read this report

This report separates three very different things that are frequently conflated in
accelerator evaluations:

| Class | Meaning | Confidence |
|---|---|---|
| **VERIFIED** | I executed it in this subscription and captured provider-level telemetry. | High — reproducible from `evidence/` |
| **INSPECTED** | I read the shipped source, templates, and docs and compiled the template where possible, but did not deploy or execute the business workflow. | Medium — claims are about the code, not about outcomes |
| **BLOCKED** | An approval gate, licence, provider registration, or third-party tenant stopped the work. Nothing is asserted beyond the gate. | Stated as a gate, not a verdict |

**Deployment success is not business success.** Where a template provisions cleanly
but the business outcome was never exercised, this report says so explicitly.

---

## 1. Executive summary

Ten solutions were carried through preflight, repository inspection, and bounded
validation. **Two** were validated functionally against live Azure model endpoints.
**Five** were inspected at source/template level with no-cost compilation or offline
conformance checks. **Three** are hard-blocked on approvals outside my authority.

### 1.1 The single most important finding

> **There is no provisioned throughput anywhere in this subscription.**
> All 25 model deployments across 13 Cognitive Services accounts are
> `GlobalStandard` (17) or `Standard` (8). **Zero** are `ProvisionedManaged`.

Evidence: `evidence/continuation-preflight/deployment-sku-audit.json`

Consequence: every latency, throughput, and concurrency number produced in this
lab — in this pass **and** in the previous pass — was measured on pay-as-you-go
shared capacity. These numbers characterise *token shape* and *workload
behaviour*, which do transfer to PTU sizing. They do **not** characterise
PTU latency, PTU burst behaviour, or PTU saturation, which cannot be inferred
from Standard measurements. Any PTU sizing recommendation built on this bundle
must be labelled as a token-shape extrapolation, not a measured PTU result.

### 1.2 Portfolio verdicts

| # | Solution | Track | Status | Ran real model calls? |
|---|---|---|---|---|
| 1 | Contract / RFP Reviewer (MACAE packs) | Configuration | INSPECTED — conformance defects found | No |
| 2A | Employee Self-Service (MACAE `hr_onboarding`) | Configuration | INSPECTED — conformance defects found | No |
| 2B | Employee Self-Service Developer Kit | Owner / Enablement | BLOCKED — 4 admin roles + Workday tenant | No |
| 3 | "Document Generation" | Deployable accelerator | INSPECTED — **scope mismatch**, template compiles | No |
| 4 | Multimodal Video / Media Analysis | Deployable sample | **VERIFIED** — 6-test suite, 1 content-filter block | **Yes** |
| 5 | Incident & Troubleshooting Agent (StepFly) | Research prototype | **VERIFIED** — 20-attempt budget, 2 defects found | **Yes** |
| 6 | Call Center Voice Agent | Deployable accelerator | **PARTIALLY VERIFIED** — Voice Live session proven; telephony blocked | **Yes** |
| 7 | Private-Tenant AI Chat / Production AI App | Platform / landing zone | INSPECTED — compiles clean; Fabric + cost gates | No |
| 8 | Unified Data Foundation (Fabric UDF) | Platform | BLOCKED — Fabric provider NotRegistered | No |
| 9 | Real-Time Operational Intelligence (Fabric RTOI) | Platform | BLOCKED — Fabric licence + capacity + UAA | No |
| 10 | Harbinger | Owner validation only | BLOCKED — no locatable package | No |

### 1.3 Defects and conflicts found

Six findings that a reader should act on, all reproducible from `evidence/`:

1. **StepFly dependency graph is internally inconsistent** — `requirements.txt` cannot resolve as pinned.
2. **StepFly hangs forever on Windows** due to an unguarded Unicode `print()`; no error is surfaced.
3. **MACAE shipped content packs violate MACAE's own authoring contract** — 6 of 7 packs.
4. **"Document generation" accelerator no longer generates documents** — the GitHub repo 301-redirects to a *marketing content generation* accelerator.
5. **The video accelerator's own bundled sample video is rejected by Azure content safety.**
6. **Call Center Voice does not consume Azure OpenAI PTU at all** — it runs on the Speech/Voice Live model plane.

---

## 2. Preflight and environment

### 2.1 Tooling

| Tool | Version | Note |
|---|---|---|
| Azure CLI | 2.84.0 | OK |
| azd | 1.23.7 | Behind current 1.34.0; satisfies repo floors (`>=1.15.0`, `>=1.18.0 != 1.23.9`) |
| Bicep CLI | 0.44.1 | Above the `>=0.33.0` floor required by solution 7 |
| Python | 3.11.9 | OK |
| Node.js | 24.15.0 | OK |
| .NET SDK | 10.0.303 | Builds the `net8.0` video sample |
| Docker | 29.6.2 | Daemon required manual start |
| Azure Functions Core Tools | 4.9.0 | OK |
| `uv` | **absent** | Required by the Call Center Voice local-dev path |
| `mongod` (local) | **absent** | Worked around with a container for StepFly |

### 2.2 Model inventory

25 deployments / 13 accounts. Relevant facts:

- **0 provisioned (PTU) deployments** — see §1.1.
- **0 image-generation deployments** (`gpt-image-1-mini`, `gpt-image-1.5`) anywhere.
  This directly blocks solution 3's differentiating capability.
- Models actually usable for this pass: `gpt-4.1-mini`, `gpt-5.1`, `gpt-5.4`,
  `gpt-5.4-mini`, `gpt-5-mini`, `gpt-5.2`, `gpt-4o`, plus embeddings.

### 2.3 Authentication pattern established

Keyless Entra auth was proven against the OpenAI-compatible surface and reused
throughout:

```
OpenAI(base_url="https://<account>.openai.azure.com/openai/v1/",
       api_key=<token for https://cognitiveservices.azure.com>)
```

No API key was printed, persisted, or written to any evidence file in this pass.

### 2.4 Provenance

All nine public repositories were cloned, pinned by full SHA, and secret-scanned.
Provenance: `evidence/continuation-preflight/repo-provenance.json`.
Scan: `evidence/continuation-preflight/repo-inspection-scan.json` — every hit was a
test fixture or documentation placeholder; **no live credentials were found**.

| Repo | SHA | Tag |
|---|---|---|
| macae | `8ac703a71f10` | v5.0.0 |
| document-generation → content-generation | `fa956c9ec374` | v2.7.1 |
| unified-data-foundation | `28c25024e438` | v1.25.4 |
| real-time-ops | `cfbdb91ee83e` | v1.3.5 |
| private-tenant-chat | `1ed62d982f77` | v1.5.3 |
| call-center-voice | `162cef590787` | — |
| ess-devkit | `3236a513b731` | — |
| stepfly | `a6229192a69d` | — |
| netaivideoanalyzer | `1d8ed2ece3ee` | `2024-11-09` (commit 2025-05-07 — stale) |

---

## 3. Solution 5 — Incident & Troubleshooting Agent (StepFly)

**Track:** research prototype · **Status: VERIFIED** · **Attempts used: 20 / 20**

This received the deepest validation because it was the only solution in the set
that could be driven end-to-end locally against a live model without provisioning
Azure infrastructure.

### 3.1 Ground truth

A 57 MB synthetic SQLite telemetry database was generated by the repo's own
generator. The planted ground truth was:

- Failing workflow: `payment_processing`
- Failure rate: 45 % at stage `payment_authorization`
- **Discoverable only at DAG Step 9**
- Deliberate decoys at Steps 2 and 3 (a fake regression, and feature flags below threshold)

### 3.2 Defects found

**Defect 1 — unresolvable dependency pins (blocks install).**

| Package | Pinned | Requires | Conflict |
|---|---|---|---|
| `httpcore` | 1.0.7 | `h11<0.15` | repo pins `h11==0.16.0` |
| `python-socketio` | 5.14.0 | `python-engineio>=4.11` | repo pins `python-engineio==4.8.2` |

Resolved locally with `h11==0.14.0`, `python-engineio==4.11.2`
(`repo/continuation/stepfly/requirements.lab.txt`).

**Defect 2 — silent infinite hang on Windows (blocks execution).**

`stepfly/tools/schedule_tool.py:94` emits `U+2713` via a plain `print()`. Under the
Windows console default `cp1252` this raises `UnicodeEncodeError` inside the
monitoring thread. The thread dies; the parent sits in `while self.running:
time.sleep(30)` forever. **No error is printed and the process never exits.**

Evidence: `evidence/stepfly/raw-responses/console-sf03-unicode-defect.log`.
Workaround: `PYTHONIOENCODING=utf-8`.

This is a genuine production-relevant defect: an agent framework that hangs
silently instead of failing loudly is worse than one that crashes.

### 3.3 Instrumentation problem worth recording

StepFly spawns Executors as `multiprocessing.Process` with the `spawn` start
method. `spawn` re-imports `__main__`, which re-ran my instrumentation with a
**fresh in-process counter** — so my first attempt budget was not global.
I rewrote it as an `O_CREAT|O_EXCL` file-locked on-disk counter
(`stepfly/lab_instrument.py`).

**Disclosure:** 6 of the 20 attempts were consumed discovering the two defects
above and this instrumentation flaw (aborted runs sf01, sf02, sf03). I kept a
single global counter so the solution total is exactly 20 rather than resetting
per run. Only 14 attempts therefore went to the business task.

### 3.4 Result (run sf04)

| DAG step | Expected | Actual | Verdict |
|---|---|---|---|
| 1 | Scope the incident | Completed | PASS |
| 2 | Regression hypothesis (decoy) | **Rejected** — `NO_REGRESSION` | PASS — correctly resisted the decoy |
| 3 | Feature-flag hypothesis (decoy) | **Rejected** — no flag over threshold | PASS — correctly resisted the decoy |
| 4–6 | Narrowing steps | Completed | PASS |
| 7 | Narrowing | Reached; budget guard fired | STOPPED |
| 8 | Narrowing | Not reached | NOT COMPLETED |
| 9 | **Identify `payment_authorization` root cause** | **Not reached** | **NOT COMPLETED** |

**The root cause was not found.** Reaching Step 9 needed an estimated 4–6 further
provider attempts. I chose to honour the 20-attempt budget rather than extend it.
It is therefore **unknown** whether StepFly would have identified the planted root
cause. This report does not claim that it would.

The positive result is nonetheless meaningful: the agent **rejected both planted
decoys**. A weaker agent would have declared the fake regression the root cause at
Step 2 and stopped. Correct negative reasoning is harder than correct positive
reasoning, and it was demonstrated.

### 3.5 Measurement — the PTU-relevant part

| Metric | Value |
|---|---|
| Provider attempts | 20 |
| HTTP 200 | 20 / 20 (no 429, no 5xx) |
| Served model | `gpt-4.1-mini-2025-04-14` |
| Prompt tokens | 249,144 |
| **Cached prompt tokens** | **178,944 (71.8 %)** |
| Completion tokens | 3,677 |
| Input : output ratio | **≈ 68 : 1** |
| Mean latency | 2.58 s |
| Max latency | 4.37 s |

**Interpretation for PTU sizing.** This workload is extremely input-dominant and
highly cache-friendly. 71.8 % of prompt tokens were served from cache. Sizing a PTU
pool from raw prompt-token volume would over-provision this workload by roughly
3–4×. Conversely, the long serial DAG means *concurrency* is low but *session
duration* is long — the shape that punishes naive per-request PTU sizing.

Raw ledger: `evidence/stepfly/tests/provider-ledger.jsonl` (23 fields per attempt,
captured pre-SDK-flattening).

---

## 4. Solution 4 — Multimodal Video / Media Analysis

**Track:** deployable sample · **Status: VERIFIED** · **Attempts used: 6**

### 4.1 What was built

The upstream repo is stale (tag `2024-11-09`; last commit 2025-05-07) and the
native console sample authenticates with an API key stored in user-secrets. I
built a lab variant, `ConsoleAOAI-Lab-VideoAnalyzer`, that:

- replaces the API key with `DefaultAzureCredential` (keyless),
- disables streaming so token usage is reliably returned,
- parameterises video / prompt / frame count / test label,
- adds a two-clip comparison mode,
- emits one telemetry JSON per call.

The unmodified upstream sample also builds cleanly (`net8.0` under SDK 10.0.303).

### 4.2 Test results

| # | Test | Expected | Actual | Verdict |
|---|---|---|---|---|
| v1 | Describe clip | Accurate description | Accurate; 4,973 in / 121 out | **PASS** |
| v2 | **Absent-event rejection** | Deny an event that never occurs | Correctly denied; 5,015 in / 28 out | **PASS** |
| v3 | Ordering / localisation | Correct temporal order | Correct; 5,012 in / 103 out | **PASS** |
| v4 | Insurance structured extraction | JSON claim record | **HTTP 400 `content_policy_violation`** | **BLOCKED** |
| v5 | Two-clip comparison | Identify differences | Correct; 8,049 in / 159 out | **PASS** |
| v6 | Corrupted media | Fail cleanly, no model call | `moov atom not found`; **0 model calls** | **PASS** |

### 4.3 The content-filter finding

Test v4 used **the repository's own bundled sample**, `insurance_v3.mp4`. Azure AI
Content Safety rejected the sampled frames:

```
HTTP 400 (invalid_request_error: content_policy_violation)
Your input image may contain content that is not allowed by our content safety system.
```

Full record: `evidence/video/tests/v4-insurance.json` — the harness decoded 422
frames, sampled 10 (step 43, 1,093,927 bytes) and the call was rejected in 5.81 s.

This is recorded as **blocked, not fixed**. Relaxing content filters is a governance
change outside the authority of this lab. The finding stands on its own merits: an
accelerator whose headline insurance-claims demo is rejected by the platform's own
default safety configuration will fail in a customer demo, and the customer will
see a raw HTTP 400.

Test v6 is the quality highlight — corrupted media fails at decode time and
**consumes zero tokens**. That is correct, cost-safe engineering.

### 4.4 Measurement notes

- Roughly **500 input tokens per submitted frame** (4,973 for 10; 8,049 for 12).
- Frame count is therefore the dominant PTU cost lever for this workload, far more
  than prompt text.
- `Azure.AI.OpenAI` 2.0.0 does **not** expose `ChatTokenUsage.InputTokenDetails`, so
  **cached-token data is unavailable at this pin**. I did not upgrade the SDK, to
  keep the measurement faithful to the shipped sample.

---

## 5. Solution 6 — Call Center Voice Agent

**Track:** deployable accelerator · **Status: PARTIALLY VERIFIED** · **Attempts used: 4**

### 5.1 What I proved

Telephony is an explicit stop gate, but the *core dependency* is not telephony —
it is the Azure Voice Live realtime session. I isolated and tested exactly that,
with no PSTN, no ACS, and no browser microphone, using a purpose-built probe
(`repo/continuation/ccv-lab/voicelive_probe.py`) against
`aif-ccptu1feb0911` (eastus2) with keyless Entra credentials.

**Four of four sessions succeeded.**

| Run | Connect (s) | TTFT (s) | Post-connect first token (s) | Tokens (in/out) | Status |
|---|---|---|---|---|---|
| 1 | 4.826 | 5.321 | 0.495 | 50 / 37 | COMPLETED |
| 2 | 4.134 | 4.833 | 0.699 | ~44 / ~37 | COMPLETED |
| 3 | 4.336 | 5.295 | 0.959 | ~44 / ~37 | COMPLETED |
| 4 | 4.089 | 4.741 | 0.652 | ~41 / ~37 | COMPLETED |

Sample session `sess_3iJfhv8Cyp3p9vgakai4Xm`, response `resp_7USWj7KJID2EwC2rE0q9jY`,
status `COMPLETED`. Evidence: `evidence/call-center-voice/tests/voicelive-probe*.json`.

**Latency honesty note.** The ~4.1–4.8 s connect time is *not* a Voice Live result.
My probe used `AzureCliCredential`, which shells out to `az account get-access-token`
per connection. That subprocess dominates the measurement. The number that
actually characterises the service is **post-connect first token: 0.50–0.96 s
(mean ≈ 0.70 s)** — which is a credible latency budget for conversational voice.
A production deployment using managed identity would not pay the CLI penalty.

*(Harness artifact, disclosed: `output_text` in run 1 appears duplicated because my
probe concatenated both streaming deltas and the final response item. The model
emitted the text once.)*

### 5.2 Correction to a prior-pass assumption

An earlier note in this bundle recorded Voice Live as **key-only** authentication.
**That is wrong**, and I am correcting it here. `server/app/config_validator.py`
accepts either credential and explicitly *recommends* managed identity:

```
Set either AZURE_USER_ASSIGNED_IDENTITY_CLIENT_ID (recommended)
or AZURE_VOICE_LIVE_API_KEY.
```

Similarly, I initially suspected a missing `aiohttp` dependency was a repo defect.
It is not — `server/pyproject.toml:19` correctly pins
`azure-ai-voicelive[aiohttp]>=1.1.0`. The omission was in **my** harness. Recorded
so the finding is not miscounted against the repo.

### 5.3 The PTU-relevant finding

> **This solution does not consume an Azure OpenAI PTU pool.**

Hard evidence: the probe ran `gpt-4o-mini` successfully against
`aif-ccptu1feb0911` — an account whose only Azure OpenAI deployments are
`gpt-5.4-mini` and `text-embedding-3-small`. No `gpt-4o-mini` deployment exists
there, or anywhere in the subscription. Voice Live therefore resolves its model on
the **Speech/Voice Live service plane**, independently of Azure OpenAI deployments,
and is billed and capacity-managed on that plane.

Including this solution in a chat-completions PTU bundle on the assumption that it
draws from the same pool would be a **material sizing error**.

### 5.4 What remains blocked

| Gate | Why |
|---|---|
| PSTN / telephony (ACS, Twilio, Infobip, Sinch, Genesys, Bandwidth) | Requires phone-number acquisition and carrier configuration — explicit stop gate, recurring cost |
| Browser microphone client | Cannot be exercised headlessly; needs a human with a mic |
| `uv` toolchain | Not installed; the documented local-dev path depends on it |

Only one telephony provider can be active at a time; the service auto-selects by
which credentials are present, defaulting to ACS.

---

## 6. Solutions 1 & 2A — Contract / RFP Reviewer and Employee Self-Service (MACAE content packs)

**Track:** configuration · **Status: INSPECTED** · **Provider attempts: 0**

These are not separate products. They are **content packs** layered on the
Multi-Agent Custom Automation Engine (MACAE). No MACAE instance was deployed in
this pass, so I validated them **offline** against MACAE's own documented
authoring contract (`content_packs/README.md`) using
`scripts/validate_macae_content_packs.py`.

### 6.1 Results — 33 PASS / 6 FAIL

Full output: `evidence/macae-packs/tests/content-pack-validation.json`.

What passes is genuinely reassuring — the hard part is wired correctly:

| Check | contract_compliance | rfp_evaluation | hr_onboarding |
|---|---|---|---|
| `pack.json` parses | PASS | PASS | PASS |
| Team-level required fields | PASS | PASS | PASS |
| `status: visible` | PASS | PASS | PASS |
| `starting_tasks` required fields | PASS | PASS | PASS |
| Registered in `Selecting-Team-Config-And-Data.ps1` | PASS | PASS | PASS |
| Agent → KB registered in `seed_knowledge_bases.py` | PASS (3/3) | PASS (3/3) | n/a (no KB) |
| `blob_indexes` source directories exist | PASS (3/3) | PASS (3/3) | n/a |
| Index referenced by a knowledge source | PASS (3/3) | PASS (3/3) | n/a |
| **`team_id` is a hex UUID** | **FAIL** | **FAIL** | **FAIL** |
| **Agent `input_key` uniqueness** | **FAIL** | **FAIL** | **FAIL** |

The full four-file knowledge-base wiring chain — team JSON → `seed_knowledge_bases.py`
→ knowledge source → blob index → dataset directory — is intact and consistent for
both document-centric packs. That is the part most likely to be broken in a
hand-authored pack, and it is correct here.

### 6.2 The systemic conformance defect

Extending the check across **all seven** shipped packs
(`evidence/macae-packs/tests/team-config-conformance.json`):

| Pack | `team_id` | Hex-UUID conformant | Agents | `input_key` populated |
|---|---|---|---|---|
| `example_pack` | `00000000-0000-0000-0000-0000000000ee` | **Yes** | 2 | Yes |
| `content_gen` | `content-gen-team` | No | 6 | Yes |
| `contract_compliance` | `team-compliance-1` | No | 3 | **No** (all empty) |
| `rfp_evaluation` | `team-clm-1` | No | 3 | **No** (all empty) |
| `hr_onboarding` | `team-1` | No | 2 | **No** (all empty) |
| `marketing_press_release` | `team-2` | No | 2 | **No** (all empty) |
| `retail_customer` | `team-3` | No | 3 | **No** (all empty) |

**Only the example pack follows the documented rules.** Six of seven real packs
violate the `team_id` hex-UUID rule, and five of seven ship empty `input_key`
values on every agent despite the README requiring uniqueness for inter-agent
routing.

**Scope of this claim — stated precisely.** The README says missing required
fields cause a `400` on upload. I did **not** upload anything, because no MACAE
instance was deployed. I therefore **cannot** and **do not** claim these packs fail
to upload. What I claim is narrower and fully supported: *the accelerator's shipped
packs do not conform to the accelerator's own published authoring contract.* The
practical risk is that a customer who follows the README to author a new pack will
produce artifacts structurally unlike every shipped example, and will have no
working reference to copy.

### 6.3 Model compatibility — a genuine positive

Every pack targets `gpt-5.4-mini` except `hr_onboarding`, which targets `gpt-5.4`.
Both are already deployed on `ptumacae7d804f70`. **No new model deployment or quota
request is required** to run these packs.

### 6.4 Housekeeping

`contract_compliance/agent_teams/` contains a zero-byte `desktop.ini` (a OneDrive
artifact from this workstation, not from the repo). The uploader globs `*.json`, so
it is inert — recorded for completeness, not as a repo defect.

### 6.5 What is NOT proven

No contract was reviewed. No RFP was evaluated. No onboarding conversation ran. No
grounding, retrieval, or synthesis quality was measured, and the previous pass's
MACAE final-synthesis step had already failed. **These solutions remain functionally
unproven.** The verdict here is a configuration-track verdict only.

---

## 7. Solution 2B — Employee Self-Service Agent Developer Kit

**Track:** owner / enablement · **Status: BLOCKED** · **Provider attempts: 0**

### 7.1 What it actually is

It is **not an Azure deployment**. It is a monorepo of VS Code Copilot slash-command
skills for building a Copilot Studio agent that integrates **Workday** and
**ServiceNow**. Its own README states:

> **This repo is intended as an example or learning tool.** It is not a Microsoft
> product or a supported service.

`SUPPORT.md` confirms: *"Support for this project is limited to the resources listed
above"* — i.e. GitHub Issues only. **There is no support owner.** For a portfolio
intended for customer engagements, this is the decisive finding.

### 7.2 The readiness gate, quantified

The kit ships `FlightCheck`, a pre-deployment validator. Running it offline
(`--list-checkpoints`) produced 28 checkpoint families
(`evidence/ess-devkit/tests/flightcheck-checkpoints.txt`), which resolve to **four
distinct administrative personas**:

| Role required | Example checkpoints |
|---|---|
| **Power Platform Admin** | `ENV-001`, `ENV-002`, `ENV-009`, `ENV-CAPACITY-001`, `WD-ENV-*`, `WD-FLOW-*`, `WD-PKG-001` |
| **Entra Admin** | `WD-ASSIGN-001`, `WD-ENTRA-CONSENT-001`, `WD-ENTRA-SCOPE-001`, `WD-ENTRA-NAMEID-001`, `WD-ENTRA-SIGNOPT-001` |
| **Workday Admin** | `WD-API-CLIENT-001`, `WD-TENANT-001`, `WD-WF-*`, `WD-RUN-001` |
| **ESS Maker / Agent Developer** | `ESS-SOLN-001`, `DV-CONN-001`, `TOPIC-*`, `WD-REST-001/002` |

Four `Critical` checkpoints require **Entra admin consent** and three require a
**Workday tenant with API client credentials**. Both are explicit stop gates.

### 7.3 Hard blocks encountered

Attempting the lightest possible run failed immediately and by design:

```
$ python -m scripts.flightcheck.cli --scope local ...
ERROR: .local/config.json not found. Run /setup first.
```

`/setup` is an **interactive VS Code Copilot Chat slash command** — it cannot be
driven from a terminal or automated. The kit additionally requires a **GitHub
Copilot subscription** and that the correct *sub*-folder
(`solutions/ess-maker-skills`) be opened as the workspace root, a documented
footgun the README devotes a whole troubleshooting section to.

### 7.4 Assessment

Even with every approval granted, this solution's LLM consumption sits in **Copilot
Studio**, not in a customer-managed Azure OpenAI PTU pool. Like solution 6, it does
not draw on the bundle's PTU capacity. Combined with the absence of a support owner
and a hard dependency on a third-party SaaS tenant (Workday), **this is the weakest
portfolio fit of the ten.**

---

## 8. Solution 3 — "Document Generation" → Content Generation

**Track:** deployable accelerator · **Status: INSPECTED** · **Provider attempts: 0**

### 8.1 Authority conflict — the headline

`microsoft/document-generation-solution-accelerator` now returns
**HTTP 301 → `content-generation-solution-accelerator`**. The repository README
describes something materially different from the portfolio idea:

> "an internal chatbot that interprets and understands context and direction from
> **creative briefs** to create multi-modal text and image content for **marketing ad
> campaigns**."

Per the controls, repository documentation is authoritative and conflicts are
**recorded, not worked around**. The portfolio intent — generating business
documents such as contracts, proposals, and reports — **is no longer served by this
repository.** Anyone planning against "document generation" should treat this line
item as lapsed and re-scope.

Ironically, the closest surviving fit for the original intent is the MACAE
`contract_compliance` / `rfp_evaluation` packs in §6.

### 8.2 What was verified at no cost

`az bicep build infra/main.bicep` → **exit 0, 0 errors, 2 warnings.**
(`evidence/content-generation/tests/bicep-build.log`)

The compiled ARM template is AVM-based and substantial:

| Resource type | Count in compiled template |
|---|---|
| `Microsoft.Resources/deployments` | 168 |
| `Microsoft.Authorization/roleAssignments` | 41 |
| `Microsoft.Authorization/locks` | 25 |
| `Microsoft.DocumentDB/databaseAccounts` | 16 |
| `Microsoft.Storage/storageAccounts` | 15 |
| `Microsoft.Network/privateEndpoints` | 14 |
| `Microsoft.Compute/virtualMachines` | 13 |
| `Microsoft.ContainerRegistry/registries` | 6 |

*(AVM modules include conditional variants, so these are template-declaration
counts, not deployed-instance counts.)*

WAF feature flags (`enableMonitoring`, `enableScalability`, `enableRedundancy`,
`enablePrivateNetworking`) all default to **`false`** — a sensible cheap-by-default
posture, but it means the shipped default is *not* the production-grade
configuration a customer demo may imply.

### 8.3 Deployment friction

`azure.yaml` defines `workflows.up` as **`azd provision` only**. Deployment is not
one command; two manual post-provision scripts are required *in order*:

1. `infra/scripts/build_and_deploy_images.ps1` — builds and pushes container images to ACR
2. `infra/scripts/process_sample_data.ps1` — loads sample data (only after step 1)

### 8.4 Blocking capability gap

`.env.sample` requires **two** models:

- `AZURE_ENV_GPT_MODEL_NAME=gpt-5.1` — available (three accounts)
- `AZURE_ENV_IMAGE_MODEL_NAME=gpt-image-1-mini` — **not deployed anywhere in the subscription**

Multi-modal image generation is this accelerator's differentiator, and it cannot
run today. Beyond availability, image generation is **not served by chat-completions
PTU**, so — as with solution 6 — its principal cost driver sits outside the bundle's
PTU pool.

### 8.5 Not deployed — and why

Deployment was declined under the cost stop gate: an Azure Container Registry, a
Container Apps environment, Cosmos DB, AI Search, and VMs constitute recurring
fixed cost with no approval on file, for an accelerator that **no longer matches the
portfolio requirement**. Spending on it before re-scoping would be the wrong order
of operations.

---

## 9. Solution 7 — Private-Tenant AI Chat / Deploy Your AI Application In Production

**Track:** platform / landing zone · **Status: INSPECTED** · **Provider attempts: 0**

### 9.1 Verified at no cost

The git submodule `submodules/ai-landing-zone`
(`Azure/bicep-ptn-aiml-landing-zone` @ `37b856bc3113`, v1.0.0-1) was initialised and
the full template compiled:

`az bicep build infra/main.bicep` → **exit 0, 0 errors, 78 warnings**
(68 `no-unused-params`, 6 `BCP318`, 2 `BCP321`, 2 `use-safe-access`), producing a
**238,181-byte** ARM template. Evidence:
`evidence/private-tenant-chat/tests/{bicep-build.log,main.compiled.json}`.

Zero errors across a wrapper plus a full landing-zone submodule is a real signal of
template quality, and it is the strongest *verifiable* result available for this
solution without spending money.

### 9.2 The Fabric linkage — a new finding

The compiled wrapper template declares **`Microsoft.Fabric/capacities`**.

This binds solution 7 to the **same blocker** that stops solutions 8 and 9: the
`Microsoft.Fabric` resource provider is **`NotRegistered`** in this subscription and
**zero** Fabric capacities exist. Solution 7's golden path is not independently
deployable here. The README's mitigation — disable Fabric and Purview on first run —
is sound, but it also means the "complete production AI platform" claim is not what
gets deployed.

### 9.3 Cost — a clear stop gate

The checked-in `infra/main.bicepparam` defaults are, in the README's own words, an
"opinionated end-to-end provisioning path", not a baseline. They deploy:

| Component | Default | Cost character |
|---|---|---|
| PostgreSQL Flexible Server | `Standard_D2s_v3`, GeneralPurpose, 32 GB | **Always-on hourly** |
| Virtual Machine (+ extension) | `deployVM = true` | **Always-on hourly** |
| Container Registry | `deployContainerRegistry = true` | Fixed monthly |
| Container Apps + environment | `true` | Variable |
| Azure AI Search | `deploySearchService = true` | Fixed monthly |
| Key Vault ×2, App Config, App Insights | `true` | Low |
| Private networking | `networkIsolation = true` | Private endpoints, longer deploys |

This is a multi-hundred-dollar-per-month footprint. **No approval is on file, so it
was not deployed.**

### 9.4 Security posture observation

A real tension exists in the defaults, and the README acknowledges it:

```
param networkIsolation            = true
param postgreSqlNetworkIsolation  = false
param postgreSqlAllowAzureServices = true
```

The golden path **weakens PostgreSQL network isolation** so that Fabric mirroring
works, inside a template whose entire premise is private networking. The README also
advises temporarily opening Key Vault *and* PostgreSQL to run the mirroring prep
script from a non-VNet host. Both are defensible engineering trade-offs, but a
customer must make them **knowingly**. Additionally, PostgreSQL ships with
`passwordAuth: Enabled` alongside Entra auth, and an admin password persisted to
Key Vault.

### 9.5 Approval gates

| Gate | Requirement |
|---|---|
| Fabric automation | Fabric Administrator; provider registration |
| Fabric capacity creation | `fabricCapacityAdmins` entry; capacity SKU cost |
| Purview integration | Existing Purview account **+ Purview Collection Admin** |
| Private networking | Private endpoint provisioning time and complexity |
| Fixed cost | PostgreSQL + VM + ACR + Search always-on |

---

## 10. Solutions 8 & 9 — Fabric Unified Data Foundation and Real-Time Operational Intelligence

**Track:** platform · **Status: BLOCKED** · **Provider attempts: 0**

Both are blocked at the same place, and the block is absolute rather than a matter
of effort.

### 10.1 Evidence of the block

| Check | Result |
|---|---|
| `Microsoft.Fabric` resource provider | **`NotRegistered`** |
| `Microsoft.Fabric/capacities` in subscription | **0** |

Registering the provider is a subscription-level change; creating an F-SKU capacity
is a **material recurring cost** (an F2 bills continuously until paused). Both fall
squarely inside the stop-gate list.

### 10.2 Additional gates per solution

**Solution 8 — Unified Data Foundation** (`28c25024e438`, v1.25.4)

- Entra **app registrations** (stop gate)
- An **F2 or larger** Fabric capacity (cost gate)
- Fabric workspace admin rights

**Solution 9 — Real-Time Operational Intelligence** (`cfbdb91ee83e`, v1.3.5)

- An **organisation-level Fabric licence**, enabled in the **M365 admin centre** — outside this subscription entirely, and outside my authority
- Fabric capacity creation
- **User Access Administrator** role for role assignments
- A **preview** Fabric Data Agent SDK (preview enablement is a stop gate)

### 10.3 Honest statement

**Nothing was validated for solutions 8 or 9.** No deployment was attempted, no code
was executed, and no measurement was taken. The repositories were cloned, pinned,
secret-scanned, and read — that is the entirety of the work, and no conclusion about
their fitness should be drawn from this report.

To unblock, a decision-maker must approve, in order:
(1) `Microsoft.Fabric` provider registration; (2) capacity creation at a named SKU
with a named owner and a pause policy; (3) for solution 9, an org-level Fabric
licence via M365 admin, a UAA role assignment, and preview SDK acceptance.

---

## 11. Solution 10 — Harbinger

**Track:** owner validation only · **Status: BLOCKED** · **Provider attempts: 0**

No public or internally locatable package, repository, or deployment artifact was
found for this item. **Nothing was validated, and nothing is asserted.**

Per the continuation instructions this is owner-validation-only. The following
evidence must be supplied by the owning team before any technical assessment is
possible:

1. Named **owner** and **support model** (who is paged, under what SLA)
2. **Source or package location** and access method
3. **Architecture**, including which model endpoints it calls and on which plane
   (Azure OpenAI chat-completions vs. Speech vs. Copilot Studio — this determines
   whether it belongs in a PTU bundle at all)
4. **Data classification** and residency constraints
5. **Authorised workflows** — what it is permitted to do autonomously
6. Whether it requires **preview** features, **app registrations**, or **admin consent**

Until item 3 is answered, Harbinger's inclusion in a PTU capacity plan cannot be
justified numerically.

---

## 12. Cross-cutting analysis

### 12.1 PTU relevance — which solutions actually consume the pool?

This is the question the bundle exists to answer, and the answer is uncomfortable.

| Solution | Consumes Azure OpenAI chat PTU? | Basis |
|---|---|---|
| 1 / 2A MACAE packs | **Yes** | `gpt-5.4` / `gpt-5.4-mini` chat deployments |
| 2B ESS dev kit | **No** | Copilot Studio licensing plane |
| 3 Content generation | **Partly** | `gpt-5.1` chat yes; **image generation no** |
| 4 Video analysis | **Yes** | Chat-completions with image parts |
| 5 StepFly | **Yes** | Chat-completions (`gpt-4.1-mini`) |
| 6 Call Center Voice | **No** | **Proven** — Voice Live/Speech plane |
| 7 Private-tenant chat | **Yes** | Foundry chat deployments |
| 8 / 9 Fabric | **Unknown** | Never reached |
| 10 Harbinger | **Unknown** | No artifact |

**At most five of ten** solutions clearly draw on a shared chat-completions PTU
pool. Two provably do not. Three are unknown. A bundle-level PTU sizing exercise
that assumes all ten share one pool would be wrong by a wide margin.

### 12.2 Token-shape summary (the transferable measurement)

| Workload | Input tokens | Output tokens | Ratio | Cache hit | Dominant cost lever |
|---|---|---|---|---|---|
| StepFly (20 calls) | 249,144 | 3,677 | 68 : 1 | **71.8 %** | Context accumulation across a serial DAG |
| Video (per call, 10 frames) | ~5,000 | ~120 | 41 : 1 | unavailable at SDK pin | **Frame count** (~500 tokens/frame) |
| Voice Live (per turn) | ~45 | ~37 | 1.2 : 1 | n/a | Turn count — **and not on the PTU plane** |

Two of the three verified workloads are **extremely input-heavy**, which is the
profile PTU serves well — but only if prompt caching is accounted for. Ignoring
StepFly's 71.8 % cache rate would over-provision by 3–4×.

### 12.3 Defect pattern

The two execution-blocking defects found (StepFly's unresolvable pins and its silent
Windows hang) share a root cause: **these accelerators are validated on Linux/CI and
not on the Windows developer workstations customers actually use.** The Unicode hang
in particular produces no error output at all — the worst possible failure mode for
a field engineer in front of a customer.

The MACAE pack conformance gap has a different but equally common root cause:
**documentation and shipped artifacts drifted apart**, with only the toy
`example_pack` kept in sync.

### 12.4 Cost and retention

**No new billable Azure resources were created during this pass.** All model calls
used pre-existing deployments. Local artifacts (venvs, a MongoDB container, cloned
repos) live outside Azure and are listed in §14.

Retained pre-existing lab resource groups (from the earlier pass, untouched here):
`rg-ptu-macae-demo`, `rg-ptu-content-demo`, `rg-ptu-bundle-platform` (62 resources),
`accel-chatbot-eval-0911`, `accel-dkm-20260911`, `rg-ptu-conversation-demo`,
`rg-ptu-modernize-demo`.

### 12.5 Protected resources

`rg-specsuite-ai-can`, `rg-demo`, `specsmith-rg`, `rg-planetaryexplorer`, `rg-pexalex`
were **not modified, read into, or deployed to**. SpecSuite and Planetary Explorer
remained inventory-only throughout. All mutating Azure calls were routed through
`Invoke-LabAz.ps1`, which rejects delete/purge/destroy/down operations, provisioned
and reservation operations, and any mutation targeting a protected resource group.

---

## 13. Recommendations

### 13.1 Immediate — before any further PTU work

1. **Stop describing this as a measured PTU evaluation.** Provision at least one
   `ProvisionedManaged` deployment, or re-label every existing number as a
   Standard-capacity token-shape study. This is the single highest-value action.
2. **Re-scope solution 3.** "Document generation" no longer exists as a product.
   Decide whether the requirement is marketing content generation (use the renamed
   repo) or business document generation (use MACAE `contract_compliance` /
   `rfp_evaluation`).
3. **Remove solutions 2B and 6 from PTU sizing.** Both provably consume capacity on
   other planes. Keep them in the portfolio on their merits; exclude them from the
   pool arithmetic.

### 13.2 Short term

4. **File the two StepFly defects upstream** — the dependency conflict and,
   especially, the silent Unicode hang.
5. **Raise the MACAE pack conformance gap** — either fix the six non-conforming packs
   or correct the README. As shipped, the documentation and the examples teach
   contradictory things.
6. **Report the video content-filter block** to the accelerator owners. A bundled
   sample that the platform's default safety configuration rejects is a
   demo-breaking defect, not a customer configuration issue.
7. **Obtain a Fabric decision.** Solutions 7, 8, and 9 — three of ten — are gated on
   one provider registration and one capacity SKU. That decision unblocks a third of
   the portfolio.

### 13.3 To complete the evaluation

8. **StepFly to Step 9** with a budget of ~30 attempts, to settle whether it finds the
   planted root cause. This is the most scientifically valuable open question in the
   set and is cheap to answer.
9. **Deploy MACAE and actually upload the packs** — this converts §6 from a
   configuration verdict into a functional one, and definitively answers whether the
   `team_id` violations are rejected by the API.
10. **Re-run the Voice Live probe with managed identity** to obtain a fair
    connection-latency number free of the `AzureCliCredential` subprocess penalty.
11. **Obtain Harbinger's architecture** — specifically which model plane it uses.

---

## 14. Reproducibility and cleanup

### 14.1 Evidence index

| Path | Contents |
|---|---|
| `evidence/continuation-preflight/` | Resource groups, AI accounts, model deployments, **deployment SKU audit**, repo provenance, secret scan |
| `evidence/stepfly/tests/` | `provider-ledger.jsonl` (20 attempts × 23 fields), `step-results-sf04.txt` |
| `evidence/stepfly/raw-responses/` | `console-sf03-unicode-defect.log`, `console-sf04.log`, `trace-sf04/` |
| `evidence/video/tests/` | `v1`–`v6` telemetry JSON incl. the content-filter rejection |
| `evidence/call-center-voice/tests/` | `voicelive-probe.json` + 3 latency runs |
| `evidence/macae-packs/tests/` | `content-pack-validation.json`, `team-config-conformance.json` |
| `evidence/private-tenant-chat/tests/` | `bicep-build.log`, `main.compiled.json` (238 KB) |
| `evidence/content-generation/tests/` | `bicep-build.log`, `main.compiled.json` |

### 14.2 Harnesses written for this pass

| File | Purpose |
|---|---|
| `scripts/validate_macae_content_packs.py` | Offline MACAE pack conformance validator |
| `repo/continuation/stepfly/lab_instrument.py` | Cross-process file-locked attempt budget + telemetry |
| `repo/continuation/stepfly/lab_run.py` | Non-interactive bounded StepFly runner |
| `repo/continuation/netaivideoanalyzer/src/ConsoleAOAI-Lab-VideoAnalyzer/` | Keyless instrumented video analyzer |
| `repo/continuation/ccv-lab/voicelive_probe.py` | Telephony-free Voice Live session probe |

### 14.3 Lab adaptations (disclosed)

| File | Change | Reason |
|---|---|---|
| `stepfly/config/config.json` | `model`: `gpt-4o` → `gpt-4.1-mini` | `gpt-4o` unavailable on the target account |
| `stepfly/config/config.json` | `max_executor_number`: 3 → 1 | Enforce concurrency 1 per the measurement contract |
| `stepfly/requirements.lab.txt` | `h11==0.14.0`, `python-engineio==4.11.2` | Work around defect 1 |
| env | `PYTHONIOENCODING=utf-8` | Work around defect 2 |

### 14.4 Cleanup performed

- All Python harness processes terminated.
- MongoDB container stopped (see §14.5).
- No Azure resources created, modified, or deleted.
- No keys printed or persisted.

### 14.5 Local artifacts retained deliberately

Cloned repositories, virtual environments, the 57 MB synthetic StepFly database,
and the corrupted-media fixture remain under
`C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\continuation\` so the results
are reproducible. They are local only and incur no Azure cost.

---

## 15. Statement of limitations

To be explicit about what this report is **not**:

- It is **not** a PTU performance study. No provisioned capacity was measured (§1.1).
- It is **not** a business-outcome evaluation for eight of the ten solutions. Only
  solutions 4, 5, and 6 executed real model calls.
- Solution 5's central question — does StepFly find the planted root cause? — is
  **unanswered**, by choice, to honour the attempt budget.
- Solutions 8, 9, and 10 have **no technical findings whatsoever**.
- Sample sizes are small (20, 6, and 4 provider attempts). Latency figures are
  indicative, not statistically robust.
- One figure in §5.1 is contaminated by harness overhead and is labelled as such
  rather than quietly dropped.

Where this report says PASS, it means a specific, reproducible check passed — not
that the solution is ready for a customer.
