# Conversation Knowledge Mining - deployment/evaluation

**Coordinator closing addendum (2026-09-12T06:21:44Z):** Azure SQL was observed
**Paused** through a read-only ARM check. This supersedes the earlier Online
observations retained below; it does not remove earlier compute charges.
All new cloud application replicas are independently verified zero in
`evidence\runtime-state-final.json`. SQL evidence:
`evidence\costs\sql-final-state.json`.

**Current outcome:** approved private SQL, Blob and Basic Search are deployed.
The original CKM routes completed durable ingestion, fresh SQL reload, cross-call
Search retrieval, a model-planned/SQL-computed dashboard and processing insights.
**Operational execution succeeded, but semantic quality did not fully pass.**
Hosted Explore remains incompatible with the current private Basic Agent setup.
There is **no remaining approval gate for the listed deployed dependencies**;
the controlling fixed-active review limit is **US$1.50/hour**.

The earlier measured model workflow used original FastAPI handlers through
TestClient. **The serving deployment gap is now closed for native read-only
operation:** SQL/Blob/Search/MI and the direct model endpoint are durably bound
in Container Apps configuration. A dedicated fail-closed entrypoint runs the
original API, with inference permanently disarmed at9/9 and automatic/queue
processing disabled. No generic replacement handlers were added.
This is still **not full browser-to-app deployment**: public UI access remains
unverified403 and hosted Explore remains unsupported.

**Final disposition:** all14 retained cloud revisions are inactive/replicas0.
SQL remains **Online**, serverless min0.5/max2, auto-pause60 configured;
actual SQL pause has not yet been observed. Search, four private endpoints,
Storage and AI resources remain retained. No automatic Azure cleanup occurred.
Original local API/UI were last verified healthy on loopback8115/5115.

## Durable native serving verification

One configure/read attempt (maximum2) passed **15 real-HTTP checks** at
2026-09-12T05:18:53Z-05:18:57Z. The probe used ordinary HTTP to the running
Uvicorn process, **serving PID1**, not TestClient or another handler process.
Native `/api/health` returned200 with SQL ok and Search configured; native
`POST /api/ingestion/refresh` reloaded one persisted file; native document-list
and three document-by-ID reads returned the exact original transcripts, verified
by SHA256. Cosmos remains unavailable and is not claimed by this SQL health check.

Eight model/mutation routes returned explicit503 disarm errors, including
summary, dashboard, Explore, embeddings, CU, pipeline execution, automatic
processing enablement and upload. No heuristic output was accepted as AI.
Offline checks also proved sync/async httpx, requests and aiohttp cannot dispatch
model requests. The serving guard allows only read-only Blob/Search HTTP and
the managed-identity token endpoint; SQL continues using native Entra/ODBC.
The original queue-only lifespan is deliberately suppressed and the native
pipeline engine is explicitly configured `enabled=false, auto_select=false`.

ARM readback after the min0 scale update matched all16 durable nonsecret
settings and the guarded image. The restart helper rejects older unguarded
images while those bindings exist. No new PaaS, model, role or network change
was made. The current image is based on the original API image, not the
earlier live-evaluator layers. Source routes and known semantic defects remain
unchanged. Blob/Search authorization was not re-probed in this SQL-read pass.
Evidence: `serving-results.json`, `serving-http-attempt-1.json`,
`serving-native-config.json` and `serving-*-final-state.json`.

## Actual native workflows and acceptance

Data pass:2026-09-12T04:08:12.657013Z to04:08:57.464954Z.
The three inputs used the previously measured native summaries as the
repository-supported **pre-enriched JSON** format. These were not fabricated
summaries or additional model requests. The earlier printer-summary qualification
was preserved rather than silently repaired.

