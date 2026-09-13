# Customer Chatbot — adapted native cloud runbook

This runs the repository's native ecommerce services in the approved shared MCAPS Consumption environment. It is **not unchanged `azd up`**, and successful infrastructure/data checks are not successful LLM journeys.

**CLOSED:** durable allowance is10 committed units, zero spendable; two uncommitted units were reclaimed to parent. All8 request records are preserved. All17 app revisions are inactive/Stopped with actual replicas0, including latest API revision `chatbot-chat-api--0000008`. Its maintenance template has min1 but is inactive; do not reactivate it. Existing deployed images reject admission because the closed ledger no longer has their original limit12; current source additionally enforces a closed flag. Old local cloud-enable, seeding and live-confirmation flags no longer authorize execution.

Future inference requires a **new explicit operator allowance**, deliberate guard re-arming and an authorized app activation. Do not reset/delete the ledger or treat historical12 as an available balance. Commands below are retained for history, not current permission. Closure receipt: `evidence\chatbot\closure.json`.

The Foundry agents are **PromptAgentDefinition** agents using project Responses, not Hosted/custom-container agents. The Hosted-only creation-time network-injection restriction is not asserted for this path. Prompt private-tool setup is unconfigured/unproven, and an existing-account/new-project transition remains unverified after five bounded lookups; see `bounded-network-review.json`. No network change or additional PaaS proposal was validated.

## Current endpoints and protections

- Storefront: `https://chatbot-scenario-ui.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`
- Chat UI: `https://chatbot-chat-ui.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`
- Both UIs permit only `174.112.74.34/32`; restrictions were present at creation.
- APIs are internal: `chatbot-chat-api.internal.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io` and `chatbot-scenario-api.internal.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io`.
- Cosmos remains PNA Disabled. The approved PE resolves to `10.246.2.18` inside the native Chat container. No JDCP resources/DNS were used.
- Search now exists in approved Canada Central: Basic1x1/semanticfree/Entra-only/PNA Disabled, private IP `10.246.2.24`. Native read-back verified16 products and3 policies.
- All four apps use Consumption, min 0/max 1. Backend limits: 0.5 vCPU/1 GiB each; frontend limits: 0.25 vCPU/0.5 GiB each.
- Current tool-path public UI checks receive 403. Do not broaden the approved CIDR to make a test pass. Allowed-client browser interaction remains unverified.

## Build and image provenance

**Host constraint update (22:08 -04:00): do not repeat heavy local builds while RAM is constrained.** The commands below describe historical successful builds, not a request to rerun them now. Parent approved short Azure ACR remote builds using the **original repository Dockerfiles**, unique `chatbot/*` tags and a minimal clean source context. Exclude all `.env`, `.azure`, credentials/internal documents, dependency caches and the parent workspace. Preserve the original Dockerfile's `COPY` layout; do not confuse the existing runtime-overlay contexts with original-source contexts. Bound build time and retries, retain failure output, and use the guarded CLI for supported actions. No new image rebuild is needed for the currently deployed images.

The obsolete dedicated local builder was inspected at **800.8 MiB** and stopped by exact container ID `22f8b1a09f45670bed8ee4355718d087d74ad8d4ded66f43ae740f60a4abfb27`; `running=false` was verified. No unfinished Chatbot PowerShell sessions were found, and the four earlier local app processes were already stopped. Cloud services were not stopped or modified by this cleanup. No global Docker/WSL/cache cleanup was performed.

Exact repository SHA: `cb86d1153df30a1bc6e744d74d3ff583764cd154`.

