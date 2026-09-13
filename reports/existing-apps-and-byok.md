# Existing deployments and GitHub Copilot BYOK

Evidence date: 2026-09-11.

## Protected existing applications: inventory only

The supplied playbook explicitly protects SpecSuite and Planetary Explorer. Their inventoried resources were not redeployed, repointed, modified, retagged, or given new identities/permissions. No identified protected model endpoint was deliberately selected for reuse. Only the separately inventoried EDC account was selected; unresolved indirect dependencies mean this is not proof of zero traffic impact on every existing application.

Azure management-plane inventory returned `Running` for:

| Application | Resource group | Existing endpoint |
|---|---|---|
| SpecSuite demo | rg-demo | https://specsuite-demo.redplant-4add1127.canadacentral.azurecontainerapps.io |
| Planetary Explorer | rg-planetaryexplorer | https://ca-web-mgxvsbslmnvjs.kindglacier-3c521d46.eastus2.azurecontainerapps.io |
| Planetary Explorer, additional deployment | rg-pexalex | https://ca-web-cbzmyrtv7w6ja.jollysea-b072c86a.westus3.azurecontainerapps.io |

This is **management-plane status**, not a fresh UI, authentication, inference or end-to-end health test. The user's statement that these applications already work is not presented as a test performed during this evaluation.

The full protected resource inventory, including AKS/managed groups and other associated resources, is in `evidence\protected-resources.json`. Recorded app status is in `evidence\preflight\protected-app-status.json`.

A later read-only check of visible endpoint settings confirmed that the two Planetary Explorer apps reference their own corresponding Foundry accounts, not the reused EDC account. No model endpoint was exposed by the narrowly selected SpecSuite environment fields. Secret-held, database-held and other indirect configuration was not resolved; the inventory is not a complete dependency or traffic-impact audit. No secret values were retrieved. Evidence: `evidence\preflight\protected-model-dependency-hosts.json`.

SpecSuite's analysis/specification/code generation can be inference-heavy, particularly for long repositories and output-heavy generation. Planetary Explorer's intent interpretation, agent reasoning and answer generation can consume inference; geospatial queries, imagery access and geospatial compute are separate dependencies. Their actual MCAPS per-workflow model usage was not measured here. Historical DND evidence in the supplied portfolio is attributed to that document, not revalidated.

## BYOK is a configuration track, not an eighth Azure accelerator repository

Current GitHub documentation distinguishes local BYOK from enterprise/organization-managed custom models:

| Path | Required configuration | Assessment in this lab |
|---|---|---|
| Local client BYOK | Supported client; provider endpoint/model; provider authentication; applicable organizational policy | Documentation checked. No user's client configuration or provider credentials changed. |
| Enterprise BYOK | Enterprise/organization owner configuration, custom-model policy, supported provider key/deployment URL, enabled organization access and Copilot license | Not configured or functionally tested. Existing Azure login does not grant GitHub enterprise administration or establish these entitlements. |
| Azure model behind either path | Model/API/client compatibility and allowed network access; compatible provisioned endpoint to actually use PTUs | The candidate non-protected shared Foundry accounts have local-key authentication disabled. Do not enable keys merely to complete a BYOK demo. |

The current CLI documentation requires tool calling and streaming. It documents `COPILOT_PROVIDER_TYPE=azure`, the deployment URL, a provider API key and the deployment/model identifier. That documented key-based path is not immediately compatible with the identity-only shared accounts. This is a configuration/authentication gap, **not** proof that all BYOK clients lack identity-based options.

The supplied portfolio's blanket "Completions only, not Responses" statement should not be generalized to all current clients: local and enterprise BYOK are distinct and evolve independently. Verify the selected client's current API requirements. The current CLI OpenAI-compatible provider documentation specifically describes Chat Completions compatibility.

If a supported Copilot surface really sends requests to a customer-owned provisioned model, those requests use its provisioned capacity. Repository context, conversation history, tool loops and generated code determine input/output token demand. Other Copilot features should not be assumed to use that endpoint without client-specific evidence. Provider charges and any required Copilot license remain separate.

**Disposition:** retain BYOK as a separate controlled developer-platform pilot. No enterprise settings were changed, no secrets were exported and no PTUs were purchased.

## Sources

- https://docs.github.com/en/copilot/concepts/models/bring-your-own-key
- https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/enable-custom-models
- https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models
- Supplied deployment playbook and portfolio Word documents.
