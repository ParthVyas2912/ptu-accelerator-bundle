# Document Knowledge Mining evaluation

## Final evaluated state — original service core verified, paused; full app still partial

**Do not count DKM as a fully verified running browser app.** The original services performed genuine ingestion, document-scoped QA and corpus/two-document comparison with verified citations, then were paused as authorized. Stock AKS failed with`AKSCapacityHeavyUsage`; no cluster or AKS workers exist.

### Verified outcomes and limitations

| Feature/test | Expected | Actual |
|---|---|---|
| Mixed corpus |10 logical fixtures |**2/10 ingested:**2025 TXT and a one-page table-PDF rendition of2026 case02. Original case02 TXT and remaining8 cases were not uploaded. |
| Original ingestion pipeline |Real extraction, keywords, summaries, embeddings, Search and Mongo persistence |Both returned200. Client times27.825s and27.154s. |
| Table extraction |Annual training15 days/year; correct columns |Passed through original DI`prebuilt-layout` path; metadata contains15 and Allowance/Days-year columns. DI metrics:1 page,3 successful HTTP calls including polling,0 errors. |
| Metadata/filtering |Two Cedar Bay policies; Omar-only1; Neverland0 |Passed; person/place/type metadata correct. |
| Persisted source integrity |Uploaded and downloaded bytes match |Both SHA256 hashes match, including after restart. |
| Document-scoped QA |Only2025 source,10 annual training days, correct citation |Original backend`/Documents/Ask` returned200 in10.423s; answer2025/10days; citation document set contains only the selected2025 document despite both being indexed. |
| Corpus QA / two-document comparison |10 to15 days,+5/+50%,2026 supersedes2025,both cited |**PASS:** one explicitly approved repeat returned200 in15.103s; all facts and both citation IDs/names verified. Full9493-byte JSON persisted in owned private Blob before console and read back with matchingSHA256. Original lost attempt retained. |
| Summary grounding |No unsupported statements |**FAIL:** both persisted summaries prepend an unrelated Hello/how-are-you exchange. Raw outputs preserved, not stripped. |
| Public browser UI |Usable original frontend at approved CIDR |**BLOCKED:** observed403`RBAC: access denied`; unchanged exact allowlist, no bypass. |
| SDK retry regressions |Defaults preserved, explicit opt-in respected |**29 assertions passed** remotely; unset/empty factory identity, invalid-value rejection, eval0→1 fake transport attempt, eval2→3. No live model calls. |
| Existing frontend suite |Four Header cases execute |Fails before execution: missing`@testing-library/dom`;0 cases executed. |
| Restart/pause |Persist both documents, leave no running replicas |Verified Pause→Resume→health200/count2/source hashes→Pause. All retained revisions inactive, replicas0. |
| Remaining coverage |Full`/chat`, charts, handwriting, demographic counterfactuals |Not run. Fairness evaluation harness exists, but no demographic inference/observation or fairness claim was made. |

### Actual inference and PTU findings

**14/14 OpenAI attempts consumed, all account HTTP statuses200. Guard disarmed; no further inference authorized.** GPT-5-mini:7 requests,2061input +7424output =9485tokens. Embedding-3-large:7 requests,351input tokens. **Total9836tokens:2412input +7424output.** The approved repeat added513input +1552output tokens; all original12 records remain. Dedicated-account Azure Monitor counters/status aliases agree; aliases are not summed. DI remains separately billed:1page,3successfulHTTPcalls.

| Feature | Model dependence / PTU relevance | Separately required Azure infrastructure |
|---|---|---|
| Upload transport, readiness, metadata filters, original-file download |Transport/read/control itself has no inference. Upload triggers the paid inference stages below. |Blob/Queues, Cosmos MongoDB, backend/KM hosting, App Configuration, managed identity/private connectivity |
| PDF/table extraction |Document Intelligence, **not Azure OpenAI PTUs** |DI S0; per-page extraction billing |
| Keyword extraction and summarization |GPT-5-mini chat calls. Current deployments are **GlobalStandard, not PTU**. Compatible provisioned chat capacity would be an optional future configuration, not a prerequisite. |Backend/KM, storage/queues, App Configuration |
| Ingestion/query embeddings |Embedding-3-large **GlobalStandard** token usage; not PTU traffic in this deployment |Azure OpenAI embedding deployment plus AI Search Basic |
| Document/corpus RAG and comparison |Query embedding + GPT-5-mini answer generation; only the compatible chat-generation portion could use separately validated provisioned capacity |AI Search, existing data/identity/network services, original backend/KM |
| Full`/chat` final synthesis/suggestions |Additional chat inference exists in source but was **not exercised** |Original backend/frontend and conversation persistence; do not treat`/Documents/Ask` as full UI chat coverage |
| Frontend and application hosting |No PTU compute dependency |Original containers on Consumption ACA here; stock architecture requires AKS |

**No PTUs, reservations, load tests or PTU utilization measurements occurred.** The inspected official template exposes only Standard/GlobalStandard; no repo-supported provisioned deployment/reuse path was verified. Platform model PTU support is not DKM template support. These smoke results cannot size PTUs or establish a fixed tokens-per-PTU ratio. Any future provisioned model/version/region requires current availability/sizing validation: <https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing>.