1. Historical build: `scripts/Build-ChatbotContainers.ps1` used the native backend Dockerfiles and an owned limited local builder. Do not repeat it under the current RAM warning.
2. Native Chat base was pushed as `chatbot/chat-api-native:cb86d11`, digest `sha256:dbc4e698c86fab528a5cd8f4ebeb09415cbfd9d70b2d8c1bc66b3706b9b5d346`.
3. `scripts/Stage-ChatbotCloudImages.ps1` stages only native sources/validated frontend artifacts and evaluation helpers under `%LOCALAPPDATA%\ptu-chatbot\cloud-images`. It excludes `.env`, `.azure`, keys and the parent workspace.
4. `scripts/Publish-ChatbotCloudImages.ps1 -Component chat-api|chat-ui|scenario-ui` builds/pushes the selected image. Backend dependency checks passed in network-disabled local containers. Frontends package the already validated native builds with the repository's production nginx image, config and startup scripts.
5. Native source adaptations include managed-identity selection for cloud seeding, the narrow catalog-card safeguard, nondeleting/fail-fast Search ingestion, and opt-in metering. Chat cloud image adds a separate native seed venv and blocks unmetered voice websockets.

Final immutable images:

| Service | Digest in `acrptubundle7d804f70.azurecr.io/chatbot/` |
|---|---|
| `chat-api` (`cb86d11-eval4`) | `sha256:760887e37ae17badc729213d32ebc41ae6b3f1091ff736cf67282003b7ac0ca7` |
| `scenario-api` | `sha256:3b64f6233329dc1f392eb19d1698881494abd1ada76ff1e071494bbf7240d42a` |
| `chat-ui` (`cb86d11-eval2`) | `sha256:e0877fe65b6f6c1b460939504436264fb6c164538d8490f6eaf5502a3b9b6517` |
| `scenario-ui` (`cb86d11-eval2`) | `sha256:30f6bcdaddc01553a7db6047fb1f917b3a96e0b6fc56c15a77a8219c72c14b39` |

The eval2 frontend startup scripts opt into the container's resolver from `/etc/resolv.conf` (`NGINX_USE_SYSTEM_RESOLVER=1`). The native App Service default remains 168.63.129.16 when opt-in is absent. In ACA, the observed system resolver was 127.0.0.11; nginx's original default produced gateway404 while direct service discovery worked. After the adaptation, the actual storefront proxy returned HTTP200 with CP-0001/Snow Veil/59.50 through the private API/data path. Both updated images passed shell syntax and nginx configuration checks. No platform DNS resource or policy was changed.

Remote rebuilds `chr`/`cht` succeeded, respectively fixing the rejected agent-reference reasoning override and capturing HTTP200 failed/error SSE codes. The evaluation Dockerfile retains the immutable original-native backend base above. Each upload was about65 KiB, without secrets or the parent workspace. No heavy local build was restarted. Current API idle revision: `chatbot-chat-api--0000007`, after a model-free coordinator ledger refresh; min0/max1 restored and no new model calls.

For a future necessary rebuild, stage first, enter only `%LOCALAPPDATA%\ptu-chatbot\cloud-images\chat-api`, then invoke the bundle's absolute guard path with `acr build --subscription 1feb53b2-854a-4ea7-b5a6-709b7d804f70 --registry acrptubundle7d804f70 --image chatbot/chat-api:<unique-tag> --file Dockerfile --timeout 900 --no-wait .`. Dockerfile is resolved from the current directory, not automatically from an unrelated source-context argument. `--no-wait` avoids the observed Windows Unicode log-stream failure. Record the returned run ID and query `acr task show-run` with only status/times/outputImages selected; do not blindly repeat a build after a local logging exception. Deploy only a verified successful immutable output digest.

## Wake for authenticated checks, then return to idle

From the bundle directory:

```powershell
.\scripts\Deploy-ChatbotCloud.ps1 -Service chat-api `
  -Image 'acrptubundle7d804f70.azurecr.io/chatbot/chat-api@sha256:760887e37ae17badc729213d32ebc41ae6b3f1091ff736cf67282003b7ac0ca7' `
  -MinimumReplicas 1

.\scripts\Invoke-ChatbotCloudCheck.ps1 -Stage readiness
.\scripts\Invoke-ChatbotCloudCheck.ps1 -Stage usage

# Already completed: the native Cosmos stage upserted 16 synthetic products.
# Re-run only intentionally; it is not required on each restart.
# .\scripts\Invoke-ChatbotCloudCheck.ps1 -Stage cosmos

.\scripts\Set-ChatbotCloudIdle.ps1 -Service chat-api
```

