# PTU Bundle Accelerator

## MCAPS deployment, functionality and capacity evaluation

**Final evaluation report | September 12, 2026**

Evaluation window: September 11-12, 2026 UTC. Subscription: ME-MngEnvMCAP687593-partvyas-1 (`1feb53b2-854a-4ea7-b5a6-709b7d804f70`). All new functional tests use synthetic, unclassified demonstration data. This is not a DND deployment, production certification or PTU performance benchmark.

## 1. Executive assessment

Seven accelerator repositories were assigned to separate implementation agents. Existing SpecSuite and Planetary Explorer deployments were protected and inventoried, not retested or redeployed. GitHub Copilot BYOK was assessed as a separate configuration track, not represented as another successfully deployed application.

The ten additional portfolio ideas are outside this deployment pass.

The intended offer is sound: sell a useful portfolio of supported business outcomes, onboarding and deployment services, then size the compatible model capacity behind the actual demand. The evidence does not support selling a fixed PTU quantity or claiming that every Azure component consumes PTUs.

**No PTUs or reservations were purchased.** The tested inference deployments use Standard or GlobalStandard capacity. Therefore the measured tokens and request counts are evidence of model demand, not measured provisioned utilization.

**This is not yet a seven-app customer-ready bundle.** Three apps passed their selected core scope, Content passed a limited native missing-document workflow, and three apps retain central workflow or semantic failures. These are scope-specific results, not blanket production acceptance.

| Application | Evaluation result | Verified scope and main limitation |
|---|---|---|
| Chat With Your Data | Selected core verified | Eight selected criteria passed using the adapted local runtime; Azure Functions hosting was not exercised. |
| Modernize Your Code | Selected API workflow verified | Native upload/process/download and malformed-file isolation passed; real source/target database equivalence is not established. |
| Document Knowledge Mining | Selected core verified | Ingestion, filters, cited QA and two-document comparison passed; only two of ten fixtures and no full browser journey. |
| Content Processing | Limited native E2E verified | Three submitted documents completed and missing police evidence was correctly flagged; four-document happy path unpassed and provider-filter warning unresolved. |
| MACAE | Partial | Planning, approval and specialists ran, but final synthesis ended in error and a factual/context mismatch remains unresolved. |
| Customer Chatbot | Partial | Private catalog/API and specialist routing ran; the native chat answer was a generic refusal, not a grounded business answer. |
| Conversation Knowledge Mining | Partial | Persistence, retrieval, model-planned analytics and durable HTTP data serving ran; KPI, prose and context defects plus hosted Explore limitations remain. |

For an initial guided demonstration, lead with the proven CWYD, Modernize and DKM scenarios, alongside the user's existing SpecSuite/Planetary deployments. Content's missing-evidence scenario is useful only with its explicit limitations. Keep MACAE, Chatbot and Conversation in an engineering validation track rather than selling them as ready-to-run customer solutions.

All new cloud application replicas were paused and inference allowances closed after evaluation. The coordinator also observed SQL **Paused at 06:21 UTC**. Retained services still have an approximately **USD 20/day reference baseline**, excluding usage and other listed charges.

## 2. What actually depends on PTUs

**None of the seven applications inherently requires provisioned capacity.** Compatible pay-as-you-go deployments can provide their model inference. The important distinction is between functions that require a model, functions supplied by separately billed AI services, and ordinary application infrastructure.

A model-dependent feature consumes a customer's PTUs only if its real client, model, API and endpoint configuration routes those requests to a compatible provisioned deployment. A project name containing "PTU", an Azure subscription, or an Azure AI service being present does not establish that routing.

There is no defensible single percentage of "the application" that is PTU-dependent. An upload screen, a database write, an agent planning call and a generated answer are different operations. The following mapping is more useful than an arbitrary percentage.

| Application | Model-dependent functionality and traffic shape | Work outside the chat-model PTU deployment |
|---|---|---|
| Chat With Your Data | Grounded answer generation, comparisons and synthesis. Interactive prompts include retrieved passages and conversation context; re-ingestion and queries can also invoke embeddings. | File handling, queue/worker execution, vector storage and retrieval, metadata, UI and hosting. Embeddings used a separate deployment in this lab. |
| Modernize Your Code | Translation, candidate selection and semantic review. A single submitted file can invoke several agents. Long source inputs, generated code and retries can create output-heavy batch demand. | Upload/download, ZIP creation, job state, storage, native syntax tools and execution-based validation. A model verdict does not prove database-engine equivalence. |
| Multi-Agent Custom Automation Engine | Safety checks, planning, routing, specialist reasoning and final synthesis. One business workflow can generate many model requests and repeated context. | Human approval, workflow state, MCP/tool execution, business-system transactions, document storage and search. Foundry-hosted tool connectivity needs its own working network path. |
| Content Processing | Customer-deployed model calls for schema mapping, safety review, summary and gap analysis. Multi-document claims multiply the number and size of calls. | Content Understanding analyses and any service-managed model usage, blob/queue traffic, Mongo state, configuration, orchestration and UI. CU usage must be accounted for separately. |
| Customer Chatbot | Grounded product/service answers and agent reasoning. Demand is conversational and latency-sensitive; retrieval may invoke a separate embedding model. | Catalog and order data, search, storefront/API hosting and deterministic lookups. Voice, if enabled, adds a distinct realtime/speech path and billing model. |
| Document Knowledge Mining | Document summaries, grounded questions and corpus comparisons. Ingestion creates embedding demand; long-document or multi-document synthesis can be output-heavy. | OCR/Document Intelligence, file persistence, search, metadata, Mongo state, Kernel Memory hosting and UI. Embeddings do not automatically use the chat deployment's PTUs. |
| Conversation Knowledge Mining | Conversation analysis, summarization and question answering, plus the selected application's model-driven retrieval/SQL path. Measure each actual pipeline separately. | Transcript ingestion/extraction, SQL, search, blob storage and app hosting. Audio processing and CU are not automatically chat-model PTU consumption. |
| SpecSuite, existing | Repository understanding, specification and code generation are potential long-context/output workloads. Not measured in this evaluation. | Repository access, application state, hosting, development tools and validation. |
| Planetary Explorer, existing | Intent interpretation, agent reasoning and generated explanations can use model inference. Not measured in this evaluation. | Geospatial queries, imagery/data access, map rendering and geospatial compute. |
| GitHub Copilot BYOK, assessed only | Supported client requests can consume a customer deployment's capacity: repository context, chat history, tool loops and code output determine demand. | Copilot licensing/policy, client functionality not routed to that provider, development tools and supporting Azure services. |