### Current Azure resources, costs and source deviations

- Subscription`1feb53b2-854a-4ea7-b5a6-709b7d804f70`; own RG`accel-dkm-20260911`.
- Retained original seven resources: Search`srch-dkmeval0911a` Basic1/1; Cosmos MongoDB`cosmos-dkmeval0911a`; Storage`stdkmeval0911a` Standard_GRS; DI`di-dkmeval0911a` S0; OpenAI`oai-dkmeval0911a`; App Configuration`appcs-dkmeval0911a` Standard; UAI`id-dkmeval0911a`.
- OpenAI in East US: GPT-5-mini2025-08-07 GlobalStandard capacity10; embedding-3-large v1 GlobalStandard capacity50. No capacity changes during this phase. Existing shared Foundry/Search were not retrofitted.
- Own original services`ca-dkm-api`,`ca-dkm-kernel`,`ca-dkm-web` use shared Consumption environment`cae-ptu-bundle` and Basic ACR`acrptubundle7d804f70`, East US2. Each1CPU/2GiB,max1; **currently inactive/zero replicas**. API/KM internal; frontend restricted to174.112.74.34/32.
- Exactly3 own-resource PEs: MongoDB, Blob, Queue; private IPs10.246.2.11/.13/.10. Cosmos/Storage PNA remain Disabled. No security-policy change, protected-resource use, new Entra registration, or resource deletion.
- Exact IDs:`evidence/documents/current-resource-inventory.json`, main`result.json`, and private-endpoint requirements. Only`DPS/Documents` exists in the app database at400RU/s, alongside the original default400RU/s. No additional ChatHistory collection.
- **Cost:** original seven-PaaS baseline **$0.183/hour** + app-created400RU/s **$0.032/hour** +3 PEs **~$0.03/hour** = **~$0.245/hour paused (~$5.88/day)**. Three active replicas add~$0.324/hour: **~$0.569/hour active**. Shared allocations, ACR build runs, storage/operations, model tokens, DI pages, network and taxes are additional; these are retail estimates, not an invoice.
- Source SHA`7df8ed33a86dd4f0f9e7417e882039fd38556e59`, describe`v1.9.0-58-g7df8ed3`. Approved changes: worker-SKU parameterization, Docker context exclusions, and **opt-in**`DKM_EVAL_MAX_MODEL_RETRIES` in3 SK construction paths. Unset/empty preserves original factories. Prompts/business/output logic and original Dockerfiles are unchanged.
- Remote builds: backend`che`111s; Kernel Memory`chh`195s, using native Buildx inside ACR because the older dependency parser rejected original Dockerfile syntax. Clean upload contexts were app-only, about2.2MB/2.0MB, outside OneDrive; no credential files or parent workspace uploaded. Complete successes/failures, exact diff and regression logs are preserved.
- Recovery first inspected18 ownedBlobobjects/13eligible text-JSON contents plus both Mongo databases; no old comparison/history/stored responseID was recoverable. No reconstruction. The approved repeat's fullJSON is at `smemory/_dkm-evaluation/comparison14-result.json`,SHA256`99a60b96a6867bf9f96ff9297daf2d7497158b79f3cfa57f11a9357619327704`. Managed identity was used; no keys/SAS. UTF8/ASCII-safe transport and4offline capture checks passed. The probe/lock/result are evidence blobs, not ingested documents or new infrastructure.

### Restart, evidence and remaining limitations

Frontend endpoint: <https://ca-dkm-web.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io> (**observed403; currently paused**). Internal services:`http://ca-dkm-api` and`http://ca-dkm-kernel`. No new local8117/5117 listeners are claimed.

Use the tested persistent runbook:`reports/documents-cloud-runbook.md`. Controller:`scripts/Set-DocumentsRuntime.ps1 -Action Resume|Status|Pause`. Read-only authenticated exec verifies health/source persistence; do not widen ingress. Latest proof:`comparison14-final-runtime-state.json` and`comparison14-persistence.json`; earlier restart proof remains in`restart-verified-*.json`.

Primary evidence:`evidence/documents/result.json`,`comparison14-final.json`,`cloud-functional-result.json`,`functional-checks.json`,`comparison14-final-metrics-summary.json`. The full durable response is in`comparison14-read-result.json`. Earlier twelve-attempt evidence, including the lost response limitation, remains preserved in`retry-evaluation-final.json`,`final-metrics-summary.json` and`retry-phase-qa-corpus-uncaptured.json`.

**Final comparison budget exhausted:**14/14 used; no additional quality/probing calls. Publicbrowser403, both stored greeting defects,2/10coverage and full/chat coverage remain explicit limitations. Final proof:`comparison14-final.json`,`comparison14-final-metrics-summary.json`,`comparison14-final-runtime-state.json`. All replicas are zero, existing sources remain intact, and the one-shot guard is disarmed.

## Historical phase logs

Earlier snapshots below are retained for audit, not current runtime/call counts.

## Historical verified result — genuine cloud ingestion; full UI still gated

