# Customer Chatbot - native ecommerce evaluation

**Status: CLOSED / partial functional result.** The allowance is closed at **10 committed units**: eight visible attempts plus two hosted allowances. **Only the two uncommitted units were reclaimed to parent reserve; spendable balance is zero.** All eight request records were preserved, and an admission check against the old deployed guard was rejected before any model call. Local/cloud live and ingestion flags are disarmed; future inference requires a new explicit operator allowance.

All **17 revisions across the four native apps** were deactivated and verified **inactive/Stopped with zero replicas**. No model, account, project or network changes were made for closure; the only data change was the authorized budget-document closure. No new model calls occurred. Closure evidence: `evidence\chatbot\closure.json` and `deactivated-revisions.json`.

The last actual native text execution returned a refusal, not a grounded answer: **"I can not assist with your request."** That remains a functional failure. This is the real Microsoft Customer Chatbot ecommerce/Contoso Paints accelerator, adapted to the approved shared Container Apps environment, not a generic replacement or unchanged `azd up`.

## Bounded agent/network clarification

Five read-only lookups confirmed **Prompt agents**, not Foundry Hosted/custom-container agents. The native creation script calls `AzureAIProjectAgentProvider.create_agent`; its SDK creates `PromptAgentDefinition` through `agents.create_version`. Inference uses the project **Responses API with `agent_reference`**, not a Hosted-agent `/invoke` custom-container path. The accelerator's own ACA application containers do not change the Foundry agent type.

The [private-networking guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/virtual-networks) explicitly scopes the creation-time-only network-injection restriction to **Hosted agents**. It must not automatically be applied to this Prompt-agent path. The [networking deep dive](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agents-networking-deep-dive) describes Prompt traffic through **Tools Service -> project single-tenant data proxy -> private endpoints**, with account-level subnet configuration and no Micro VM.

**Current conclusion: setup unconfigured/unproven; nondestructive existing-account/new-project transition unverified.** The official Standard/BYO sample README documents existing-account reuse and skipping model deployment, but also distinguishes tools-behind-VNet setup. The bounded reads did not establish an exact minimal, nondestructive private-tool transition for this existing account/project, so no validated resource/role proposal is asserted. No deletion/recreation requirement is inferred for Prompt agents. The generic refusal's cause is still **not proven**. Details and all five sources: `evidence\chatbot\bounded-network-review.json`.

The chronological results below describe the completed evaluation, not authority to restart or spend.

## Bounded refusal diagnosis after closure

Eight focused read-only lookups found **no retained provider Responses ID, raw specialist response, provider status, `incomplete_details`, or tool terminal error**. The session ID and budget UUIDs are not provider response IDs; no guessed ID, existing-response fetch, app wake or new generation was used.

The native HTTP handler forwards `result.text` (or `str(result)`) and otherwise raises500; it has **no constant refusal fallback** on that path. The exact observed sentence is in the orchestrator's RAI instructions. The SDK maps both provider `output_text` and structured `refusal` parts into text, so the saved final string cannot distinguish those two cases.

Reasoning is kept as `text_reasoning` and excluded from `.text`; specialist `as_tool` returns only `.text`. Reasoning-only/non-text or incomplete specialist output could therefore be flattened to empty tool text. The SDK retains response ID/raw representation in memory, but the native router saves only answer content/recommendation metadata. Its inspected parser does not reject failed/incomplete status before building the text response. None of those possible conditions is proven to have occurred.

The specialist's HTTP200/null usage is **not proof of completion, zero tokens, token-limit exhaustion, or private Search failure**. Final orchestrator output was12 tokens, while specialist usage and terminal details are missing. No network cause is established.

The specific next diagnostic improvement, **not executed**, is to persist whitelisted response IDs/status/error/incomplete details, output-part types, tool terminal outcomes and specialist text-presence before flattening, then retrieve that existing response. Any future generation still requires a new operator allowance; no new infrastructure is needed merely to capture this metadata. Full evidence/proposal: `evidence\chatbot\refusal-diagnosis.json`.

## Revision and safety boundary