**PTUs do not repair** authentication, service firewalls, missing private egress, regional AKS/Search capacity, serialization, invalid SQL, inaccurate answers or application error handling.

## 3. Interpretation of the functional evidence

These are small, deliberately bounded demonstrations, not production acceptance tests. A successful resource deployment is not an application test. HTTP 200 is not proof of a correct answer. A workflow marked Completed is not necessarily successful if its document-level outcomes contain errors.

The evaluation distinguishes native application behavior, hosting/dependency adaptations, individual verified workflows, negative cases and untested features. Local compatibility bridges and Container Apps hosting are disclosed; they are not described as unchanged official cloud deployments.

### Chat With Your Data

**Verified selected core scope: 8/8 criteria.** The real React interface and FastAPI backend ran locally. The upstream ingestion implementation ran through a local queue harness with pgvector and Azurite; the Azure Functions host itself was not exercised.

Five factual answers and source citations, an absent-answer response, a cross-document comparison and an actual replacement from 73 to 91 credits were verified against persisted source/index/history evidence. This was more than a direct model connectivity test. Eighteen persisted-evidence assertions and 23 upstream ingestion unit tests support the selected scope.

The evaluation consumed its closed allowance of 16 instrumented attempts, including early authentication, timeout and unsupported-parameter failures. Reported chat usage was 2,507 input and 210 output tokens; embeddings used 597 input tokens separately. Two recorded API durations were 21.77 seconds for the grouped-question request and 3.52 seconds for the replacement query. These are individual observations, not P95 or throughput results.

Local addresses: `http://127.0.0.1:5112/` and API `http://127.0.0.1:8112/`. At closure, the API was read-only, the worker disabled and inference disarmed at 16/16. Data and evidence remain. Session-attached processes are not a persistent hosted service; use the recorded start procedure and explicitly authorize a new allowance before any further inference.

**Infrastructure:** no new Azure hosting was required for this adapted-local evaluation. It reused the non-protected EDC model account through Entra authentication and the canonical OpenAI endpoint. Production deployment still needs hosted web/API/ingestion compute, a supported persistent retrieval store, file/queue storage, identity, networking and monitoring.

Evidence and operation: `reports\cwyd.md`, `evidence\cwyd\result.json`, `scripts\Start-Cwyd.ps1`, `scripts\Stop-Cwyd.ps1`.

### Modernize Your Code

**Verified an adapted-cloud native API upload/process/download workflow.** Two SQL files were submitted: the malformed file was isolated as an error and produced no translation; the valid Informix NVL example passed the Migrator, Picker, native syntax tool and Semantic Verifier. The original ZIP download contained the valid translated SQL.

The output parsed and matched five synthetic SQLite rows after explicitly documented rewrites. This does not establish Informix-to-SQL Server execution equivalence. An earlier procedure translation changed interfaces without sufficient warning and remains a quality concern.

A false-success condition accepting "No migration" was fixed with 11 focused regression tests. Nine guard/identity tests and actual private Blob ETag accounting supported bounded execution.

The closed evaluation used 10 model requests: 13,203 input and 2,264 output tokens, with zero cached tokens reported. The full API batch added six requests to the earlier component tests, processed in 39.06 seconds and completed the API evaluation in 44.15 seconds.

**Infrastructure:** private LRS Hot Blob storage in Canada Central; a successful East US 2 NoSQL Serverless Cosmos account after Canadian availability failures; per-app identities; two private endpoints; API and UI on the shared Consumption Container Apps environment. It reused EDC GPT-5.1 in Canada East rather than creating a new model deployment. A failed Canadian Cosmos resource is retained and must not be represented as a working database.

Both cloud apps were verified at zero replicas. The API revisions were inactive/Stopped; the UI initially reached ScaledToZero, then the coordinator deactivated its remaining active revision. A top-level ARM Running flag does not establish active compute. The current authorization is 10/10, zero remaining. A historical Blob ledger cap of 12 is not permission to consume more; inference remains disarmed.

Public browser access returned HTTP 403 from the evaluator. The successful API flow was collected through authenticated Azure control-plane execution, not a completed public browser journey.