**The original DKM container core has now performed a genuine ingestion successfully. This is not a full browser-app E2E pass.** Stock AKS remains blocked; no AKS cluster exists.

- Original backend, Kernel Memory and frontend images were built and pushed to isolated `dkm/*:7df8ed3-aca20260911` tags in the approved shared Basic ACR. Original Dockerfiles/business logic remain unchanged. All dotenv/Azure credential paths are excluded from image contexts.
- Three original services deployed to shared **Consumption** ACA, each max1 replica. API/KM ingress is internal. Frontend allowlist was included at creation and remains exactly`174.112.74.34/32`.
- **Private DNS was verified inside the actual backend container:** Mongo`10.246.2.11`, Blob`10.246.2.13`, Queue`10.246.2.10`. Cosmos/Storage PNA remain Disabled. The three approved PEs succeeded through the parent's guarded helper.
- **Actual health/data checks:** Kernel Memory`/health`200; original Mongo-backed document API200. Frontend's initial0.5GiB Vite optimizer crashed; restoring the upstream2GiB memory envelope with1CPU allowed stable cloud Node execution.
- **Real upload:**`01-policy-2025.txt`,207bytes, source hash verified, original backend returned200 in**27.825s** (server processing25.7567s). Document ID`3951c54f0a974f79b9d8fc3d7e4591ad202609120125365840455`. Ingestion completed the original storage/queue/keyword/summary/embedding/Search/metadata flow.
- **Metadata tests passed:** Maya Chen, Cedar Bay, Policy and10days extracted; unfiltered count1, Cedar Bay filter1, Neverland filter0.
- **Quality failure found:** generated summary correctly mentions the policy but prepends an unrelated “Hello how are you?” exchange absent from the source. Do not count this as fully grounded summarization.
- **Actual model telemetry:4/12 requests used, all200** — GPT-5-mini2 requests,392input+1513output tokens; embedding-3-large2 requests,100tokens. **Total2005tokens.** Provider operation-average latency: GPT5975ms; embeddings159.5ms. Initial metric zeros were telemetry delay, not evidence of zero traffic.
- **Public UI remains blocked:** both ordinary HTTPS and isolated Edge return403`RBAC: access denied`, even after confirming matching actual clientIPv4/ARM allowlist and environment PNAEnabled. No ingress broadening or policy bypass was attempted.
- Upstream frontend unit suite now reaches Jest but fails before running its4cases because`@testing-library/dom` is missing.

**Retry-inclusive budget gate:** first-upload fan-out was4, not3: the embeddings base handler also embeds the synthetic summary directly. Stock worst-case next upload is13 attempts and full backend chat9, exceeding the remaining8. No additional paid action was initiated. Requesting a narrow test-only SDK retry-control change so a second policy upload4 + one full compare/chat3 can fit within11/12; this application-code change has **not** been made.

**Costs:** original seven-PaaS baseline **$0.183/hour** remains visible. The genuine app automatically created`DPS/Documents` at400RU/s, adding**$0.032/hour**; three PEs add~**$0.03/hour**. Current paused residual subtotal is~**$0.245/hour**; three fully active1CPU/2GiB replicas add~**$0.324/hour**, giving~**$0.569/hour** before shared allocations and variable usage. No free grant or invoice amount is assumed. No resources are deleted.

**Final current runtime state: paused and verified.** Executed Pause → Resume → real Kernel Memory health200 and backend200 with persisted document count1 → Pause again. Every retained revision now has`active=false, replicas=0`; resources/images/data remain intact. This verifies core restart/persistence, not the blocked public browser route. Detailed evidence:`evidence/documents/cloud-functional-result.json`; budget:`model-budget.json`; tested persistent runbook:`reports/documents-cloud-runbook.md`. All earlier sections below are historical phases.

## Historical phase — native builds pass; private dependencies require approved shared host

The official native Kernel Memory build now **succeeded:308 warnings,0 errors,5m14.67s**, alongside the prior successful backend build. The unchanged official frontend Dockerfile also built successfully; image SHA256`387bace500d977d46914e1f98cd2fddc1fe67bacb95e876085fc14a363e9e53c` (1,452,431,613bytes). These are **build results, not runtime or E2E passes**.

Azure confirms DKM **Cosmos and Storage publicNetworkAccess=Disabled**. This blocks the local data path and will not be bypassed. Search/OpenAI/DI/AppConfig remain PNAEnabled; identity authentication will be used. The parent approved hosting the original containers in the shared Consumption ACA environment, with at most one replica/service and no duplicate DKM services/models.

Parent private-network requirements are persisted in `evidence/documents/private-endpoint-requirements.json`: **Cosmos group`MongoDB`; Storage groups`blob` and`queue`**, including full IDs, authoritative required DNS zones and DKM runtime identity/AcrPull coordination. No Analytical/table/file/web/dfs private endpoints are needed for the active app.

Backend Docker build is running in the4GiB/two-CPU isolated builder; frontend image is ready for its isolated shared-ACR tag. DKM agent has not modified shared infrastructure. **Retained seven-PaaS fixed cost remains ~$0.183/hour plus usage; live-model budget remains0/12.** Health and genuine mixed-corpus results remain unproven.