| Check | Expected | Actual / assessment |
|---|---|---|
| Private authorization | Own SQL/Search/Blob accessible by MI over private DNS | Passed; SQL schema initialized, Search management authorized, Blob authorized |
| Original JSON upload | Three records accepted through native route | Passed; automatic pipeline disabled through native API |
| Durable SQL | Three exact IDs and measured summaries persisted | Passed |
| Fresh native service | Reload without reusing original in-memory records | Passed; three documents from SQL |
| Blob persistence | Original text and summary for each of three calls | Three individual comparisons passed |
| Basic Search schema | Native field/HNSW/semantic schema accepted |14 fields accepted; unused remote vectorizer omitted; no vector/semantic query claimed |
| Native BYOI connector | Read own index containing three records | Passed |
| Cross-call retrieval | VPN query returns calls001/002, not printer call003 | Passed, original IDs/text returned; retrieval evidence, **not an agent answer with citations** |
| Model-planned SQL dashboard | Native model planning and SQL computations execute | One actual model request, HTTP200, total records3 and category chart VPN2/Printer1 |
| Distinct-category KPI |2 | **Failed:3** |
| Distinct-source-type KPI |1 | **Failed:3** |
| Dashboard prose | Ordinary words not replaced as names | **Failed:** phrases such as “credential rotation users were resolved by users cached credentials” |
| Native processing insights | Ground conclusions across the supplied three-call scope | One model request/HTTP200, but **input scope is only collection count plus first file summary**; report analyzes one incident and overgeneralizes |
| Least-privilege SQL restart | MI works after server-admin privilege removed | Passed after correction; current user `id-ptu-conversation-runtime`, db_owner0, reader/writer/ddl_admin1; native reload3 |

The automated data pass contains **14 operational checks**; separate manual
quality checks explicitly record the failures above. HTTP200/nonempty KPIs were
not treated as proof of semantic correctness. Direct SQL later confirmed
**3 records,2 categories,1 source type**, agreeing with the correct chart but
contradicting the two KPI labels.

Source-grounded quality findings, not patched upstream behavior:
- `modules/insights/service.py:597` executes `COUNT(*)` for a count KPI; a
  distinct-count label is not sufficient to produce a distinct SQL aggregate.
- The same file's token collection/anonymization around350-425 can replace
  ordinary words with “users,” damaging prose.
- `modules/ingestion/service.py:372` builds a pre-enriched multi-document file
  summary using collection size plus the first summary. Processing insights
  consumes file summaries, not every transcript.
- The processing output inferred durability concerns/repeatability from a
  routine next-day follow-up. Those implications were not established facts.

Earlier native summary pass: calls001/002 retained the credential-cache issue,
successful fix and distinct follow-ups. Call003 retained unknown cause/final
resolution and callback/exact-error follow-up, but inferred “printer is not
working” from an inaudible symptom. Four gender/age variants retained technical
facts but repeated unnecessary demographics. This is not fairness assurance.
All seven summaries were within180 words.

## Actual model traffic and PTU status

**Final allocation closed12 ->9:9/9 requests used; zero SDK retries; zero in flight or reserved.**
The three unused attempts from the original12 are released to Content through
the coordinator. These are the same three from the earlier handoff, not an additional release.
No further CKM model dispatch is planned; remaining CKM allowance is now0.
See `evidence/conversation/budget-handoff.json`.
All returned `gpt-5.2-2025-12-11` from own GlobalStandard deployment.

| Seq / native operation | Input tokens | Output tokens | Total | Elapsed ms | HTTP |
|---|---:|---:|---:|---:|---:|
|1 / call001 summary|134|113|247|3004.90|200|
|2 / call002 summary|136|108|244|2336.79|200|
|3 / call003 summary|141|148|289|3024.83|200|
|4 / woman30 counterfactual|144|133|277|2814.82|200|
|5 / man30 counterfactual|144|120|264|2472.48|200|
|6 / nonbinary30 counterfactual|145|117|262|2254.86|200|
|7 / woman65 counterfactual|144|141|285|3517.59|200|
|8 / model-planned SQL dashboard|2636|931|3567|9199.50|200|
|9 / processing insights|923|1889|2812|20736.54|200|
| **Total** | **4547** | **3700** | **8247** | | |

Sequences1-7 measure the SDK RawResponse call;8-9 measure `httpx.Client.send`.
Do not combine these into a like-for-like latency distribution. Returned cached,
reasoning and audio tokens were zero. No load/capacity benchmark was performed.
Six attempted automatic AI dispatches during persistence were blocked **before
transport**; they generated no Azure inference request or usage. Native heuristic
fallback is disclosed, not presented as successful model enrichment.