Evidence and operation: `reports\modernize.md`, `reports\modernize-cloud-runbook.md`, `evidence\modernize\result.json`, `evidence\modernize\coordinator-replica-state.json`.

### Document Knowledge Mining

**Verified selected ingestion, metadata/filtering, document QA and corpus comparison.** Only 2 of the 10 planned logical fixtures were ingested, including a policy-table PDF. Positive and negative filters, source hashes, document-scoped answers and citations were checked.

The final comparison correctly returned 2025: 10 days; 2026: 15 days; increase: 5 days/50%; and that 2026 supersedes 2025, citing both persisted sources. A previous response was lost during Unicode console capture and could not be recovered. The single approved repeat saved full JSON to private Blob before export; read-back matched its SHA256.

Final usage was 14/14 provider attempts, all HTTP 200, with 2,412 input and 7,424 output tokens across chat and embedding deployments. Document Intelligence was separate: one page and three successful HTTP calls. Source summaries retain an unrelated greeting defect; the output was not cleaned up to fabricate a pass.

**Infrastructure:** Basic Search, RU-based Mongo Cosmos, LRS Blob/Queue storage, Document Intelligence S0, an OpenAI account with GPT-5-mini and embedding-3-large, App Configuration Standard, managed identity and three private endpoints. The original API, Kernel Memory service and frontend run as an explicitly disclosed Container Apps hosting adaptation.

The stock AKS node SKU was unavailable across multiple regions. An approved equivalent-SKU attempt then hit AKSCapacityHeavyUsage. No AKS cluster, workers or node resource group exists; there is no AKS cluster to describe as paused.

All three application services were verified at zero replicas, and the comparison guard is disarmed. Restart/persistence was checked. The app-level retained estimate is approximately USD 0.245/hour before shared allocations and usage, including Search, App Configuration, Mongo throughput and three private endpoints. The 2/10 corpus coverage, summary defects and browser403 remain limitations; no full-browser E2E claim is made.

Evidence and operation: `reports\documents.md`, `reports\documents-cloud-runbook.md`, `evidence\documents\result.json`, `evidence\documents\comparison14-final.json`.

### Multi-Agent Custom Automation Engine

**Native stages were exercised, but no successful final workflow synthesis was obtained.** The original onboarding evaluation verified HR team save/select, planning, explicit approval, clarification handling and demonstration HR tools. These were demonstration tools, not enterprise account or personnel transactions.

A fresh, deliberately smaller two-specialist advisory workflow retained configuration/request RAI, planning, routing and explicit human approval. Its structured plan was inspected and approved. Both specialists responded, but HR/compliance treated supplied handbook/training dates as missing evidence and was invoked again. The run ended in a native terminal error at the authorized cap, not successful synthesis.

A bounded review confirmed that both dates survive in the saved request and approval plan, but the exact specialist inputs were not captured. No conflicting demonstration-tool output or instruction requiring documentary proof was found. The input/output mismatch is established; deterministic context loss and model-only hallucination are not proved. The separate observation that orientation was not scheduled on the required start date correctly reflected a one-day-late booking and is not counted as a defect.

All 24 upstream responses were HTTP 200, demonstrating why transport success is not business success. The second twelve calls recorded 16,200 input, 2,417 output and 1,280 cached-input tokens. Cumulative Azure account metrics were 24 requests, 36,352 processed prompt tokens and 3,997 generated tokens; the Azure increase agrees with the second-run SDK totals. Complete historical cached usage remains unknown.

**Infrastructure:** East US 2 Foundry account/project with GPT-5.4 and GPT-5.4-mini GlobalStandard capacity 10 each; NoSQL Serverless Cosmos; LRS Blob; Basic Search 1x1 in Canada Central after an East US 2 capacity failure; three private endpoints; scoped identity; one ACA app with frontend, backend and client-side MCP containers totaling 1 vCPU/2 GiB, maximum one replica.

RFP/contract documents were privately indexed, but the server-side knowledge-base tool path is unverified. MACAE uses local MAF orchestration and Foundry PromptAgentDefinition/Responses, not Foundry custom-container Hosted Agents. Official samples show an existing-account capability-host/customerSubnet mechanism, but compatibility, required data-service tiers and data-proxy costs have not been established for this exact configuration. Mandatory account recreation is not a demonstrated requirement.

Inference is disarmed at 24/24, and zero replicas were verified. Original three-domain onboarding, grounded contract/RFP analysis and public browser use are not complete demonstrations.

Evidence and operation: `reports\macae.md`, `reports\macae-cloud-runbook.md`, `evidence\macae\result.json`, `evidence\macae\network-agent-type-correction.json`, `evidence\macae\advisory-root-cause-review.json`.

### Customer Chatbot

**Private catalog infrastructure works; the grounded text journey did not pass.** Managed-identity seeding/read-back verified 16 products, and Search contains those products plus three policies. The native storefront proxy and product API returned CP-0001 / Snow Veil / USD 59.50. A nonexistent SKU returned HTTP 404 without fabricating a product.

Three native agents were created. The native chat route invoked product_agent, but its HTTP 200 response was "I can not assist with your request." This is a failed business-answer check, not a successful chatbot demonstration. The Foundry account has no network injection; private hosted retrieval is an unresolved integration dependency, not a proven explanation for that specific answer.