## Historical outcome — AKS regional capacity rejection; genuine PaaS retained

The approved deployment reached Azure but **AKS failed with `AKSCapacityHeavyUsage` in Central US**, despite successful revised validation and an available worker SKU. Azure recommends another region. Post-check returns **ResourceNotFound** for `aks-dkmeval0911a`; its managed node RG is absent. There are **zero AKS workers and no cluster to stop**, not a tested/paused cluster.

**Seven resources were actually created and retained** in `accel-dkm-20260911`: Search `srch-dkmeval0911a`, Cosmos `cosmos-dkmeval0911a`, identity `id-dkmeval0911a`, Storage `stdkmeval0911a`, DI `di-dkmeval0911a`, OpenAI `oai-dkmeval0911a`, and App Configuration `appcs-dkmeval0911a`. ACR was not created because it depends on AKS. Nothing was deleted or changed in protected environments.

New model deployments **succeeded**: GPT-5-mini2025-08-07 GlobalStandard capacity10 and embedding-3-large v1 GlobalStandard capacity50. Model requests remain **0/12**; no ingestion or application E2E has passed.

Actual Cosmos database inventory is `default` with **400 RU/s manual throughput**; DPS collections have not been created. Current retained fixed retail estimate is **$0.183/hour (~$4.39/day)**: Search$0.101 + AppConfig$0.05 + Cosmos$0.032, plus storage/operations and any future usage. This is an estimate, not an invoice. These costs continue until the owner explicitly chooses a retention/cleanup action; no automatic deletion is authorized.

East US2 D4s_v6/D4as_v6/D4ads_v6 have only Zone2 restrictions, not Location restrictions; UK South alternatives are Location-restricted. **Not all regions are proven blocked.** To avoid a duplicate paid PaaS stack, the next useful path is the repository's **official native local-development setup**, now that genuine matching Azure dependencies exist. Frontend Docker dependencies installed successfully using the unchanged official Dockerfile in a4GiB/two-CPU builder; image export is still in progress. No public application ingress was opened.

Authoritative current inventory/error/cost evidence: `evidence/documents/deployment-capacity-result.json`. Following sections preserve prior phase history.

## Historical phase 3 — approved equivalent worker validated; deployment proceeding

At20:12 the coordinator approved a compatible available x64,4-vCPU/16-GiB worker with the same initial2/max2 and <=$1.50/hour envelope. **Central US `Standard_D4s_v6` has no Location restriction; only Zone3 is restricted.** The unchanged template uses nonzonal placement. Regional and Dsv6-family quota are each0/100.

- Genuine runtime configuration uses Azure Blob/Queues/Search and remote OpenAI, not ephemeral local storage or CPU-specific inference. D4s_v6 requires Gen2 and managed OS disk; Linux AKS automatically uses Gen2 on Gen2-only sizes.
- Sole tracked source deviation:8 insertions/1 deletion in `infra/main.bicep`, adding `aksNodeVmSize` with the original default and replacing the one worker literal. No other resource/SKU/node-count/zone setting changed.
- Compilation succeeded with five existing warnings. Both upstream parameter mappings and revised Azure group validation passed.
- Central US Cosmos regional API reports Online and subscription regular/zone access allowed. DI S0 has no SKU restriction. Remaining fixed-service provider metadata supports Central US; all required providers are registered. This does not guarantee actual creation capacity.
- Authoritative Central US Linux retail rate: **$0.228/node-hour**. Revised full fixed estimate: **$0.914775/hour expected**, **$1.034775/hour conservative**, planning allowance$1.10/hour plus tiny usage charges. Exact inventory and remaining SKU defaults stay as in the approved proposal.
- Evidence: `evidence/documents/equivalent-worker-preflight.json`; compiled template `dkm-adapted-main.json`; selected value in `approved-parameters.json`.
- No E2E result is claimed by this preflight. Earlier exact-SKU failure remains below as history.

## Phase 2 — explicitly approved short isolated AKS test: blocked by Azure SKU availability

The coordinator granted a DKM-only no-AKS exception at 19:49 -04:00 on 2026-09-11, with a $1.50/hour fixed-infrastructure decision threshold, exact D4ds_v5 initial2/max2 envelope, new Standard/GlobalStandard models only, and mandatory cluster stop after testing. The earlier no-AKS conclusions below are retained as **phase-1 history**, not the current authorization.