**Coordinator refresh, 2026-09-11 23:36 -04:00:** freshly read the durable ledger, with **zero new model calls**: 8 visible attempts, 10/12 committed conservative units (including two hosted allowances), **two uncommitted units**. Do not reclaim the committed ten. The smallest next real catalog/unknown-SKU journey plans three visible attempts plus two hosted allowances, requiring five units; shortfall three. No optional calls are planned. The API was briefly woken for the ledger read and restored to min0/max1 at revision `chatbot-chat-api--0000007`; post-refresh instantaneous replicas were not remeasured. Current evidence: `evidence\chatbot\coordinator-state.json`. The previously recorded all-zero replica snapshot is historical after this brief wake.

Repository: https://github.com/microsoft/customer-chatbot-solution-accelerator

- Checkout: `C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\customer-chatbot-solution-accelerator`.
- SHA: `cb86d1153df30a1bc6e744d74d3ff583764cd154`; describe: `v2.0.0-54-gcb86d11`.
- Subscription: `1feb53b2-854a-4ea7-b5a6-709b7d804f70`; tenant: `a600acd0-3028-4689-8402-3b471d7d924d`.
- Own resource group: `accel-chatbot-eval-0911`. Shared MCAPS platform: `rg-ptu-bundle-platform`; this is **not JDCP**.
- No SpecSuite/Planetary calls, modifications or reuse. No keys, secret files, policy exceptions, public-enable attempts in this deployment phase, quota increases, provisioned models or Azure deletion.
- All model/data authentication uses managed identity/Entra. APIs are internal; both UIs retain the approved `174.112.74.34/32` ingress restriction.

## Current functional evidence

| Check | Expected | Actual | Verdict |
|---|---|---|---|
| Private Cosmos | Native container can use its own MI to seed/read | Private IP `10.246.2.18`; 16 native products seeded and read back | PASS |
| Native product API | CP-0001 is Snow Veil, 59.50 | Exact native product returned | PASS |
| Native unknown SKU API | HTTP404, no fabricated product | `404 Product not found` | PASS, data layer only |
| Native storefront proxy | nginx -> internal API -> private Cosmos | HTTP200, CP-0001/Snow Veil/59.50 | PASS, not browser/model proof |
| Private Search | Private DNS and MI data access | `10.246.2.24`; PNA Disabled; index listing succeeded | PASS |
| Native Search ingestion | 16 products and 3 policies | Native scripts ran; subsequent Search document-count read-back returned exactly 16 and 3 | PASS |
| Native agents | Catalog, policy and orchestrator created | `ptu-chatbot-product-eval`, `ptu-chatbot-policy-eval`, `ptu-chatbot-chat-eval` | PASS, metadata/setup only |
| Combined model journey | Grounded catalog, policy, dual routing and unknown SKU | Native `/api/chat/message` HTTP500 in 2,863.111 ms; Foundry HTTP400 rejected the evaluation wrapper's `reasoning` override | FAIL; wrapper fixed and redeployed |
| Product/unknown-SKU model retry | Genuine native catalog-specialist answer | Native route HTTP200 in 18,315.762 ms; product_agent invoked; final generic refusal and zero cards | FAIL, not grounded success |
| Return/warranty and dual-specialist model outcomes | 30-day returns, custom-tinted final sale, two-year warranty; both specialists observable | No successful model result yet; remaining budget no longer fits another full mixed journey | NOT VERIFIED |
| Browser interaction | Allowed-client rendering/interaction | Current public tool path receives403; restrictions retained | NOT VERIFIED |
| Voice | Short supported and metered synthetic audio | Realtime not deployed; evaluation websocket gate blocks unmetered voice | NOT RUN |