A bounded review found no constant refusal fallback in the native handler; the exact sentence appears in the orchestrator's RAI instructions. The SDK flattens provider refusal and ordinary output into text, and raw specialist status/error/incomplete details and a genuine provider response ID were not retained. Therefore the precise cause remains unresolved. Future diagnosis must capture those fields before text flattening, rather than infer a network failure or token exhaustion from HTTP 200 and a generic sentence.

Eight visible attempts were recorded: four embedding calls and four Responses attempts, including one HTTP 400. Ten conservative allowance units were committed because the specialist call also reserved two hosted-operation allowances. Those units are not ten observed provider calls. SDK-visible usage totals 3,485 input and 74 output tokens; specialist usage is incomplete. Azure account metrics provide a separate cross-check and must not be added to that subtotal.

**Infrastructure:** four native services on the shared Consumption Container Apps platform; NoSQL Serverless Cosmos in East US 2; Basic Search 1x1 in Canada Central after two East US 2 capacity failures; two private endpoints; managed identities; GPT-5.4-mini and embedding-3-small GlobalStandard deployments at capacity 10. No realtime model was deployed or voice journey tested.

An additional inbound AI private endpoint is not indicated by the observed results: Entra-authenticated inference already worked. Such an endpoint would not, by itself, provide hosted-agent outbound access to private Search. Public browser access remains unverified with HTTP 403 responses and unchanged ingress restrictions. The allowance is closed at ten committed units, with zero spendable balance; all seventeen revisions were deactivated and actual replicas verified at zero.

Evidence and operation: `reports\chatbot.md`, `reports\chatbot-cloud-runbook.md`, `evidence\chatbot\result.json`, `evidence\chatbot\coordinator-state.json`.

### Content Processing

**A native three-document missing-police workflow passed; the four-document happy path remains unpassed.** Claim `887455af-d0bd-4a44-a9fc-8a30ab940620` used the original API and all native stages. Claim form, repair estimate and fictional damage diagram completed Map/Evaluate/Save with targeted source-field assertions and identical saved values. RAI returned `IsNotSafe=false`, the summary was coherent, and gaps correctly identified `REQ-PR-THIRD-PARTY-006` because third-party involvement required a missing police report.

The native workflow took 4 minutes 9.546 seconds. This is one observation, not a latency distribution. The image was a synthetic diagram, not evidence of real-photo authenticity. Native schema/entity scores are not measured extraction accuracy. VIN/date-discrepancy and four-document clean-claim acceptance remain unverified.

Twenty-one initial app HTTP requests produced nineteen HTTP 200 responses and two expected HTTP 415 rejections for bad magic/unsupported text. The corrupt-file workflow returned API 202, then CU 400 and application 500 without additional model calls at that step. Cumulative CU evidence records eleven submissions, eight returned standard pages and three rejected 400 responses; the final missing-police run added two pages. CU is billed separately from customer OpenAI inference.

Two claim runs reached native Completed status with document-level errors and were not accepted as E2E passes. Schema-prefix and missing-tokenizer-cache problems were corrected without weakening the guard. One live document evaluation recovered, but a clean complete claim still needs verification. Native Completed semantics were not changed without a definitive contract; the evaluation driver now requires every expected document to have succeeded. Eleven focused offline regressions passed.

The first ten client-observed model responses returned 39,760 input/23,301 output tokens. The final six responses added 72,636 input/19,884 output. **Cumulative known returned usage is 112,396 input and 43,185 output tokens**, including 4,352 cached input and 30,046 reasoning tokens within those totals. Usage for the separate unknown reservation is excluded; this is not a complete provider-billed total.

| Final native stage | Model calls | Input tokens | Output tokens |
|---|---:|---:|---:|
| Three document mappings | 3 | 22,481 | 15,232 |
| RAI | 1 | 1,530 | 22 |
| Summary | 1 | 1,697 | 844 |
| Gaps | 1 | 46,928 | 3,786 |

The gap stage's long input and the mappings' reasoning-heavy output are concrete PTU-demand characteristics. Of the final run's output tokens, 13,716 were reported reasoning tokens, already included above.

**Provider-filter warning:** the gap response returned HTTP 200 but included `content_filter_error: The contents are not filtered`. Its usable answer does not establish provider-side filtering. Native RAI is a separate check; this warning must be resolved before customer-sensitive or unattended use.

Azure Monitor's final snapshot separately returned 12 requests, 119,537 prompt tokens and 46,854 generated tokens. Earlier it returned six requests while matching the first ten client responses' token totals; one mapping token bucket even had a zero request count. These request/token-boundary discrepancies remain unresolved, and individual Azure request IDs were not retained for correlation. Neither observation is rewritten or added to the other to force agreement.

**Infrastructure:** four small Consumption services on the shared platform; East US 2 LRS Hot Blob/Queue storage; Mongo 7 with shared manual 400 RU/s and a 400 RU/s account ceiling; App Configuration Standard; AIServices S0/Content Understanding and GPT-5.1 GlobalStandard capacity 50; four private endpoints covering Mongo, Blob, Queue and the three AI DNS zones. Mongo's required connection string was retrieved into runtime memory under a narrowly scoped role, not saved in reports or source.

The stock four-app, 4 vCPU/8 GiB per-app, minimum-one configuration was avoided. During attempted zero-model recovery, however, an older Processor revision ran despite the intended isolation, returned a CU 400 and created an additional model reservation. Its provider transmission/outcome was not captured by the client. The first ten HTTP 200 records remain unchanged; the additional reservation is conservatively retained as spent, not refunded.