- Exact proposal/parameters saved before provisioning: `evidence/documents/approved-deployment-proposal.md` and `approved-parameters.json`.
- Fuller Central US estimate: **$0.968775/hour expected**, about **$1.088775/hour conservative**, plus small token/page/operation usage.
- New RG **`accel-dkm-20260911`** was created successfully. No billable resources have been deployed yet.
- Official ARM group validation succeeded with no reported error.
- Subsequent exact SKU inventory reports **D4ds_v5 NotAvailableForSubscription in Central US**, despite100 available regional/family quota. Validation success does not establish physical/subscription SKU availability.
- The exact same SKU also reports **NotAvailableForSubscription in East US, East US2 and UK South**. Central US/East US/UK South all have0/100 regional and Ddsv5-family vCPU usage. This is a subscription/SKU availability restriction, not insufficient numeric quota.
- Final guarded resource inventory of `accel-dkm-20260911` returned **`[]`** at20:09 -04:00. Only the nonbillable empty RG exists; it was not deleted.
- **No billable template deployment was started**, because doing so despite the known AKS restriction could leave other billed resources behind without a working app. No alternate/larger VM, quota increase, policy change or bypass was attempted.
- No app is running; no model requests or E2E flows ran. **Do not label this “tested but paused”: no cluster exists to stop or restart.** There is no verified restart command.
- **Actual new fixed infrastructure cost remains $0.** The ~$0.36–$0.48/hour paused residual estimate in the proposal is hypothetical; no Search/AppConfig/Cosmos/disk resources were created.
- Machine-readable outcome: `evidence/documents/approved-preflight-result.json`. Next action is coordinator resolution of the exact approved SKU's subscription availability in a compatible region.

## Phase-1 history — before the DKM-only approval exception

**Phase-1 status: first-pass evaluation completed; deployment and full application E2E were BLOCKED. Do not count phase-1 results as a verified running full app.**

- Repository: https://github.com/microsoft/Document-Knowledge-Mining-Solution-Accelerator
- Clone: `C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\Document-Knowledge-Mining-Solution-Accelerator`
- Commit: `7df8ed33a86dd4f0f9e7417e882039fd38556e59`, committed 2026-09-07; nearest reachable tag `v1.9.0`, 58 subsequent commits. This is not a tagged release checkout.
- Subscription: `1feb53b2-854a-4ea7-b5a6-709b7d804f70` (`ME-MngEnvMCAP687593-partvyas-1`).
- Tenant: `a600acd0-3028-4689-8402-3b471d7d924d`.
- Resources created/reused: **none**. Live model/extraction/search requests: **zero**.
- Proposed isolated resource group, only if separately approved: `rg-ptu-documents-demo`. No group was created.
- Protected SpecSuite and Planetary resources were not called, reused, modified, or granted permissions.

## Exact documented minimum deployment proposal

The default development configuration disables private networking, monitoring, redundancy and scalability, but **does not remove AKS**. No documented parameter makes the complete accelerator serverless or local-only.

| Required item | Authoritative default/minimum configuration | Cost implication |
|---|---|---|
| AKS | Unconditional module; Linux `Standard_D4ds_v5`, **2 initial nodes**, autoscaling enabled, min 1 / max 2 | VM worker compute, OS disks, load balancer/IP; forbidden under current contract |
| Container Registry | **Standard**, hard-coded in main template | Daily fixed charge |
| App Configuration | **Standard**, hard-coded | Daily fixed charge; mandatory runtime dependency of both .NET services |
| Azure AI Search | **Basic**, one replica and one partition | Hourly fixed charge |
| Cosmos DB | MongoDB 7.0, Standard offer; `EnableServerless` is commented out | Provisioned-throughput billing; exact collection throughput requires deployment details |
| OpenAI | New S0 account; `gpt-5-mini` version `2025-08-07`, GlobalStandard; `text-embedding-3-large` v1 | PAYG token charges, not PTU |
| Model capacity | Defaults 150k GPT / 100k embedding TPM. Bicep lower bound 10 for both; post-deployment guidance minimum 10k GPT / **50k embedding** | Quota, not a purchased PTU or automatic cost commitment |
| Document Intelligence | New S0 FormRecognizer account | Separately billed document extraction/pages |
| Storage | Blob/queue storage | Data, operations and retention |
| Managed identity / RBAC | User-assigned identity, role assignments; Entra app registration/auth setup | Coordination/security prerequisites |

Only **Log Analytics workspace reuse** is documented in the deployment guide. There is no documented Foundry/OpenAI/Search existing-resource parameter for this accelerator. The permitted shared models (`gpt-5.1`, `gpt-4.1-mini`, `text-embedding-3-small`) do not match its constrained template models. No Foundry retrofit, endpoint substitution, model capacity increase, or speculative IaC rewrite was attempted.

**Recommendation to parent: do not provision this architecture under the present low-cost/no-AKS contract.** Preserve the repository and test evidence, and request an already deployed isolated compatible DKM environment or an upstream-supported non-AKS deployment. The parent-directed `write_agent` attempt could not resolve the coordinator ID; this report preserves the early proposal.

### Public retail cost floor (not a quote or approval)

Azure Retail Prices API queried during this evaluation for **Central US**, a region recommended in the repository. Prices returned in USD:

- Linux D4ds v5 on-demand, non-Spot: **$0.255/hour/node**.
- Search Basic: **$0.101/hour/unit**.
- ACR Standard: **$0.6666/day**.
- At the template's two-node initial configuration, these **three items alone** cost about **$15.33/day**, or **$466.31 per 730-hour month** (ACR daily charge prorated to 730/24 days).
- Even a one-node state would make those items about **$9.21/day / $280.16 per 730-hour month**. The template specifies two nodes; this is not a claim that changing to one is a supported deployment parameter.
- Excludes App Configuration, Cosmos provisioned throughput, disks, load balancer/IP, storage, extraction, model tokens, networking and taxes. MCAPS discounts/credits are not assumed. Full cost is higher.