The refusal's root cause is **not established**. The tested prompt explicitly mentioned `product_agent`; the persisted harness now uses an ordinary business question, but that revision has **not** been run. The hosted Foundry Search tool has a separate network path from the native ACA application's successful Search connection. [Current Microsoft guidance](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/ai-search#limitations) states that basic agent deployment does not support private Search with PNA Disabled; standard agents with VNet injection are needed. The own Foundry account has `networkInjections=null`. This is a known integration risk, **not a confirmed diagnosis of the refusal**.

## Required versus actual Azure infrastructure

Full IDs, identities, image digests and revision evidence are in `evidence\chatbot\result.json`, `cloud-result.json` and the cloud runbook. Own resource IDs start with `/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/accel-chatbot-eval-0911/providers/`.

| Required surface | Actual provisioned/reused surface | Region / size |
|---|---|---|
| Foundry account/project | `Microsoft.CognitiveServices/accounts/aif-ccptu1feb0911`, project `proj-ccptu1feb0911` | East US 2, AIServices S0, local auth disabled |
| Text model | `gpt-5.4-mini`, version `2026-03-17` | GlobalStandard, capacity10; **not PTU** |
| Embedding model | `text-embedding-3-small`, version `1` | GlobalStandard, capacity10; **not PTU** |
| AI Search | `Microsoft.Search/searchServices/srch-ccptu1feb0911` | Canada Central, Basic, 1 replica x 1 partition, semantic free, Entra-only, PNA Disabled |
| Native search objects | `ptu-chatbot-products`, `ptu-chatbot-policies`; AAD project connection `aifp-srch-connection-ccptu1feb0911` | 16 product documents, 3 policy documents |
| Native agents | Three `ptu-chatbot-*-eval` agents | Own Foundry project |
| Cosmos persistence | `Microsoft.DocumentDB/databaseAccounts/cosmos-ccptu1feb0911`, `ecommerce_db` | East US 2, NoSQL Serverless, Entra-only, PNA Disabled |
| Five native containers | `carts` /user_id, `chat_sessions` /user_id, `products` /productId, `transactions` /user_id, `users` /email | Existing native schemas |
| Private connectivity | `pe-chatbot-cosmos` (Sql) and `pe-chatbot-search` (searchService) | Two approved PEs in parent East US 2 PE subnet; existing private DNS zones |
| Runtime hosting | Four native `chatbot-*` Container Apps in parent `cae-ptu-bundle` | Consumption; max1 each; min0 except temporary test wake |
| Registry | Reused parent `acrptubundle7d804f70.azurecr.io` | Basic, admin disabled; only `chatbot/*` tags |
| Identities | `mi-chatbot-chat-api`, `mi-chatbot-scenario-api`, `mi-chatbot-chat-ui`, `mi-chatbot-scenario-ui` | Per-app; AcrPull and applicable own-resource roles |
| Stock App Service hosting | Not created; native containers adapted to approved ACA instead | No App Service plan, AKS, VM or duplicate platform |
| Optional audio/monitoring | Realtime/Voice Live deployment, dedicated App Insights and alerts not created | No voice bill or PTU purchase |

Search placement in Canada Central was explicitly approved at **2026-09-11 22:15 -04:00**, following two East US 2 capacity failures. Cross-region **synthetic MCAPS** data is authorized and may incur transfer/latency overhead. Search was created with PNA Disabled on its initial PUT, using the repository's full-configuration Search module rather than its initial public-default two-step wrapper. Cosmos PE was already present and was not duplicated.

Search identity roles follow the native module: project reader/schema access, seeding app data/schema contributor and scenario reader. Current Microsoft guidance additionally requires Foundry account MI Search Data Contributor/Service Contributor; both were added **only at this own Search service**. Search MI has OpenAI User only on the own Foundry account for vectorization. No shared-account role was duplicated.

## Measured model traffic and budget

Final ledger: **8 visible model HTTP attempts / 10 of 12 conservative units**. Observed totals: **3,485 input / 74 output / 0 cached tokens**, **incomplete**. Four embeddings contributed 2,347 input tokens; two orchestrator responses contributed 1,138 input/74 output/0 cached tokens. The catalog specialist's HTTP200 had no captured usage, and the rejected HTTP400 had none. Embedding output/cache tokens were not returned and remain null, not measured zeros.

| Deployment / operation | Status | Elapsed ms | Returned input tokens |
|---|---:|---:|---:|
| text-embedding-3-small, 16-product batch | 200 | 616.987 | 1,608 |
| text-embedding-3-small, policy 1 | 200 | 239.656 | 442 |
| text-embedding-3-small, policy 2 | 200 | 271.871 | 128 |
| text-embedding-3-small, policy 3 | 200 | 237.935 | 169 |
| gpt-5.4-mini, orchestrator request | 400 invalid_payload | 132.433 | null |
| gpt-5.4-mini, retry orchestrator/tool selection | 200 | 1,846.321 | 530 |
| gpt-5.4-mini, catalog specialist | 200; no captured terminal usage | 12,068.313 | null |
| gpt-5.4-mini, final orchestrator/refusal | 200 | 1,031.293 | 608 |

The failed text attempt is **not removed or refunded from the cap**. The wrapper now avoids the rejected per-request `reasoning` override when an agent reference is present; native agent settings remain authoritative. It also captures failed/error SSE event codes even when transport status is200. Both corrections have offline regressions and are deployed in `cb86d11-eval4`. The readiness check after that deployment verified 16 private Cosmos products and the unchanged 8-attempt/10-unit ledger; no additional inference was made.

**At evaluation end two units were uncommitted; they have now been reclaimed. Zero units remain spendable.** Further grounded/policy/mixed/negative-SKU validation requires a new operator allowance. The native result validator rejects the actual recorded refusal despite HTTP200; a synthetic positive fixture only verifies assertion code, not live functionality.

The Cosmos ETag ledger is `ecommerce_db/chat_sessions`, document `ptu-chatbot-eval-cb86d11`, partition `__ptu_chatbot_evaluation_budget__`. Never reset/delete it. Embeddings and visible Responses HTTP attempts are metered before network transmission; SDK retries are disabled. Specialist requests reserve three conservative units to allow for hosted Search embedding and a hosted model turn. These allowances are **not measured server-side request counts**; hosted token visibility can be incomplete. The cap is shared across replicas/revisions. No load/bulk performance test occurred.

ACA console management429 at `2026-09-12T02:32:57Z` specified Retry-After600. It was respected; the native request began only after `02:43:10Z`. This is distinct from model throttling. Initial long exec payloads also hit Windows command-length and management URL limits; compact compressed, quote-free transport subsequently worked without a local build, ingress change or secret transfer.

## Per-feature PTU dependence and costs

**PTU is optional capacity, not a functional prerequisite.** These deployments are GlobalStandard; capacity10 is not ten PTUs. No provisioned throughput, PTU utilization, sustained throughput, latency percentiles or fixed tokens-per-PTU conversion was measured.

| Feature | PTU relationship | Separate Azure dependency / billing |
|---|---|---|
| Product discovery | Optional compatible provisioned capacity for orchestrator/catalog model turns | Foundry agents, Search, embeddings, Cosmos/history |
| Return/warranty answers | Optional compatible text-model capacity | Policy index/retrieval, embeddings, Cosmos |
| Mixed specialist routing | Routing itself requires no PTU; nested text turns may use compatible PTU | Agent orchestration/tool calls and both indexes |
| Nonexistent SKU | Deterministic authoritative-catalog validation uses no PTU; natural-language answer may use text capacity | Catalog/retrieval and native card parser |
| Embedding ingestion/query vectorization | Separate model/token billing; not text-model PTU | Embedding deployment and Search vectorizer |
| Hosted Search / Foundry IQ | Search capacity is not OpenAI PTU; native `azure_ai_search` is not proof of a separately exercised Foundry IQ planner/meter | Search units/semantic/tool usage and hosted connectivity |
| Realtime / Voice Live / speech | Not automatically covered by ordinary text PTU; possible downstream text-agent calls remain separate | Realtime audio, speech/transcription and Voice Live meters |
| UI, data, networking and operations | No PTU dependence | Consumption vCPU/GiB seconds/requests, Cosmos RU/storage, PE hours/processing, ACR, monitoring |

[Microsoft Learn sizing guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing) documents provisioned support for relevant GPT models, including the selected text model/version. Availability and sizing remain model/version/region/workload specific. Smoke results cannot establish PTU sizing.

Search Basic reference: approximately **US$0.10/hour / US$2.40/day**, from the parent's public Canada Central retail reference, not an invoice or binding quote. Search has no scale-to-zero here and remains billable. Add two PE hour/data meters, small serverless Cosmos usage, shared ACR allocation, any short remote-build compute and cross-region transfer. No duplicate registry/network/environment, paid semantic tier, S1 upgrade or model-capacity change occurred. Actual model dollar cost and effective per-answer cost have not been established.

## Runtime, implementation changes and reproduction

Storefront: `https://chatbot-scenario-ui.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`

Chat UI: `https://chatbot-chat-ui.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`

Both APIs use the corresponding `chatbot-chat-api.internal...` / `chatbot-scenario-api.internal...` names, ports8001/8000 inside their containers. Each API is 0.5 vCPU/1 GiB; each UI is 0.25 vCPU/0.5 GiB. Native health probes are shallow; successful configuration labels alone do not establish dependency authorization.

All four local processes were stopped for cloud migration: PIDs35252/10668/10856/21048 were historical serving PIDs, not current ones. The obsolete owned BuildKit container `22f8b1a09f45670bed8ee4355718d087d74ad8d4ded66f43ae740f60a4abfb27` was stopped and verified after an observed 800.8 MiB footprint. No other application's process or the shared Docker daemon was stopped. Further necessary builds use approved bounded remote ACR work, minimal clean context and the original native image lineage; no heavy local build was restarted.

Native changes: MI selection for cloud credentials/seeding, unique data/agent names, nondeleting/fail-fast embedding ingestion, authoritative native catalog-card validation, and opt-in nginx system resolver for ACA. The native App Service resolver default remains unchanged outside this opt-in. Evaluation-only transport metering and a voice gate do not replace the native chat route or specialists.

Offline outcomes: native component regressions **8/8**; current HTTP-meter regressions **6/6** and durable-budget regressions **3/3**. Native frontend/widget builds and isolated native backend dependencies previously passed. No grounded-model success is inferred from those checks.

Remote builds `chr` and `cht` both **Succeeded** in approximately90 and86 seconds, uploading only65.097/65.129 KiB contexts and retaining the immutable backend base built from the original repository Dockerfile. These rebuilds updated the existing evaluation overlay, not a substitute application. Windows CLI log streaming failed on Unicode; authoritative run metadata confirms success, and partial streams/errors are retained. Final API digest: `sha256:760887e37ae17badc729213d32ebc41ae6b3f1091ff736cf67282003b7ac0ca7`. It was returned to min0/max1 at revision `chatbot-chat-api--0000005`; no always-on worker remains configured.

Final scale/ingress verification passed: all four apps remain Consumption/min0/max1, HTTP concurrency5; APIs internal, UIs restricted to the original clientCIDR. Latest observed replica counts are **zero for all four**: the other three were checked at03:08Z and the Chat API at03:10Z after its cooldown. Search remains billable; no cloud resources were deleted.

Persistent start/stop/digest instructions: `reports\chatbot-cloud-runbook.md`. From the bundle:

**Historical commands only while closed:** live/ingestion launchers now reject the old flags. Do not reactivate revisions or restore a budget without a new explicit operator allowance.

```powershell
# Wake/redeploy uses the runbook's current immutable digest.
.\scripts\Invoke-ChatbotCloudCheck.ps1 -Stage readiness
.\scripts\Invoke-ChatbotCloudCheck.ps1 -Stage usage
.\scripts\Invoke-ChatbotLiveCheck.ps1 -Stage search
# Live needs five remaining conservative units and explicit confirmation.
.\scripts\Invoke-ChatbotLiveCheck.ps1 -Stage live -ConfirmModelCalls
.\scripts\Set-ChatbotCloudIdle.ps1 -Service chat-api
```

Do not reseed embeddings just to restart the app. Preserve the fixed ledger and honor management Retry-After headers. Exact per-request records and expected/actual outcomes are retained under `evidence\chatbot`; historical local failures remain explicitly historical in the main JSON.