Shutdown had inspected only the latest revision and missed an older running API. That deployment-control defect was corrected to inspect/deactivate every retained revision. All fourteen revisions were subsequently inactive with zero actual replicas. Prior queue effects remain unverified. This was an evaluation-control failure, not a successful zero-inference recovery.

The allocation was raised to seventeen using genuinely unused allowances from closed apps. Eleven reservations left six, one short of a fresh four-document/seven-call run, so the authorized alternative was the real three-document missing-evidence case. All six new inference records belonged to that approved claim. Unrelated queued work was visibly deferred without deletion; outputs were neither replayed nor manually marked successful.

The final budget is **17/17 reservations: sixteen returned responses plus unknown reservation 33**, conservatively spent. Inference is disarmed. All eighteen retained revisions across the four services were inactive with zero replicas at agent closure, and the coordinator independently reconfirmed zero replicas.

Evidence and operation: `reports\content.md`, `reports\content-cloud-runbook.md`, `evidence\content\result.json`, `evidence\content\missing-police-native-final.json`, `evidence\content\isolated-run-result.json`, `evidence\content\zero-model-recovery-abort.json`.

### Conversation Knowledge Mining

**Native summarization, persistence, retrieval and model-planned analytics executed; full acceptance did not pass.** Three synthetic support conversations were used. Two summaries preserved the technical issue, fix and follow-up; an ambiguous printer case retained uncertainty but inferred an unsupported symptom. Four demographic variants preserved technical facts without establishing fairness.

The original handlers accepted repository-supported pre-enriched JSON containing those previously measured summaries. SQL and Blob persistence were verified, a fresh service reloaded all three records, and native keyword retrieval returned the two VPN calls rather than the printer call. This was retrieval evidence, not a hosted agent answer with citations. The unused remote vectorizer was omitted; vector/semantic retrieval was not demonstrated.

The model-planned dashboard executed real SQL. Its total-record count 3 and VPN 2/Printer 1 category chart were correct, but two distinct-count KPIs incorrectly returned 3 instead of 2 categories and 1 source type. Native count execution uses COUNT(*). Anonymization also replaced ordinary words with "users" and damaged prose.

Processing insights received the collection count plus only the first summary for the tested multi-record, pre-enriched file, rather than all three transcript summaries. Its broader conclusions therefore lacked the full requested context. These are recorded semantic limitations, not problems remedied by additional PTUs.

Nine model requests succeeded with zero SDK retries: 4,547 input and 3,700 output tokens. Seven summary/counterfactual requests used 988/880 tokens; dashboard planning used 2,636/931; processing insights used 923/1,889. Six attempted automatic AI dispatches during persistence were blocked before transport; native heuristic fallback was disclosed, not counted as model enrichment. No embeddings, CU or Speech requests were made.

**Infrastructure:** Sweden Central AIServices S0/project with GPT-5.2 and embedding-3-small GlobalStandard capacity 10; Canada Central Basic Search, LRS Hot Blob and Entra-only SQL GP_S_Gen5 serverless, min 0.5/max 2 vCores, auto-pause 60 minutes and a 32 GB cap; four private endpoints; two small ACA services and a managed identity. SQL contained-user identity mapping was corrected; the app no longer holds server-administrator/db_owner privileges, and native reload succeeded with reader/writer/ddl_admin roles.

The initial measured data workflow used original FastAPI handlers through TestClient inside the real cloud API container, not a generic replacement service. The deployment was then completed with durable SQL/Blob/Search/MI settings in the actual serving process. Fifteen real HTTP checks against Uvicorn passed: SQL health, reload, all three original transcripts and explicit 503 responses for unarmed model/processing routes. Automatic processing and queue workers are disabled; restart tooling rejects unguarded images. This final configuration work made no additional model calls. Public browser access remains unverified after HTTP 403.

Hosted Explore remains blocked by Basic Foundry Agent/private-Search incompatibility. A supported private Standard Agent topology would need missing Cosmos, a dedicated agent subnet and Foundry/VNet regional alignment; Sweden Central Foundry and the shared East US 2 VNet do not meet that same-region relationship. An inbound AI endpoint alone does not solve hosted outbound access.

The allocation is closed at 9/9; its three unused requests were transferred to Content. All fourteen retained cloud revisions were inactive with zero replicas. The last observed SQL connection was 05:18:57 UTC. SQL remained Online at the agent's closure, then the coordinator independently observed Paused at 06:21:44 UTC. This later observation supersedes the earlier Online status; it does not erase compute charges incurred before pausing.

Evidence and operation: `reports\conversation.md`, `reports\conversation-cloud-runbook.md`, `evidence\conversation\result.json`, `evidence\conversation\serving-results.json`, `evidence\conversation\budget-handoff.json`, `scripts\Manage-ConversationCloud.ps1`.

## 4. Shared infrastructure and networking

MCAPS policy forced public network access off for new storage/database dependencies. Local Azure credentials did not provide a network route. The corrective deployment used private endpoints and application compute inside a new isolated VNet, rather than requesting policy exemptions or weakening access controls.

