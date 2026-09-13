# MACAE — parent private-network/container handoff

## Superseding outcome — 2026-09-12 01:57 UTC

The shared platform is ready and MACAE was deployed. Private Cosmos, Blob and
Search access passed from the native container; MACAE added only the Search PE.
The native onboarding segment consumed12/12 calls and reached explicit
approval, HR clarification and demonstration actions; IT/final synthesis and
RFP/contract agent grounding remain incomplete. Both synthetic documents are
now privately indexed. Inference is disabled, min0/max1, and **zero replicas
were observed at01:57:55 UTC**.

**Use `reports/macae-cloud-runbook.md` for current restart/build instructions
and `evidence/macae/result.json` for current images, identity, usage and state.**
The current evaluation Dockerfile requires `hrpack`, `indexscripts` and
`testdata` named build contexts. Do not use the old build or budget-initialization
commands below; the existing Cosmos ledger must never be reset.

## Historical pre-cloud handoff — not current status

Prepared 2026-09-12 UTC. MCAPS subscription
`1feb53b2-854a-4ea7-b5a6-709b7d804f70` only. No JDCP hub resources,
protected applications, new model purchases or firewall exceptions.

## Verified outcome and remaining gate

**Coordination update, 2026-09-11 20:58 EDT:** parent is provisioning
`rg-ptu-bundle-platform` / East US 2, `vnet-ptu-bundle` (`10.246.0.0/16`),
Consumption `cae-ptu-bundle`, Basic `acrptubundle7d804f70` with admin disabled,
and initial MACAE Cosmos/Blob private endpoints. This is **announced, not yet
verified ready**. Do not create duplicates or deploy before parent readiness.
Search `searchService` is the additional private endpoint needed. Verify the
actual registry loginServer and environment domain from parent/ARM; do not
infer their final DNS names. Wait for the parent's current allowed-client CIDR
rather than treating the earlier observed address as renewed ingress approval.

- **Search fallback succeeded:** `ptu-macae-7d804f70-srch`, Canada Central,
  Basic, one replica, one partition, semantic **free**, system identity,
  `disableLocalAuth=true`, `publicNetworkAccess=Disabled`.
  Its RG remains `rg-ptu-macae-demo` (East US 2). Cross-region operation is
  intentional and authorized for synthetic data, not a residency assurance.
- Before creation: provider listed Canada Central, name availability was true,
  retail Basic was **USD0.101/hour**, and ARM validation succeeded. These
  preflights could not guarantee capacity; the subsequent real allocation did.
  The original East US 2 failed deployment is preserved.
- All three official images built successfully from
  `8ac703a71f10b622bd3c82a9cc2b5dfe921c3025`, using an isolated clean worktree.
  A small explicitly disclosed backend metering layer also built.
- Offline Linux container tests passed for native frontend/UI, guarded native
  backend startup, and actual MCP HR tool discovery/blueprint.
- **0/12 live inference attempts.** Seven new budget tests use fake Cosmos and
  HTTPX MockTransport only. They are not live model or cloud database tests.
- No ACA app, ACR, network, private endpoint, DNS zone or runtime-MI role was
  created by MACAE in this continuation. Parent platform IDs are still needed.

## Exact private-link resources — observed from Azure

Resource ID prefix for all rows:
`/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/rg-ptu-macae-demo/providers/`

| Resource-ID suffix | Region | Actual groupId | Required private DNS zones | Client port |
|---|---|---|---|---|
| `Microsoft.DocumentDB/databaseAccounts/ptu-macae-7d804f70-cosmos` | East US 2 | `Sql` | `privatelink.documents.azure.com` | TCP443, Python SDK gateway |
| `Microsoft.Storage/storageAccounts/ptumacae7d804f70st` | East US 2 | `blob` | `privatelink.blob.core.windows.net` | TCP443 |
| `Microsoft.CognitiveServices/accounts/ptumacae7d804f70` | East US 2 | `account` | `privatelink.cognitiveservices.azure.com`, `privatelink.openai.azure.com`, `privatelink.services.ai.azure.com` | TCP443 |
| `Microsoft.Search/searchServices/ptu-macae-7d804f70-srch` | Canada Central | `searchService` | `privatelink.search.windows.net` | TCP443 |

