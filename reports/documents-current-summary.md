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