| Shared component | Deployed configuration |
|---|---|
| Resource group and region | `rg-ptu-bundle-platform`, East US 2 |
| VNet | `vnet-ptu-bundle`, 10.246.0.0/16; no peering to protected application networks |
| Application subnet | `snet-aca`, 10.246.0.0/23, delegated to Microsoft.App/environments |
| Private-endpoint subnet | `snet-private-endpoints`, 10.246.2.0/24 |
| Application hosting | `cae-ptu-bundle`, Consumption workload profile only; small per-service requests and maximum one replica |
| Image registry | `acrptubundle7d804f70`, Basic; registry administrator authentication disabled |
| Private DNS | VNet-linked service zones for the approved new dependencies; AI account endpoints require cognitive services, OpenAI and services.ai zones |
| Logs | No shared Log Analytics destination was configured. This is a cost-conscious lab choice, not a production observability design. |

The actual private probe resolved Blob and Cosmos endpoints into 10.246.2.0/24 and received service-level HTTPS responses. This established DNS/route reachability only; application authorization was separately exercised by the relevant app workflows.

Single-client public ingress restrictions were retained. The evaluator still received403 on cloud browser requests, so results obtained through authenticated Azure execution must not be called publicly accessible demonstrations. No VPN gateway, Bastion, tenant app registration or consent change was introduced to work around this.

Application private endpoints do not automatically give Microsoft-hosted tool execution access to private Search or other services. The exact Foundry API/agent type and its supported private data-proxy/egress configuration must be checked. Documentation distinguishes prompt agents from Hosted agents; a tool running server-side is not, by that fact alone, a Hosted-agent container deployment.

The temporary network diagnostic app was deactivated after its checks. The coordinator's final merged snapshot verifies all sixteen new application Container Apps plus that diagnostic app: zero replicas and zero active revisions. Data services are retained. Evidence: `evidence\runtime-state-final.json`; local read-only UI/health/schema responses are recorded separately in `evidence\loopback-readiness-final.json`.

Infrastructure and supporting evidence: `infra\lab-network.bicep`, `infra\app-private-endpoints.bicep`, `scripts\Add-LabPrivateEndpoints.ps1`, `reports\private-connectivity-decision.md`, `evidence\azure-resource-delta.json`.

## 5. Consumption and cost accounting

Model usage must be reported by model/deployment and observation boundary. Response usage, agent-run counters and Azure Monitor are overlapping observations; adding them would double count consumption. Missing usage is unknown, not zero. Cached-input details and output/reasoning breakdowns are only as complete as the captured responses.

**SKU numbers are not interchangeable.** An AIServices S0 account, a GlobalStandard deployment's capacity 10/50 quota setting, a Search unit and Cosmos RU/s are not PTUs. The deployment capacity values in this report are Standard quota allocations, not purchased provisioned units.

Likewise, Basic versus Standard **Foundry Agent setup** describes an agent/data/network topology, not Azure AI Search's Basic/S1 tier and not Standard versus provisioned model billing. Upgrading Search or buying PTUs alone does not supply the missing hosted-agent private egress.

The portfolio guard limits instrumented live model attempts, including failed attempts and retries; Chatbot additionally commits conservative units for hosted operations whose full usage is not visible. Allowance units are therefore not a substitute for observed request counts. The guard is not a currency spending cap and cannot prove that separately metered managed AI services made no internal model calls. CU analyses/pages and Document Intelligence usage are tracked separately.

The final coordinated allocation is fully committed: MACAE 24, CWYD 16, Modernize 10, DKM 14, Content 17, Conversation 9 and Chatbot 10 units. Content includes one unknown reservation; Chatbot includes two conservative hosted-operation allowances. No budget was silently reset or refunded to create additional room.

| Application / model | Count and basis | Measured input tokens | Measured output tokens |
|---|---|---:|---:|
| CWYD / GPT-4.1-mini | 3 SDK attempts; 2 HTTP 200 | 2,507 | 210 |
| CWYD / embedding-3-small | 13 SDK attempts; 8 HTTP 200 | 597 | Not text output |
| Modernize / GPT-5.1 | 10 model requests | 13,203 | 2,264 |
| MACAE / GPT-5.4 | 9 Azure-observed requests | 13,026 | 511 |
| MACAE / GPT-5.4-mini | 15 Azure-observed requests | 23,326 | 3,486 |
| DKM / GPT-5-mini | 7 Azure-observed requests | 2,061 | 7,424 |
| DKM / embedding-3-large | 7 Azure-observed requests | 351 | Not text output |
| Chatbot / GPT-5.4-mini | 4 visible attempts; 3 HTTP 200 | 2,066 | 116 |
| Chatbot / embedding-3-small | 4 visible attempts | 2,347 | Not text output |
| Conversation / GPT-5.2 | 9 SDK/HTTPX requests | 4,547 | 3,700 |
| Content / GPT-5.1 | 16 returned responses; 1 additional unknown reservation | 112,396 | 43,185 |

CWYD, Modernize, Conversation and Content values use their captured response usage; MACAE and DKM use reconciled dedicated-account deployment series. Chatbot token values use Azure's deployment series because its specialist SDK usage was incomplete. Content's row excludes unknown reservation 33 usage; its larger Azure account totals are separately reported above. Failed/unreturned usage is not presumed zero. These models' tokens must not be pooled into one PTU-sizing calculation.

`scripts\Capture-LabModelMetrics.ps1` collects AzureOpenAIRequests, ProcessedPromptTokens and GeneratedTokens from new dedicated lab accounts, split by ModelDeploymentName. This avoids combining embedding demand with chat-model demand for sizing. The account total and its deployment series are the same observations. Pre-existing shared EDC accounts are excluded from this attribution because other workloads may use them.