Source: `https://prices.azure.com/api/retail/prices`, filters for Central US, Consumption, `Standard_D4ds_v5`, Search Basic and Container Registry Standard. No subscription data was sent to this public pricing endpoint.

## Two deployment paths investigated

1. **Official cloud path:** `azd up` followed by `Deployment/resourcedeployment.ps1`; requires prohibited AKS and unapproved billable infrastructure. Not executed.
2. **Official native local-development path:** `docs/LocalDevelopmentSetup.md` explicitly requires a pre-existing deployed DKM Azure environment. Frontend, backend API and Kernel Memory can run locally, but both backend processes unconditionally connect to Azure App Configuration and then Azure services. Its instructions to change the existing App Configuration Kernel Memory endpoint are not safe to apply to unrelated shared environments and were not executed. Dockerfiles package the same services; no standalone Compose/emulator deployment was found.

Region caveat: README has stale fixed-region claims, whereas `infra/main.bicep` exposes OpenAI location and places Document Intelligence in `solutionLocation`. Region-pair dictionaries do not include Canada Central. No Canadian-region deployment compatibility is claimed and no quota reservation/change was made. README lists App Service, but the actual inspected deployment runs the three app workloads on AKS; an App Service cost was not invented.

Read-only inventory confirmed the permitted account's GPT-5.1 (`2025-11-13`, GlobalStandard), GPT-4.1-mini (`2025-04-14`, GlobalStandard), and embedding-3-small (`1`, Standard). They were not invoked. The App Configuration inventory command emitted an Azure CLI command-module load timeout, so its empty array is **not reliable proof of no App Configuration resources**.

## Tests and runtime evidence

| Check | Expected | Actual |
|---|---|---|
| Official backend .NET build | Build unmodified host and library | **PASS**: 148 warnings, 0 errors, 14m27.91s including restore |
| Backend startup on `127.0.0.1:5117` | Start actual API | **BLOCKED**: unhandled `ArgumentException: Invalid URI: The URI is empty`, `AppConfiguration.cs:20`, invoked at `Program.cs:19`; no listener |
| Backend `dotnet test` | Find and execute tests | Exit 0 but **no test output or test project**; not counted as a test pass |
| Upstream Bicep parameter validator | Both default/WAF parameter files match main template | **PASS**: 2 files, 0 errors, 0 warnings; native JSON is an empty findings array `[]` |
| Locked frontend dependencies | Frozen Yarn install | **FAILED twice**: official feed `ESOCKETTIMEDOUT` for `@azure/msal-browser` 4.30.0, then `@fluentui/react` 8.125.5. Retry used network concurrency 2 / timeout 15s. Neither changed lockfile |
| Frontend build | `tsc && vite build` | **BLOCKED**, exit 1: `tsc` not found because installation was incomplete |
| Upstream Header tests | Four cases | **BLOCKED**, exit 1: `jest` not found; no cases executed |
| Kernel Memory build | Complete actual service | **INCOMPLETE**: official project dependencies restored; initial analyzer-enabled compile stopped after partial progress. Reduced-memory retry (`RunAnalyzersDuringBuild=false`, no restore, one MSBuild worker) also stopped without a completed service DLL |
| Upstream pytest E2E discovery | Collect, not invoke paid operations | **BLOCKED**, exit 1: `No module named pytest` during incomplete isolated install. Full browser suite not run |
| Frontend HTTP | Response at `127.0.0.1:8117` | Connection refused; curl exit 7, 2.026s, no HTTP status |
| Backend HTTP | Response at `127.0.0.1:5117` | Connection refused; curl exit 7, 2.034s, no HTTP status |
| Offline synthetic corpus | Ten small valid files with ground truth | **PASS**: 10 files / 2,590,122 bytes; 10 SHA-256 checks, 4 image decode checks, 2 PDF structural checks |

These are component/readiness and fixture checks, **not proof of ingestion, retrieval, extraction or grounded chat**. No running app, UI screenshot or successful inference endpoint is claimed.

The host had approximately 1.6–1.9 GiB free physical memory of 31.7 GiB during the slow installs/builds. Both complete-service Kernel Memory attempts were stopped to bound local resource use. This is an incomplete build, not an asserted source compilation defect. The isolated Python install was stopped after downloads and partial installation; it is **not a ready E2E environment**. Pillow was available and used successfully for offline fixture generation.

### Functional corpus and expected/actual outcomes

Corpus: `test-data/documents/`; generator: `scripts/documents-corpus.py`; ground truth and individual file hashes: `test-data/documents/manifest.json`.

- Formats: four TXT, two PDF, two PNG, one JPG, one TIFF.
- Fictional policy versions give 10 training days in 2025 and 15 in active 2026.
- Metadata includes people, four fictional locations, and document types.
- Table fixture has actual training CAD150 / total actual CAD330.
- Chart fixture has actual36/planned40 = 90%.
- Handwriting-style PNG says six binders due 2026-10-03. It uses synthetic typography, **not genuine handwriting**, so it cannot establish real handwriting accuracy.
- Paired synthetic gender fixtures contain identical job/training facts. These prepare a limited fairness check; no model bias test or broad demographic fairness certification was possible.