To restart/redeploy another service, use its row's immutable digest with `Deploy-ChatbotCloud.ps1 -Service <service>`. Set minimum 1 only for a bounded exec/test session; restore zero afterward. The templates enforce max 1, probes, identity, ingress and Consumption-only placement.

`Set-ChatbotCloudIdle.ps1` re-applies the checked-in template rather than a generic CLI scale update. A CLI update was observed blanking HTTP `concurrentRequests`; IaC restored it to `"5"` and min 0/max 1 was verified for all apps. Default cooldown is 300 seconds; configured min 0 is not a measurement of instantaneous zero replicas.

Final observations on2026-09-12: all four had zero latest-observed replicas (other three03:08Z; Chat API rechecked03:10Z). `final-app-configuration.json` verifies unchanged ingress/Consumption/scaler settings, and `final-replica-counts.json` records the timestamps. Requests can wake them again; Basic Search continues billing independently.

Serialize exec calls to the same app: concurrent attempts intermittently returned `ErrorGeneratingAuthToken`. On 2026-09-12 at 01:56:40Z, the management websocket returned HTTP429 with `Retry-After: 600`; no exec retry was made during that cooldown. This was **not** a model request/429. Prefer one baked test script per exec for future batches, and honor management retry headers. Avoid nested `python -c` quoting; invoke the baked script or simple curl arguments with `--max-time 60` as separate tokens.

## Model budget and remaining work

- Durable ledger: existing Cosmos `ecommerce_db/chat_sessions`, document `ptu-chatbot-eval-cb86d11`, partition `__ptu_chatbot_evaluation_budget__`.
- **Do not delete/reset the ledger.** ETag conditional reservations occur before model attempts and survive replicas/revisions. Local app processes were stopped to avoid separate local/cloud budgets.
- Current usage: **8 visible attempts, 10/12 conservative units**. Returned totals3485 input/74 output/0 cached are incomplete; specialist usage is unknown.
- Authoritative coordinator refresh at2026-09-12T03:36Z reconfirmed those exact counts. Only two units are uncommitted; the hosted allowances within the committed ten must not be reclaimed. See `coordinator-state.json`; post-refresh instantaneous replicas were not remeasured.
- **Do not rerun ingestion or inference.** Product/policy embeddings and all three agents already exist. The allowance is closed and the two previously uncommitted units have been reclaimed; zero remain.
- Canada Central Search and its approved PE are complete. No additional Search/region approval is pending.
- `Invoke-ChatbotLiveCheck.ps1 -Stage search` performs a model-free private data/count check. `-Stage live -ConfirmModelCalls` is guarded, sends an ordinary business question through the actual native route and rejects HTTP200 refusals or incorrect catalog/SKU results. It cannot run with the current remaining budget.
- Actual corrected text run invoked product_agent but returned "I can not assist with your request." No grounded answer or mixed specialist success is claimed. The first combined request failed on an evaluation reasoning override, now fixed; its attempt remains counted.
- The private hosted-tool path is not proven: Foundry has no VNet injection, and Microsoft documents that basic agents do not support private Search. This is a risk, not a confirmed refusal diagnosis. Do not enable public access, add policy exceptions or create unapproved standard-agent dependencies.
- Existing passes: private DNS/data access, native 16-product ingestion, native `CP-0001` → Snow Veil/$59.50, native nonexistent SKU → 404. These **do not** establish model grounding or specialist routing.
- Text-model provisioned throughput is optional compatible capacity, not exercised here. Cosmos, Search, registry/hosting, embeddings and voice have separate cost/throughput relationships. No PTUs or realtime deployment were purchased.