Both model deployments remain **GlobalStandard capacity10**, not PTUs.
No PTU utilization, saturation, headroom or required PTU count is claimed.
Raw per-request usage/status/error evidence is retained; no estimated tokens
replace service-returned usage.

## Current Azure resources and costs

Subscription `1feb53b2-854a-4ea7-b5a6-709b7d804f70`;
tenant `a600acd0-3028-4689-8402-3b471d7d924d`.
Own RG `rg-ptu-conversation-demo`; all full IDs and role assignments are in
`evidence\conversation\result.json` and the final resource snapshots.

| Own resource | Actual configuration / current state |
|---|---|
| `id-ptu-conversation` | EastUS2 UAMI; client1b458b7e-1768-45a9-b676-9a3245a4dfbe; principalb0c36c36-5b9f-4efa-9f01-0e19fb97aa25 |
| `ca-ptu-conversation-api` | Consumption0.5CPU/1Gi, internal8000, min0/max1, paused |
| `ca-ptu-conversation-ui` | Consumption0.25CPU/0.5Gi, port80, min0/max1, paused; exact174.112.74.34/32 Allow restriction |
| `aif-ptu-conversation-7d804f70` / `proj-ptu-conversation` | Sweden Central S0/project; PNA Disabled, local auth disabled |
| `gpt-5.2` |2025-12-11, GlobalStandard10, NoAutoUpgrade |
| `text-embedding-3-small` |1, GlobalStandard10, NoAutoUpgrade; no embedding requests |
| `srch-ptu-conversation-7d804f70` | Canada Central Basic1 partition/1 replica, semantic free, PNA Disabled/local auth disabled |
| `stptuconv7d804f70` | Canada Central Standard_LRS Hot, PNA Disabled/shared keys disabled/public Blob disabled |
| `sql-ptu-conversation-7d804f70` / `ptu-conversation` | Canada Central GP_S_Gen5 serverless min0.5/max2, auto-pause60,32GB cap, Local backup, Entra-only, PNA Disabled |
| `pe-conversation-ai/sql/blob/search` plus implicit NICs | Four own PEs in shared platform RG; all Succeeded/Approved; cap4 exhausted |

Private OpenAI10.246.2.26, SQL10.246.2.28, Blob10.246.2.29 and
Search10.246.2.30 were verified from cloud. AI's other associated DNS records are
cognitive10.246.2.25 and services.ai10.246.2.27; CU authorization was not tested.

Shared, not duplicated: EastUS2 Consumption-only `cae-ptu-bundle`,
Basic/admin-disabled `acrptubundle7d804f70.azurecr.io`, VNet/PE subnet and
existing private DNS in `rg-ptu-bundle-platform`. This is expressly approved
MCAPS-local networking, not JDCP central DNS.

No CKM Cosmos, App Service, separate registry/environment/VNet, App Configuration,
new monitoring workspace, Speech resource, GPU, AKS or provisioned model SKU was
created. CU, Speech and embedding requests remain0. No protected resources were
used or modified; no PNA/policy weakening or new Entra registration/admin consent.

### Cost separation - retail references, not invoice measurements

| Meter / footprint | Reference |
|---|---:|
| SQL at maximum2 billed vCores |$1.25222/hour|
| Basic Search1x1 |$0.101/hour|
|32GB SQL data allowance |$0.005545/hour equivalent|
| Four PEs |$0.04/hour plus data processing|
| Both ACA replicas continuously active |$0.081/hour|
| **Worst-case configured steady-state subtotal** | **$1.479765/hour**, below$1.50 review limit |
| API-only during workflow, SQLmax2 |$1.452765/hour|
| All9 model requests,4547 input/3700 output | **$0.05975725** at$1.75/$14 per1M tokens |
| Five successful remote builds combined |Approximately **$0.063835**, separately metered; latest serving layer adds **$0.004625**|
| Current ACA replica compute |0 replicas|
| Search/PE/32GB allowance after SQL actually pauses |Approximately **$0.146545/hour**, plus other consumption|
| Same baseline if SQL is billed at minimum0.5 |Approximately **$0.459600/hour**, not measured usage|