| Required full-app test | Expected | Actual |
|---|---|---|
| Ingest 10 documents | All indexed with metadata | **BLOCKED**; 0 uploaded, 0 indexed |
| Filter by person/place/type | Cedar Bay returns 01/02/04/06; Policy returns 01/02 | **BLOCKED**; no Search data-plane requests |
| Single document vs corpus | 01 alone answers 10 days; current corpus answer 15 days with appropriate citations | **BLOCKED** |
| Compare two documents | Increase of 5 days / 50%; cite both policies | **BLOCKED** |
| Table/chart/handwriting-style | Answers trace to the correct source | **BLOCKED**; no Document Intelligence requests |
| Missing evidence / fairness | Do not invent a CEO salary; same extraction for matched training records | **NOT RUN** |

Full-app functional score: **0 passed, 5 blocked** for the five requested feature groups. This is not a measured 0% model accuracy.

### Processes and reproducibility

**No DKM service or container is left running.** Ports 8117 and 5117 had no listeners at final verification. All DKM install/build/runtime command trees still pending were stopped; no cloud resources were deleted.

Isolated dependencies/cache:

```text
C:\Users\partvyas\AppData\Local\ptu-eval\documents\nuget
C:\Users\partvyas\AppData\Local\ptu-eval\documents\npm-cache
C:\Users\partvyas\AppData\Local\ptu-eval\documents\yarn-cache
C:\Users\partvyas\AppData\Local\ptu-eval\documents\venv
```

Backend build, from the repository root:

```powershell
$env:NUGET_PACKAGES='C:\Users\partvyas\AppData\Local\ptu-eval\documents\nuget'
dotnet build App/backend-api/Microsoft.GS.DPS.Host/Microsoft.GS.DPS.Host.csproj --configuration Release --verbosity minimal
```

Actual attempted backend start, from `App/backend-api/Microsoft.GS.DPS.Host`:

```powershell
$env:ASPNETCORE_ENVIRONMENT='Production'
$env:ASPNETCORE_URLS='http://127.0.0.1:5117'
dotnet .\bin\Release\net8.0\Microsoft.GS.DPS.Host.dll
```

This command currently fails as recorded above. There is **no known successful restart command** for a working complete app without its missing prerequisites. A future native frontend launch must explicitly override the upstream `host: true` with `vite --host 127.0.0.1 --port 8117`; it must not use mock servers as evidence. Kernel Memory requires a third separately coordinated loopback port (the guide defaults to 9001); none was allocated or opened here.

Prerequisites before any full restart: a compatible **isolated** pre-existing Azure DKM environment, documented App Configuration/identity configuration, finished frontend/Kernel Memory dependencies, a third port allocation, and a staged inference budget. Do not change shared App Configuration values or expose the unauthenticated development API publicly. Runtime credentials must remain in identity/environment/secret stores, never in this bundle.

### Evidence references

- `evidence/documents/result.json`
- `evidence/documents/bicep-parameter-validation.json`
- `test-data/documents/manifest.json`
- Repository working tree remained free of tracked changes; no application or IaC replacement was made.
- Key source files at the recorded SHA: `docs/DeploymentGuide.md`, `docs/LocalDevelopmentSetup.md`, `docs/AVMPostDeploymentGuide.md`, `docs/QuotaCheck.md`, `docs/DataProcessing.md`, `infra/main.bicep`, `App/backend-api/Microsoft.GS.DPS.Host/AppConfiguration/AppConfiguration.cs`, and `App/kernel-memory/service/Service/Program.cs`.

## PTU interpretation

Potential PTU-addressable inference: multimodal/context extraction performed by the chat model; document summarization; keyword/entity extraction; query answering and follow-up suggestions. Embeddings are a distinct deployment/cost stream and must not be assumed covered by a chat PTU allocation. Document Intelligence OCR, Search, AKS, Cosmos, App Configuration, ACR and storage are separately billed.

No provisioned deployment is used. Actual PTU utilization, live token counts and inference latency are **not measured**, not zero-valued performance claims. First-pass cap is 12 live model requests including retries; current actual count is zero. Ingesting ten documents can invoke multiple inference stages per document, so even a future configured deployment needs a staged budget before bulk ingestion.

### Per-feature PTU dependence and Azure infrastructure

**No DKM feature inherently requires a PTU purchase.** PTU is an inference-capacity/deployment choice, not a feature dependency. At this SHA, the template only allows `Standard` or `GlobalStandard` model deployment types; it does not expose a provisioned deployment or compatible existing Foundry reuse path. The potential PTU inference below is therefore architectural classification, **not a deployed or tested configuration**.

