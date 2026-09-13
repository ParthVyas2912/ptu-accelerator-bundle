# Modernize inspection / infrastructure proposal

Inspected 2026-09-11. Repository cloned to the requested repo directory.
Commit `7592ea97550fb711d7d8b64186875967d574c5d5`, main, commit date
2026-08-27T20:37:31+05:30; describe `v1.9.1-57-g7592ea9`.

## Scope and official references

Read the deployment contract and playbook reuse/Modernize/testing sections first.
Authoritative source files inspected: `azure.yaml`, `infra/main.bicep`,
`infra/main.parameters.json`, `infra/modules/cosmosDb.bicep`,
`infra/modules/ai-foundry/aifoundry.bicep`, backend `.env.sample`, requirements,
app lifespan/config/credential helper, SQL agent orchestration and native parser,
frontend package/Vite config, Docker compose, and docs DeploymentGuide,
LocalDevelopmentSetup, LocalSetupGuide, SampleWorkflow, CustomizingScenario,
re-use-foundry-project.

## Early proposal (sent before any new billable infrastructure)

- Tenant `a600acd0-3028-4689-8402-3b471d7d924d`.
- Subscription `1feb53b2-854a-4ea7-b5a6-709b7d804f70` only.
- Preferred full-app path: official native FastAPI and React, bound only to
  `127.0.0.1:8114` and `127.0.0.1:5114`. No cloud hosting/ACR needed.
- Existing nonprotected Foundry: `rg-edc-foundry-hack/edcfoundryhack01`,
  project `edc-hack-proj`, Canada East.
- Existing `gpt-5.1`, model version `2025-11-13`, `GlobalStandard`, capacity 100,
  matches the current five-agent defaults. This is NOT provisioned throughput.
- Minimum proposed persistence: dedicated `rg-ptu-modernize-demo`;
  `stptumodernize<unique suffix>`, StorageV2 Standard_LRS Hot, private Blob
  container `ptu-modernize-files`; `cosmos-ptu-modernize<unique suffix>`,
  Cosmos NoSQL Serverless, database `ptu-modernize`, three containers with
  partition keys `/batch_id`, `/file_id`, `/log_id`. Canada Central proposed.
  Charges would be storage GB/transactions and Cosmos RU consumption/GB.
  These resources have NOT been created by the inspection/proposal.
- Alternative: parent-approved nonprotected shared Cosmos/Storage using
  documented runtime configuration. No speculative IaC changes.
- Full default Azure deployment is more expensive: two Container Apps
  (minimum one replica; backend 1 vCPU/2 GiB), ACR, Storage Standard_LRS,
  Cosmos (provisioned throughput implicitly configured by module defaults),
  managed identity and optional monitoring. Native hosting avoids these fixed
  hosting/registry items.

Parent owner ID supplied by agent registry was not messageable (`No agent found`);
the proposal was also relayed to the MACAE sibling for parent coordination.
No new billable resource creation is authorized by that delivery failure.

## Concrete issues / deviations

1. Reuse doc says `AZURE_EXISTING_AI_PROJECT_RESOURCE_ID`, but current
   `infra/main.parameters.json` reads `AZURE_EXISTING_AIPROJECT_RESOURCE_ID`.
2. Backend sample omits `AI_PROJECT_ENDPOINT`; real Config/lifespan requires it.
3. Docker compose describes only storage connection strings, while actual
   clients use identity and account/database environment fields.
4. Official app has five persistent Foundry Agents; a migration is multiple
   billable inference steps, including syntax tool continuation and retries.
   A per-HTTP-call guard is needed for the 12-call initial limit.
5. Native frontend Vite proxy defaults to port 8000 and strips `/api`, but
   backend mounts routes under `/api`. Loopback/port compatibility adjustment
   must be explicitly recorded if used.
6. App lifespan catches agent initialization errors and still exposes healthy
   `/health`; that cannot establish a functional deployment.
7. Source syntax checker uses the bundled Microsoft T-SQL parser; its
   semantic verifier is an LLM judgment, not database execution equivalence.
8. No Informix or SQL Server engine has yet been established. A synthetic
   alternative engine check must not be labeled Informix/SQL Server equivalence.

## Initial observations

- Read-only Foundry Agents list probe (not inference) returned HTTP 401:
  missing `Microsoft.CognitiveServices/accounts/AIServices/agents/read`.
- The repository grants Foundry User role
  `53ca6127-db72-4b80-b1b0-d745d6d5456d` in `infra/main.bicep`.
  Narrow, additive project-scoped access is being investigated rather than
  changing any protected resource or shared model deployment.
- Bundled Windows T-SQL parser executed: `SELECT TOP 5 * FROM employees;`
  returned `[]`; `SELEC FROM WHERE;` returned line 1/column 1 syntax error.
  These are parser component results, NOT migration results.
- Official frontend install/build and backend isolated virtualenv/dependency
  installation are in progress. Virtualenv is outside OneDrive.

No secrets are included here; identity tokens remain in process memory.