**Charges outside PTUs remain:** hosting, search, database throughput/compute/storage, blob/queue operations, extraction/OCR/CU, voice, registry builds/storage, private endpoints, DNS, managed networking, egress and observability. Models and embeddings on other deployments are separate as well.

Pausing Container Apps does not pause AI Search, App Configuration, provisioned Cosmos throughput, private endpoints or retained storage. The reconciled reference footprint below counts the shared platform once.

| Retained item | Quantity / basis | USD per hour reference |
|---|---|---:|
| AI Search Basic | Four services, each one partition/replica | 0.40400 |
| App Configuration Standard | Two stores | 0.10000 |
| Provisioned Mongo throughput | Three 400 RU/s allocations across Content and DKM | 0.09600 |
| Private endpoints | Eighteen, all Succeeded/Approved | 0.18000 |
| Basic registry | One, USD 0.1666/day | 0.00694 |
| Private DNS zones | Ten new zones, USD 0.50/zone-month first tier | 0.00685 |
| Managed networking | One Standard LB plus documented ingress/egress IP pattern | 0.03500 |
| SQL data allowance | Full 32 GB cap at USD 0.1265/GB-month | 0.00555 |
| **Reference subtotal excluding SQL compute** | **Application replicas zero** | **0.83434** |

| SQL compute condition | USD/hour | USD/24 hours | USD/730-hour month |
|---|---:|---:|---:|
| SQL actually paused | 0.83434 | 20.02 | 609.07 |
| SQL billed at configured minimum 0.5 vCore | 1.14739 | 27.54 | 837.60 |
| SQL billed at configured maximum 2 vCores | 2.08656 | 50.08 | 1,523.19 |

These are scenarios, not measured current SQL utilization or a bill. The full 32 GB SQL allowance is not a measurement of occupied storage. One ingress public IP is visible in the managed resource group; the additional egress IP follows Microsoft's documented workload-profile VNet billing pattern. Actual discounts, taxes, storage/transaction overages, registry builds, network processing/egress, DNS queries and model/extraction consumption are additional or may change the result.

**Retaining the lab is not free: approximately USD 20/day is the reference baseline with SQL paused.** SQL was observed Paused at 06:21:44 UTC; if it resumes, compute becomes chargeable according to billed usage. Resources were preserved rather than automatically deleted, as required by the playbook. After the demonstration, the owner must explicitly choose what to retain or remove; stopping application replicas alone does not eliminate these charges. Do not delete shared EDC or protected application resources.

Cost basis and arithmetic: `evidence\costs\retained-cost-assumptions.json`, `retained-cost-estimate.json`, `private-endpoint-state.json`, `managed-network-inventory.json`, and `scripts\Calculate-LabRetainedCosts.ps1`.

An earlier subscription cost query reported USD 70.622667 before attributing lab usage. That is not the lab's cost. A successful refresh at 05:00 UTC on September 12, covering September 11-12, reported approximately USD 78.24 across the subscription, but no matching lab-resource-group rows had posted. The lab subtotal remains unknown, not zero; subtracting the two subscription totals would not isolate this lab. Model usage billed to the pre-existing EDC group also cannot be attributed from a resource-group total alone.

Cost queries initially encountered HTTP 429 throttling in the shared, unspecified ClientType bucket. The capture script now uses a stable reporting-application identifier following Microsoft's guidance and records retry headers without saving credentials. Neither reported cost nor a spending-limit flag establishes the remaining MCAPS credit balance.

Revenue terminology: Azure consumed revenue and Azure Container Registry both use the abbreviation ACR, but they are different concepts. An accelerator can create valuable Azure consumption without every dollar being PTU revenue.

## 6. How to size a customer deployment after this pilot

Collect production task volume, peak concurrency, per-model calls per task, representative input/output lengths, cache reuse, latency targets, duty cycle and acceptable quality. Use peak model requests per minute, not merely user requests per minute.

For the relevant GPT-4.1/GPT-5.x text models, apply the current Microsoft model-specific sizing parameters:

```text
input_TPM = peak_model_RPM * average_input_tokens
output_TPM = peak_model_RPM * average_output_tokens
normalized_TPM = input_TPM * (1 - input_cache_fraction)
                 + output_to_input_ratio * output_TPM
raw_PTUs = normalized_TPM / input_TPM_per_PTU
```

Round up to the applicable minimum and increment, add headroom, and validate representative traffic on a real provisioned deployment. Check current model/version/geography availability. Do not generalize this formula to models with different cache-read/write accounting.

| Tested text model | Published input TPM/PTU | Output-to-input weight |
|---|---:|---:|
| GPT-4.1-mini | 14,900 | 4 |
| GPT-5-mini | 23,750 | 8 |
| GPT-5.1 | 4,750 | 8 |
| GPT-5.2 | 3,400 | 8 |
| GPT-5.4 | 2,400 | 6 |
| GPT-5.4-mini | 7,900 | 6 |

For these published model rows, Global/Data Zone provisioned minimums are 15 with increments of 5. Regional minimums/increments are 25/25 for GPT-4.1-mini, GPT-5-mini and GPT-5.4-mini, and 50/50 for GPT-5.1, GPT-5.2 and GPT-5.4. These are service parameters as of the evidence date, not recommended purchase quantities or proof of availability in a customer's region.