| Feature / stage | Model work and potential PTU dependence | Azure infrastructure outside chat-model PTU | Actual verification |
|---|---|---|---|
| File upload and ingestion orchestration | Upload/queue scheduling has no direct model or PTU dependence; downstream stages below do | AKS backend/Kernel Memory workers, Blob and Queue Storage, App Configuration, Cosmos state | 10 local fixtures validated; 0 uploaded |
| OCR and basic document extraction | Document Intelligence processing is **not chat PTU traffic** | Document Intelligence S0, storage, AKS processing workers | Blocked; 0 extraction calls |
| Chart/image/handwriting context interpretation | Hybrid pipeline can add multimodal GPT inference; that inference could use compatible provisioned capacity in a supported future configuration. OCR remains separate | Document Intelligence, Blob Storage, AKS; stored/indexed results in Cosmos/Search | Blocked; handwriting fixture is typography only |
| Document summaries and entity metadata | GPT summarization and keyword/entity prompts produce inference traffic; no mandatory PTU purchase | AKS, queues/storage, Cosmos, Search and App Configuration | Blocked |
| Vectorization and indexing | `text-embedding-3-large` calls are a separate model stream, **not covered by chat-model PTU**; index writes are not model inference | Azure AI Search Basic, queues/storage and AKS workers | Blocked; 0 embedding/Search data-plane calls |
| Person/place/document-type filtering | Facet/filter execution uses indexed metadata, not a chat-model call. Producing that metadata during ingestion is a separate inference stage above | Azure AI Search Basic; AKS API/frontend and App Configuration | Blocked |
| Single-document and corpus chat with citations | Grounded answer generation produces GPT inference; retrieval may also invoke embeddings. Citation/source retrieval itself is not a separate PTU allocation | Search, Blob document/source access, Cosmos chat state, AKS backend/Kernel Memory/frontend, App Configuration | Blocked; no answer/citation accuracy measured |
| Compare two documents / follow-up questions | GPT synthesis and suggestion generation produce inference; prompt size depends on retrieved context. No fixed calls-per-document or PTU-per-question assumption | Same retrieval, document storage, chat state and application services as grounded chat | Blocked |

ACR Standard stores/builds the application images and is billed independently across these features. AKS worker compute, App Configuration, Cosmos, Search and networking remain chargeable even when model request count is low or zero.

Sizing reference verified on 2026-09-11: [Microsoft Learn — Determine PTU sizing for a workload](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing). It lists provisioned support for GPT-5.1, GPT-4.1-mini and the repo's GPT-5-mini. **Platform model support does not establish repository reuse support, regional capacity, approved provisioning, or compatibility with a different model.**

For those text-model sizing estimates, use model/version/deployment-specific input throughput, output-token weighting, peak request rate, prompt/response sizes, cache rate, and minimum/scale increments. Do not use a universal “one PTU equals a fixed number of tokens” conversion. Representative provisioned benchmarks are required before making utilization/performance claims; build checks, localhost checks and PAYG smoke calls are not PTU tests. No sizing estimate or provisioned benchmark was performed here.

## Shared guard and identity update

- Shared account `edcfoundryhack01` has `disableLocalAuth=true`. Any future **documented compatible** access must use Entra credentials such as `DefaultAzureCredential` or `AzureCliCredential`; never fetch/use keys or enable local auth. This evaluation made no data-plane calls to that account.
- Shared `edc-hack-search` is Basic, one partition and one replica. This does not make it an approved/documented reuse target for DKM.
- `evidence/protected-resources.json` is the authoritative expanded protected-ID inventory, including additional SpecSuite/specsmith and managed resource groups. None were called, reused or mutated.
- `Invoke-LabAz.ps1 -AzArguments <string[]>` is the required guard for subsequent supported Azure CLI actions. Passing the guard is **not billing approval**. No additional Azure CLI or provisioning action was needed for this report update.
- Every DKM infrastructure proposal is identified as **Document Knowledge Mining (DKM)**. The no-AKS/no-new-billable-infrastructure decision is unchanged.
- Shared preflight confirms tenant/subscription and successful azd authentication. Installed azd **1.23.7 satisfies** this repository's `>=1.18.0 !=1.23.9` requirement; no azd update is needed.
- The later shared memory check reports approximately 12 GiB free host RAM and a 15.5 GiB Docker limit. That is a later observation than the low-memory build checks above. No DKM builds/emulators remain running and none are being relaunched.
- Canada Central retail reference rates supplied by the coordinator are not substituted into the Central US estimate above. DKM's inspected template does not deploy an App Service plan, so B1/S1/P1v3 App Service rates do not establish a supported cheap hosting alternative.
- **Immediate DKM approval proposal: create nothing.** The exact required architecture is already inspected and conflicts with the no-AKS contract. Request access to a pre-existing isolated compatible full DKM environment or an upstream-supported non-AKS path; do not treat an unapproved architecture rewrite as a deployable proposal. No new PTUs are required for a modest Standard-model functional test.

## Recommendation

**Resolve approved-SKU availability before billable deployment.** The DKM-only exception removed the initial contractual AKS blocker and the fuller estimated fixed cost falls below the $1.50/hour threshold. The actual remaining blocker is `NotAvailableForSubscription` for the approved D4ds_v5 worker in four checked regions. A compatible isolated pre-existing DKM environment remains another option. No alternative framework, mock backend, static substitute UI, speculative IaC rewrite, undocumented Foundry retrofit, larger worker, or quota/policy bypass was used to inflate the running-app count.