Cosmos requires both DNS members `ptu-macae-7d804f70-cosmos` and
`ptu-macae-7d804f70-cosmos-eastus2`. Foundry reports members
`default`, `secondary`, `third`. Provision the account endpoint, not a separate
project private endpoint. Storage needs **blob only**, not file/queue/table/dfs.

Keep canonical service URLs; private DNS must resolve them correctly from
actual ACA runtime. Do not rewrite SDK URLs to private-link hostnames or proxy
around storage. Parent also owns DNS resolver access and authenticated registry
pull/identity dependencies. Basic ACR has no Private Link support; do not
silently upgrade it to Premium or assume a private ACR endpoint is available.

Foundry was last observed PNA Enabled with Entra-only authentication; this
continuation does not change it. Cosmos, Blob and Search stay PNA Disabled.

## Important RFP/contract caveat: client private endpoints are not enough

Native `src/backend/agents/agent_template.py` deliberately executes local HR
MCP tools **client-side**, but preserves knowledge-base MCP tools as
**server-side Responses API tools**, authenticated by project connections.
Therefore:

1. ACA → Cosmos/Blob/Foundry/Search private endpoints can unblock application
   persistence, client-side ingestion, and HR/IT orchestration.
2. **Foundry-hosted Responses tool → private Search** needs a supported Foundry
   outbound private-network configuration. A private endpoint in the *caller*
   ACA VNet does not supply that server-side path.
3. If Foundry inference is also made private, **Search KB → Foundry** reasoning
   needs Search shared private access. Microsoft Learn documents
   `Microsoft.CognitiveServices/accounts`, group **`openai_account`**, with
   Basic-and-higher support for knowledge bases. This is a distinct outbound
   connection, not the inbound Foundry PE group `account`.
4. Search's actual private-link listing returned `searchService` and an older
   outbound-type list that did not advertise `openai_account`; treat the
   documented shared-private-link path as requiring API/runtime validation,
   not as an already-working connection.
5. **Corrected 2026-09-12:** the detailed Learn creation-time warning is explicitly
   for Hosted agents. MACAE is local MAF plus project Responses and
   `PromptAgentDefinition`, not a Foundry custom-container Hosted Agent.
   Account recreation is **not established as mandatory**. Read-only ARM GETs
   returned null network injection and empty account/project capability-host
   lists: the service-side private path is unconfigured, not proven immutable.
6. The official standard-setup sample documents an existing-account capability
   host using `customerSubnet`, plus existing-project wiring. The latter requires
   prior account injection; it alone does not resolve the observed prerequisites.
   Exact Responses/KB MCP, Serverless Cosmos, Basic Search and cost compatibility
   remain unverified. See `network-agent-type-correction.json` for the bounded
   reuse proposal. No account recreation, model redeployment, new subnet,
   trusted-service bypass or alternative proxy is authorized by this handoff.

Sources verified:
- https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/networking-options
- https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/virtual-networks
- https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agents-networking-deep-dive
- https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep/15-private-network-standard-agent-setup
- https://learn.microsoft.com/en-us/azure/search/search-indexer-howto-access-private

The current Foundry IQ tutorial's ingestion-time embedding trusted-service
bypass is outside authorization, even when a shared private link exists.
Its newer API/different traffic direction is not proof of this native path.

RFP/contract remote reasoning remains blocked until both its network path and
aggregate model-call accounting are resolved. A larger call allowance alone
would not fix the network path.

## Cheap container composition prepared for parent

`scripts/macae-shared-aca.bicep` compiles successfully. It creates **only one
application** against parent-supplied existing infrastructure; it has not been
deployed. Three containers share the replica's loopback network:

| Container | Image/context | Port and route | Requested CPU/RAM |
|---|---|---|---|
| Frontend | Official `src/App/Dockerfile`, context `src/App` | Sole ingress target3000; `/`, `/config`, `/health`, `/api/*` and WebSockets | 0.25 vCPU / 0.5GiB |
| Backend | Official `src/backend/Dockerfile`, context `src/backend`, plus metering entrypoint | Internal8000; API `/api/v4`; liveness `/healthz` | 0.5 vCPU / 1GiB |
| MCP | Official `src/mcp_server/Dockerfile`, context `src/mcp_server` | Internal9000; `/hr/mcp` and domain MCP mounts | 0.25 vCPU / 0.5GiB |