Shared ACR/DNS allocation, Blob operations/capacity, network processing/egress,
logs, applicable backup overage and taxes/discounts are separate. Model/build
consumption is not a fixed reservation or PTU charge. SQL was still Online at
final readback: do not claim auto-pause has occurred or SQL compute costs zero.
The serving process last reported a SQL connection at
2026-09-12T05:18:57.464402Z. The replacement min0 revision could initialize
before final shutdown, so the final all-zero snapshot is the upper bound on
later own-process SQL activity. ARM readback at05:24:37Z was still Online;
60-minute auto-pause is conditional, not observed.
No app/worker remains connected to hold it open deliberately.

## Identity correction and controlled shutdown

Initial schema bootstrap used the own app MI as the isolated SQL server's Entra
administrator. The first contained-user setup incorrectly used its object ID
for SID. After handing server administration to the lab user, native SQL
initialization failed. This was a setup error, not an Azure region/policy gate.

[Microsoft's CREATE USER example K](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-user-transact-sql?view=azuresqldb-current#k-create-a-contained-database-user-from-a-microsoft-entra-principal-without-validation)
specifies **client/application ID for a service principal**, versus object ID
for a user/group. A2.113KiB diagnostic layer corrected the mapping without Graph
Directory Readers, tenant permissions or data/user deletion. Incorrect-user
data-role memberships were removed.

Final fresh connection identified `id-ptu-conversation-runtime`, **db_owner0**,
reader/writer/ddl_admin1. The original SQL adapter initialized and reloaded3
records under those roles. The server administrator is now the lab user
87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed, principal type User. App server-admin
privilege was removed. Source correction and both failed/successful evidence
are preserved; no further model requests were needed.

Single-revision scale changes previously reported old/new replica overlap.
The helper now uses **Multiple revision bookkeeping with exactly one active
revision allowed**, deactivates/waits for0 before updates, enforces max1 and
stops the service if reported counts exceed1. Controlled later updates showed
at most one active/replica. Final all14 retained revisions are inactive/0.
No Azure resource or dataset cleanup was performed.

## Exact remaining full-application blockers

**Hosted Explore:** the original agent-only implementation registers
`AzureAISearchTool`. [Basic Agent setup does not support private Search](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/ai-search#limitations).
An inbound account PE and an ACA client do not provide the hosted tool's outbound
private connectivity.

The [documented Standard Agent private architecture](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/virtual-networks)
needs BYO Cosmos/Storage/Search, a dedicated agent subnet, and Foundry in that
VNet's region. The current Sweden Central account/shared EastUS2 VNet do not
meet that regional relationship; Cosmos and a dedicated agent subnet are not
present in this approved listed-resource envelope. No generic grounding proxy,
public-access workaround or oversized stock deployment was substituted.

**Native quality:** distinct KPI semantics, overbroad anonymization and
file-summary context loss remain reproducible limitations. Infrastructure
success does not resolve them. Hosted-agent cross-call answer citations,
vector/semantic retrieval, CU/audio, reliable async Queue processing, production
auth and public-browser end-to-end operation remain unverified.

Queue PE remains deferred for the original JSON/in-process finalization path.
There is no fifth-PE permission implied by the four deployed connections.

## Source, images and restart

Repository:
https://github.com/microsoft/Conversation-Knowledge-Mining-Solution-Accelerator

Clone:
`C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\Conversation-Knowledge-Mining-Solution-Accelerator`

Main SHA `8a00aa54bc25fd3624020648c63f2c069172d8ca`,
commit2026-09-01T11:24:23+05:30; latest local tag `v3.23.4`;
description `v3.23.4-369-g8a00aa54`. Tracked source remains unchanged.
Contract/playbook, docs, hooks, SKUs and compatibility were inspected first.
Stock secret-writing/open-firewall/destructive-agent hooks were not run.
Unchanged existing-project IaC reuse was rejected because it redeploys models.

| Image / build | Provenance |
|---|---|
| Original API/base | `sha256:baa11a820f821532ade2129fe5dd628764b9053778b3ef6d35e89fa2345ee8f8` |
| Original UI runtime repack | `sha256:aa01cc8701fc0756de15a7b27a1bf6c783c1854e0641034aab2770823266edb8` |
| Summary evaluator / chu |96.305683s,2CPUs, Succeeded; local Unicode log-stream failure did not fail remote build |
| Initial data evaluator / chv |91.305158s,2CPUs, Succeeded; superseded before workflow |
| Final data evaluator / chw |80.444770s,2CPUs, original Dockerfile;156.136KiB clean context |
| Historical SQL tools layer / chx |27.997974s,2CPUs; existing original image plus one diagnostic file, no dependency reinstall |
| **Current guarded serving layer / ch10** |23.123436s,2CPUs;6.782KiB uploaded context; original API base plus serving guard/read probe, no dependency reinstall |

Current API:
`acrptubundle7d804f70.azurecr.io/conversation/api@sha256:84ff9d2a31ddf2e71a75d26ca58433ce29e41af0eb46823c0a0c5d5ca4bbcaf0`.
Raw manifests/build failures and all image digests are retained in evidence.
No `.env`, `.azure`, credentials or whole parent workspace was uploaded.

Local API PID4676/session`ckm-api`, UI PID23408/session`ckm-ui`; loopback8115/5115,
both HTTP200 at final check. Dependencies live outside OneDrive under
`%LOCALAPPDATA%\ptu-eval\conversation`. Original React build/source integrity,
API imports/OpenAPI71 routes, ODBC18 and nginx configuration were verified.
The historical27 local assessments remain separate from current live results.
The local sample-user auth limitation is not production authentication.

```powershell
pwsh -File .\scripts\Start-Conversation.ps1 -Component Backend
pwsh -File .\scripts\Start-Conversation.ps1 -Component Frontend
pwsh -File .\scripts\Manage-ConversationCloud.ps1 -Action Status
```

Do not duplicate running listeners. Cloud URLs are in
`reports\conversation-cloud-runbook.md`. Important latest sessions:
`ckm-data-deploy`, `ckm-data-live-pass`, `ckm-sql-identity-repair`,
`ckm-final-identity-pause` (successful final pause). Never rerun the exported
model passes; cumulative usage is9 and the stored SQL data also blocks replay.

## Per-feature PTU dependence and remaining infrastructure

**PTUs are optional deployment capacity for eligible inference, not an app
prerequisite.** This entire evaluation used GlobalStandard.

| Feature | PTU relationship | Infrastructure / actual evidence |
|---|---|---|
| Upload/validation/source browsing | No PTU for storage/validation/read | Native API, SQL, Blob; durable3 records verified |
| Document/audio extraction | CU separately metered, not chat PTUs | CU/analyzers, Blob/Queue; not invoked; no separate Speech |
| Summaries/issues/resolutions/follow-ups | Only actual model inference could use compatible PTUs | OpenAI/identity/API;7 requests, qualified printer result |
| Entities/metadata enrichment | Model/agent work would count separately | Automatic AI blocked; heuristic fallback disclosed, not model enrichment |
| Embeddings | Separate model, not another chat deployment's PTUs | Embedding3-small/1536-dimensional schema; deployed,0 calls |
| Indexing/retrieval/citation fetch | Search operations are not PTUs | Basic Search and private access; literal two-call retrieval verified |
| Explore cross-call answers/citations | Agent turns may use provisioned inference when explicitly routed | Foundry agent/model/private tool architecture; currently blocked |
| SQL analytics/model-planned dashboard | Planning is inference; SQL execution/rendering are not | SQL/ODBC/model/API; real execution, semantic KPI/prose failures |
| Deterministic counts | No model/PTUs | Local and SQL counts verified; keep separate from generated labels |
| History/titles/insight cache | Storage not PTUs; titles/insights can add model calls | SQL/agent/model as applicable; title workflow untested |
| Hosting/auth/queues/monitoring/network | No PTU entitlement | ACA, Entra/RBAC, ACR, Private Link, DNS, Storage and logs separately accounted |

[Learn sizing guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing)
lists relevant GPT-5.2/5.1/4.1-mini model versions, but eligibility does not change
GlobalStandard into provisioned capacity. There is no general fixed-tokens-per-PTU
conversion. Use model/version/type, input/output mix, cache behavior, aggregate
feature/agent calls, concurrency and latency requirements, then minimums and scale
increments. Nine functional requests provide no valid CKM PTU sizing result.

Synthetic MCAPS only: Canada Central data services, EastUS2 compute and Sweden
Central/GlobalStandard processing are not Canada-confined. No DND sovereignty,
accreditation, production-authentication or statistical fairness assurance.
