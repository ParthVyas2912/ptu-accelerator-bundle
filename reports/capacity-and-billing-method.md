# PTU capacity and billing: interpretation for this evaluation

Evidence date: 2026-09-11. This is a non-production MCAPS evaluation with synthetic data, not a DND deployment or an accreditation assessment.

## What "depends on PTUs" means

None of these applications inherently requires a **provisioned** deployment to supply its AI features. A compatible Standard/GlobalStandard deployment can supply inference instead. The distinction is the capacity and billing arrangement, not a separate application feature.

Conversely, many important application features do depend on **model inference**: answer generation, agent planning, specialist reasoning, structured extraction performed by an LLM, summarization, SQL translation, and validation performed by an LLM. Those requests can consume provisioned capacity only when their actual endpoint/model/API configuration routes them to a compatible provisioned deployment.

There is no evidence-based single percentage of "the app" that is PTU-dependent. The final comparison separates:

1. Semantic features that invoke customer-configured inference.
2. AI services that may have their own pricing or internal model routing.
3. Non-inference infrastructure such as hosting, databases, search, queues and storage.

The initial subscription inventory found Standard and GlobalStandard deployments, not ProvisionedManaged, GlobalProvisionedManaged or DataZoneProvisionedManaged. Do not label measured Standard tokens or latency as measured PTU utilization. A model smoke test alone does not validate application behavior or prove production throughput.

## Measuring useful consumption

Record per workflow and per model deployment: input tokens, cached input tokens, output/reasoning tokens when returned, number of inference calls including retries, client duration, request status, throttling and task quality. A multi-agent task can make several model calls; a tool invocation by itself is not necessarily an inference call.

Do not add token counters from response totals and their details twice. Do not infer zero usage from a missing usage field. Mark unavailable measurements explicitly. Azure Monitor totals on a shared account can include other applications and are not automatically attributable to this lab.

`scripts\Capture-LabModelMetrics.ps1` additionally collects `AzureOpenAIRequests`, `ProcessedPromptTokens` and `GeneratedTokens` from **new dedicated lab accounts only**, split by `ModelDeploymentName`. This separates chat and embedding deployments for capacity interpretation. The account aggregate and deployment series are the same observations, not additional usage. This provides an Azure-side cross-check and can reveal calls made through managed-service integrations. It deliberately excludes pre-existing shared accounts. Raw responses and their exact time range are retained in `evidence\model-metrics`; empty metric series remain unknown, not zero.

SDK, agent-run and Azure account metrics describe different observation boundaries. Report them alongside one another where helpful, never add them as independent consumption. Server-mediated search/agent calls and metric reporting delays can explain discrepancies. A configured client request guard alone does not establish complete attribution of every internal managed-service model call.

PTU utilization, capacity headroom and Standard-versus-PTU latency remain unmeasured unless a real provisioned deployment is tested under representative traffic. No new PTUs or reservations are authorized by the lab deployment contract.

## Sizing after a successful pilot

Use a separate capacity calculation for each compatible model/version/deployment type and geography. Aggregate applications only when they can genuinely share that deployment. Different models do not automatically pool into one PTU deployment.

For the GPT-4.1 and GPT-5.x text-model rows relevant to these accelerators, the Microsoft sizing formula is:

```text
input_TPM = peak_model_requests_per_minute * average_input_tokens
output_TPM = peak_model_requests_per_minute * average_output_tokens
normalized_TPM = input_TPM * (1 - input_cache_fraction)
                 + output_to_input_ratio * output_TPM
raw_PTUs = normalized_TPM / model_input_TPM_per_PTU
```

Round up to the model/deployment type's minimum and scale increment; include operational headroom and validate on a real deployment. Use peak model-call RPM, not merely user-task RPM. For multiple calls in one workflow, sum their per-model token shapes first.

Selected published values as of the evidence date:

| Model | Input TPM/PTU | Output-to-input ratio | Global/Data Zone minimum; increment | Regional minimum; increment |
|---|---:|---:|---|---|
| gpt-4.1-mini | 14,900 | 4 | 15; 5 | 25; 25 |
| gpt-5-mini | 23,750 | 8 | 15; 5 | 25; 25 |
| gpt-5.1 | 4,750 | 8 | 15; 5 | 50; 50 |
| gpt-5.2 | 3,400 | 8 | 15; 5 | 50; 50 |
| gpt-5.4 | 2,400 | 6 | 15; 5 | 50; 50 |
| gpt-5.4-mini | 7,900 | 6 | 15; 5 | 25; 25 |

These are model-specific sizing parameters, not token billing rates. Availability, model version, quota and physical capacity must still be checked. Do not extend the cache formula indiscriminately to newer models: the current documentation gives GPT-6 Astra different normalized cache-read/write weights.

No numeric customer PTU recommendation is justified yet: expected production demand, concurrency, representative prompt/output distribution, duty cycle, latency target and caching are not supplied.

## Charges that do not disappear when PTUs are purchased

- App Service plans, Container Apps compute, AKS nodes and associated networking.
- Azure AI Search provisioned search capacity and applicable semantic/agentic retrieval charges.
- Cosmos DB throughput or serverless operations; Azure SQL compute/storage.
- Blob storage, queues, transactions, network egress and private networking.
- Content Understanding, Document Intelligence/OCR, Speech and voice processing, according to the selected service's billing model. Verify whether any customer-selected model deployments are additionally used; do not assume all service usage burns customer PTUs.
- Embeddings on separate deployments and other models not routed to the provisioned text-model endpoint.
- Container Registry, Key Vault operations, monitoring/log ingestion and retention.
- GitHub Copilot licensing where required, independent of Azure provider charges.

Standard deployments incur token charges when used; provisioned deployments incur PTU-hour charges while allocated, including idle periods. Batch is a credible alternative for asynchronous ingestion/translation/analysis that does not need interactive latency. Low-volume pilots should not be used to justify idle provisioned capacity.

**Revenue terminology:** the business metric Azure consumed revenue (ACR) is different from Azure Container Registry (also commonly abbreviated ACR). Supporting services may contribute Azure consumption without consuming a customer's provisioned model capacity. A successful bundle should demonstrate useful outcomes and efficient utilization, not unnecessary token generation.

## Sources

- Microsoft Learn, provisioned throughput concepts: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput
- Microsoft Learn, model-specific PTU sizing (updated 2026-09-11): https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing
- GitHub, local versus enterprise BYOK: https://docs.github.com/en/copilot/concepts/models/bring-your-own-key
- GitHub, enterprise custom-model configuration: https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/enable-custom-models
- GitHub, CLI BYOK requirements: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models