Total **1 vCPU / 2GiB**, maxReplicas **1**, minReplicas **0** by default.
Use min1 only for the bounded active workflow/approval test, then return to0:
in-memory waiting/checkpoint behavior is not scale-to-zero recovery proof.
This is an ACA sidecar composition of official services, not a claim that the
repo supplies a single combined image. Do not expose ports8000 or9000.

Required nonsecret runtime values are fully enumerated in the Bicep:
- Frontend: `PROXY_API_REQUESTS=true`,
  `BACKEND_API_URL=http://127.0.0.1:8000`.
- Backend: `APP_ENV=prod`, parent UAMI `AZURE_CLIENT_ID`, tenant/subscription,
  dedicated Foundry project/account/model URLs, Cosmos database/container,
  `MCP_SERVER_ENDPOINT=http://127.0.0.1:9000/mcp`, Search and Blob endpoints.
- MCP: `BACKEND_URL=http://127.0.0.1:8000`,
  **`UV_NO_SYNC=true`**, `ENABLE_AUTH=false` on its nonexposed sidecar only.
  No image-generation endpoint/deployment is configured; image features are
  out of scope and unverified.
- Default cloud backend **`MACAE_LIVE_REQUESTS_ENABLED=false`**.
  Never supply `AzureCliCredential`, client secrets, API keys or connection
  strings to these cloud containers.
- Sole ingress: HTTPS, mandatory single-client CIDR, initially
  `174.112.74.34/32` from parent's lab-ingress evidence; revalidate at deployment.
  Optional `AUTH_ENABLED=true` only after actual ACA Entra authentication is
  configured. With CIDR-only ingress, native sample-user mode is an evaluation
  choice, not verified per-user production authorization.

Observed native local working sets were backend/UI127.6MiB and MCP97.2MiB.
Offline backend startup passed at1GiB/0.5CPU; frontend at0.5GiB/0.25CPU;
MCP at0.5GiB/0.5CPU. Requested MCP0.25CPU and combined cloud sizing remain
unverified. The Docker build worker was capped at3GiB and1.5CPU with one build
step at a time; no other app's builder was changed.

## Container-specific issues found and addressed

- Official MCP CMD `uv run ...` attempts a runtime project rebuild and fetches
  `hatchling` even though frozen dependencies were built. It failed under
  `--network none`. Setting supported uv env **`UV_NO_SYNC=true`** preserved
  the same official image/CMD and passed actual9-tool HR discovery/blueprint.
- Official MCP Docker HEALTHCHECK requests `/health`, which actually returns
  **404**. Prepared ACA probes use **TCP9000**, not that broken HTTP route.
- Backend `/healthz` returns200 with an always-true default check: it proves
  liveness, **not Cosmos/Search/Foundry readiness**. Frontend `/health` is also
  only liveness. Validate private dependencies separately before enabling calls.
- Backend evaluation entrypoint invokes the already-installed Python runtime,
  installs metering, then imports the unchanged `app:app`. No app workflow was
  replaced. This is an explicit evaluation-only layer, not an upstream image.

## Runtime identity and data permissions to supply

Existing lab-user grants do not cover cloud MI. Parent supplies UAMI resource
ID, client ID and principal/object ID. Use these exact new-resource scopes:

| Principal/use | Role | Scope |
|---|---|---|
| Runtime UAMI | Foundry User `53ca6127-db72-4b80-b1b0-d745d6d5456d` | New project only |
| Runtime UAMI | OpenAI User `5e0bd9bd-7b93-4f28-af87-19fc36ad61bd` | New Foundry account |
| Runtime UAMI | Cosmos DB Built-in Data Contributor | `/dbs/ptu-macae` only |
| Ingestion identity | Storage Blob Data Contributor | Each of the two MACAE Blob containers only |
| Bootstrap identity | Search Service Contributor + Search Index Data Contributor | New Search service only; no subscription-wide grant |
| Runtime validation/retrieval | Search Service Contributor for native metadata validation; Search Index Data Reader for direct retrieval where needed | New Search service only |
| Foundry project MI `64446efa-4feb-4f2a-9853-dc67be56592d` | Search Index Data Reader | New Search service for managed KB connection |
| Search MI `6f4938e0-07b1-49b9-9f15-6777ed93ce30` | OpenAI User | New Foundry account for KB reasoning |
| Runtime UAMI image pull | AcrPull, or registry's supported equivalent | Parent Basic ACR only |