Different models do not automatically share one PTU allocation. Combining workloads is useful only when their model/API/residency and isolation requirements genuinely permit a shared deployment. Interactive RAG/chat may supply a steadier demand stream; asynchronous document or modernization work may fill scheduled spare capacity. This is a hypothesis to validate, not evidence of achieved utilization.

For low-volume or sporadic workloads, Standard capacity or an applicable Batch path can be more appropriate than idle provisioned capacity. Optimize useful outcomes, not unnecessary calls or inflated token counts.

Detailed methodology and model-specific published sizing parameters: `reports\capacity-and-billing-method.md`.

## 7. Existing applications and BYOK

SpecSuite and two Planetary Explorer deployments were management-plane inventoried as Running. That is not a fresh UI, authentication or model workflow check. Their inventoried resources were not redeployed or repointed. Only the separately inventoried EDC model account was deliberately selected for shared inference; unresolved indirect dependencies prevent a blanket claim of zero traffic impact on every existing application.

Visible Planetary Explorer settings referred to their own Foundry accounts. The narrow SpecSuite environment inspection did not reveal a model endpoint; indirect secret/database-held dependencies were not resolved. This is not a complete dependency audit.

GitHub distinguishes local client BYOK from enterprise/organization-managed custom models. Azure login alone does not establish GitHub enterprise administrator rights, licensing or compatible provider authentication. The candidate shared Foundry account disables key authentication; keys were not enabled to force a demonstration.

The assessed documented CLI Azure provider path expects compatible tool calling/streaming, a deployment URL and provider key configuration. This does not establish that every Copilot client has the same authentication/API requirements. No client configuration, enterprise policy, consent or credential was changed. BYOK remains unconfigured and functionally unverified in this evaluation.

Evidence and existing endpoints: `reports\existing-apps-and-byok.md`.

## 8. DND and production gates

The MCAPS private network is not a JDCP landing-zone design. In JDCP, private endpoints must integrate with centrally owned hub DNS through the current Cloud Ops process. Do not copy lab-owned privatelink zones into a JDCP spoke.

Before any customer deployment:

1. Confirm data classification, authorized processing/residency boundaries and service/model eligibility. A Canada East resource using GlobalStandard does not guarantee Canadian inference residency.
2. Validate inbound user access and outbound tool/data paths from the actual runtime. Private endpoint creation and Entra roles solve different parts of this problem.
3. Establish human approval, identity, least-privilege access and real connector permissions before replacing demonstration tools with consequential business operations.
4. Add durable workflow recovery, usable error reporting, negative tests, grounding evaluation and domain-specific acceptance tests. Code translation requires real target-engine validation.
5. Define observability, retention, alerting, support ownership, incident handling, dependency updates and a cost owner. This evaluation is not a security audit or authorization to operate.
6. Benchmark quality, latency, concurrency and model-specific capacity before a PTU commitment. Keep an explicit rollback/fallback and operating budget.

## 9. Evidence and reproducibility

Repository clones reside under `C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo`. Reports, synthetic fixtures, deployment scripts and evidence reside in the PTU accelerator Bundle directory. The supplied Word documents and original protected PDFs were preserved; the evaluation used the readable Word content.

Each application's `evidence\<app>\result.json` and `reports\<app>.md` records its source revision, actual configuration, adaptations and outcomes. Cloud runbooks are separate from inference authorization: resuming compute must not silently reset a model ledger or reuse an old allowance.

| Application | Tested source commit, abbreviated |
|---|---|
| MACAE | `8ac703a71f10` |
| Chat With Your Data | `0fce71307dfa` |
| Content Processing | `659eaa1f503dd` |
| Modernize Your Code | `7592ea97550f` |
| Conversation Knowledge Mining | `8a00aa54bc25` |
| Customer Chatbot | `cb86d1153df3` |
| Document Knowledge Mining | `7df8ed33a86d` |

These are upstream base revisions; disclosed local patches, adapters and pinned images are also part of the evaluated builds. Full commit IDs are retained in the per-app results. Source repositories:

- https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator
- https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator
- https://github.com/microsoft/content-processing-solution-accelerator
- https://github.com/microsoft/Modernize-your-code-solution-accelerator
- https://github.com/microsoft/Conversation-Knowledge-Mining-Solution-Accelerator
- https://github.com/microsoft/customer-chatbot-solution-accelerator
- https://github.com/microsoft/Document-Knowledge-Mining-Solution-Accelerator

Parent evidence includes the baseline inventory, resource delta, role assignments, network checks, deployment-level model metrics and reported-cost responses. Inventory deltas do not by themselves prove that no configuration changed, and shared-subscription activity requires careful attribution.

Primary public references:

- Provisioned throughput concepts: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput
- Model-specific sizing: https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing
- Foundry private networking: https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/virtual-networks
- Agent network architecture: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agents-networking-deep-dive
- GitHub BYOK concepts: https://docs.github.com/en/copilot/concepts/models/bring-your-own-key
- Enterprise custom models: https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/enable-custom-models
- CLI BYOK configuration: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models
- Container Apps billing: https://learn.microsoft.com/en-us/azure/container-apps/billing
- Managed VNet resource charges: https://learn.microsoft.com/en-us/azure/container-apps/custom-virtual-networks#managed-resources
- Cost API client identification/rate limits: https://github.com/Azure/azure-rest-api-specs/issues/24407#issuecomment-1594282220