Only grant roles actually needed for the selected stage. No new grant from
this table has been performed. Native `index_datasets.py` downloads Blob data
client-side and pushes Search documents; that ingestion path does not itself
require a Search-managed Blob indexer/private link.

## Metering, observability and rollback

- `macae_cosmos_budget.py` uses ETag compare-and-swap in the already-created
  `memory` container, fixed document `__ptu_macae_model_budget_v1`,
  partition `__ptu_macae_evaluation__`. No new database/container/storage SKU.
- Missing ledger, failed authorization/networking, contention exhaustion and
  slot13 all fail closed. Restarts/revisions share the same durable cap.
- Before enabling any live cloud call: stop the local backend, export/check
  its consumed total (currently0), then run the cloud entrypoint once with
  `init-budget` and explicit `MACAE_PREVIOUS_LIVE_CALLS`. It uses create, never
  upsert/reset. Do not run local and cloud inference ledgers concurrently.
- Only after actual private connectivity/ledger verification set
  `MACAE_LIVE_REQUESTS_ENABLED=true` for the controlled HR workflow.
  Do not seed/run KB teams until hidden service-side calls are accountable.
- Actual returned model/status/latency/input/output/cache/error fields go to
  Cosmos and sanitized `MACAE_MODEL_METER` console lines. Null stays unknown.
  Local scratch JSONL is not durable cloud storage; Cosmos is authoritative.
  No prompts, model text, credentials or headers enter this meter.
- Parent can use existing environment system/console diagnostics to alert on
  failed revision/probe, restart, HTTP403/5xx and exhausted budget. Notification
  channel and alert rules are **not deployed**.
- `Test-MacaeRelease.ps1` prepares health/config verification and an explicit
  failure-triggered reapply of parent-supplied previous image parameters. It
  is not executed and is not a workflow test. First deployment has no previous
  verified rollback target. Preserve the Cosmos budget across any rollback.
- No load test, production SLA, backup/restore or zero-downtime claim.

## Costs and parent inputs

Reproduce local images from the clean pinned worktree:

```powershell
# Worktree is already staged at %LOCALAPPDATA%\ptu-eval\macae-container-source.
.\scripts\Build-MacaeImages.ps1 -Component all
docker build --builder desktop-linux --file .\scripts\macae-backend-eval.Dockerfile --tag ptu-macae-backend-eval:8ac703a7-eval1 .\scripts
```

After parent supplies the registry, Entra-login to that approved registry,
tag/push `ptu-macae-frontend:8ac703a7`, `ptu-macae-mcp:8ac703a7` and
**`ptu-macae-backend-eval:8ac703a7-eval1`** under a MACAE-only registry prefix.
Resolve resulting registry digests and pass those exact references, not
mutable `latest`, into `macae-shared-aca.bicep`. Do not deploy the unguarded
backend image during the capped evaluation.

The compiled template requires `managedEnvironmentId`,
`runtimeIdentityResourceId`, `runtimeIdentityClientId`, `registryServer`,
`frontendSiteName`, `backendImage`, `mcpImage`, `frontendImage` and `clientCidr`.
Initial `liveRequestsEnabled=false`, `minReplicas=0`; no passwords or secret
parameters. The parent must validate all supplied IDs against the authorized
MCAPS/new-resource scopes before executing deployment.

**Current additional fixed Search baseline:** USD0.101/hour (~USD73.73/730h),
plus metered Cosmos/Blob and applicable governance diagnostics.

Prepared East US 2 Consumption resource request, fully active:
`1 × 3600 × 0.000024 + 2 × 3600 × 0.000003 = USD0.108/hour`.
Retail API also reports USD0.40/million requests. This excludes shared ACR,
private endpoints, DNS, logs, cross-region traffic, models and free grants;
it is not an invoice or a current cloud-compute charge. No ACA was created.
All of these are separately billed from any eligible PTU inference.

**Supply next:** managed environment resource ID and region/default domain,
Basic ACR name/login server/resource ID, UAMI resource/client/principal IDs,
approved current ingress CIDR/auth choice, completed private DNS/PE IDs and
the supported Foundry-to-Search private egress decision. No self-provisioned
network or cloud compute is requested or performed by this handoff.
