# Document Knowledge Mining — approved isolated short test

Approval received 2026-09-11 19:49 -04:00. This DKM-only exception supersedes the earlier no-AKS decision, but does not authorize protected-resource use, provisioned models, reservations, premium upgrades or other agents' infrastructure.

## Exact target, before provisioning

- Tenant: `a600acd0-3028-4689-8402-3b471d7d924d`.
- Subscription: `1feb53b2-854a-4ea7-b5a6-709b7d804f70`.
- New application RG: **`accel-dkm-20260911`**, Central US. Confirmed absent.
- AKS necessarily creates its own associated node RG, expected **`MC_accel-dkm-20260911_aks-dkmeval0911a_centralus`**; no unrelated existing RG is a target.
- Source SHA: `7df8ed33a86dd4f0f9e7417e882039fd38556e59`.
- Official checked-in ARM: `infra/main.json`; `docs/DeploymentGuide.md` explicitly supports ARM/Bicep/group-deployment provisioning.
- Parameter file: `evidence/documents/approved-parameters.json`. No template/resource replacement.
- Environment flags: private networking, monitoring, redundancy, scalability and module telemetry disabled.
- CLI actions pass through `Invoke-LabAz.ps1 -AzArguments`; authorization is this explicit exception, not the guard.

| Expected resource | Configuration |
|---|---|
| `aks-dkmeval0911a` | AKS Standard control-plane tier (AVM default), Kubernetes 1.34.2; Regular Linux D4ds_v5 system pool, initial 2, autoscale min1/max2 |
| Associated worker resources in new managed RG | VMSS, default Azure CNI networking/NSG, Standard load balancer, public outbound IP; OS disks as assigned by AKS defaults |
| `crdkmeval0911a` | ACR Standard |
| `appcs-dkmeval0911a` | App Configuration Standard |
| `cosmos-dkmeval0911a` | MongoDB 7.0, single region, no serverless/free-tier assumption; default database and app-created DPS collections |
| `srch-dkmeval0911a` | Search Basic, one partition/replica |
| `stdkmeval0911a` | StorageV2 Hot **Standard_GRS**, the actual AVM default; private `smemory` blob container and runtime queues |
| `oai-dkmeval0911a` | OpenAI S0 in East US; new GlobalStandard GPT-5-mini 2025-08-07 capacity10; embedding-3-large v1 capacity50 |
| `di-dkmeval0911a` | Document Intelligence S0 in Central US, no training/commitment tier |
| `id-dkmeval0911a` and scoped RBAC | New workload identity and documented access assignments only |

No App Service, Bastion, jumpbox, private endpoints, replicas, premium Search, premium ACR, PTU or reservations are proposed. The nested AKS module only enables OMS when a workspace ID exists, so default monitoring=false does not propose a separate monitoring workspace.

## Fuller hourly estimate and hard decision threshold

Public Azure Retail Prices API checked 2026-09-11. USD list rates, no assumed credits/discounts. Short-test cost, not a monthly commitment:

| Item | Basis | USD/hour |
|---|---|---:|
| 2 D4ds_v5 Linux workers | 2 x $0.255/hour | 0.51000 |
| AKS Standard management | Standard Uptime SLA meter | 0.10000 |
| Search Basic | 1 x $0.101/hour | 0.10100 |
| ACR Standard | $0.6666/day /24 | 0.027775 |
| App Configuration Standard | $1.20/day /24 | 0.05000 |
| Cosmos, expected small test | Allow 1200 RU/s total at $0.008 per100 RU/s-hour | 0.09600 |
| Standard load balancer | Included rules/outbound rules | 0.02500 |
| Standard regional public IP | One address | 0.00500 |
| OS disk estimate | Two P10-equivalent disks, $19.71 each /730h; no disk premium upgrade requested | 0.05400 |
| **Expected fixed baseline** | Before small data/operation usage | **0.968775** |

Cosmos child template defaults to400 RU/s when not specified; live offers must be checked because parent passes optional values and app collections are created at runtime. The estimate allows default400 plus two400 app collections. A conservative allowance of **2000 RU/s plus up to $0.11/hour OS disks** gives **$1.088775/hour**, before small usage. Use **$1.15/hour planning allowance**, not an asserted billing cap. **Do not proceed with provisioning if fixed infrastructure clearly exceeds the approved $1.50/hour threshold.** Verify actual SKUs/offers before ingestion; do not increase them.

Variable usage:

- Document Intelligence S0 has no fixed hourly minimum. Current Read rate starts at $1.50/1000 pages; prebuilt/layout is $10/1000 pages. Ten one-page extraction passes would be approximately $0.015–$0.10 at these rates; this is not a claim that all ten are authorized within the model-call cap.
- Standard_GRS Hot blob data: $0.0368/GB-month initial tier, plus writes/reads/queues. Corpus is only2.59 MB.
- GPT-5-mini and embedding-3-large charge separately for actual tokens; no provisioned capacity is being purchased.
- No load testing. Original **12 live model-request cap including retries remains** unless explicitly increased. Stage ingestion and questions; do not automatically ingest all ten if that would exceed the cap.

## Quota/version preflight

- Central US regional vCPU and Ddsv5-family usage: **0 of100** each. Two workers require8 vCPU; no quota increase requested.
- East US GlobalStandard GPT-5-mini: **0 of1000 capacity units** used.
- East US GlobalStandard embedding-3-large: **0 of1000 capacity units** used.
- Requested capacities10/50 match the post-deployment guide's minimum10k GPT /50k embedding TPM.
- Exact Kubernetes1.34.2 appears in current Central US AKS version output.
- These checks are not a guarantee against policy, regional allocation or deployment-time failures.

## Ingress, secrets and procedural safety

- **Do not publish unauthenticated paid-model routes.** The dev ingress template is public and its backend service ports do not match the checked-in ClusterIP service ports. Do not blindly run the entire post-deployment script.
- Build and deploy the official three services and checked-in ClusterIP service manifest. Access through authenticated `kubectl port-forward --address 127.0.0.1`, using frontend8117/backend5117. Do not create public application ingress or a replacement app.
- This is a restrictive deployment procedure, not a speculative IaC/app rewrite. No WAF/premium infrastructure is substituted.
- Skip the script's unconditional nodepool upgrade; it could create surge workers beyond the approved short-test envelope.
- Use Azure identity for AI/Search/Storage. Existing shared Foundry is not reused. The template places its new Cosmos Mongo credential in Azure App Configuration; never export configuration contents/keys to logs, files or source.
- Top-level deployment outputs were inspected: names, IDs/endpoints and disabled monitoring fields only. Do not dump secure nested deployment outputs.
- Local build/runtime config may contain public service endpoints only; no secrets in source or OneDrive.

## Stop and residual cost commitment

After verification (or an unrecoverable app blocker), stop **only `aks-dkmeval0911a`** using `az aks stop`, then verify `powerState.code=Stopped`. Do not delete the RG or resources.

Expected paused residual baseline approximately **$0.36/hour**, with a conservative storage/Cosmos allowance up to about **$0.48/hour**: Search, ACR, App Configuration, Cosmos, disks and IP/network resources persist. Stopping is not zero cost. Actual inventory and billing dimensions must replace estimates in the final report.

Restart command will target the same subscription/RG/cluster with `az aks start`, refresh credentials and verify deployments before reopening localhost port-forwards. A restart is itself a return to compute billing; no automatic restart after final pause.

Reference: https://learn.microsoft.com/en-us/azure/aks/start-stop-cluster . Capacity is released on stop; a future restart can encounter availability constraints. No success/restart/E2E claim is made until verified.
# Revised worker selection — 2026-09-11 20:23 -04:00

The20:12 coordinator exception permits an equivalent x64,4-vCPU/16-GiB worker. Selected `Standard_D4s_v6` in Central US, initial2/max2, unchanged nonzonal placement. Only Zone3 is restricted; no Location restriction. Dsv6-family and regional quota0/100. Cosmos regular regional access allowed; DI S0 unrestricted; other service provider metadata supports this region. Official runtime persistence is Azure-backed; no ephemeral local disk requirement exists.

Exact source adaptation: `aksNodeVmSize` parameter, allowed original D4ds_v5 or selected D4s_v6, original default preserved; one vmSize reference changed. Bicep compilation, official parameter validation and Azure group validation succeeded. Compiled artifact `dkm-adapted-main.json`; all other intended resources, names, model capacities and secure access/pause plan below remain unchanged.

Azure Retail Prices API meter `1b3fa6d6-532d-55e2-8a78-a3ce7a8a4764` quotes Central US Linux D4s_v6 **$0.228/hour**, Consumption. Two workers$0.456/hour; replace former$0.510/hour line only. Revised **expected fixed$0.914775/hour; conservative$1.034775/hour; planning allowance$1.10/hour**, below approved$1.50/hour. Model/page/transaction/network usage and taxes extra; estimate is not a hard billing cap. No Spot, reservation or provisioned-model purchase.

Exact inventory below was recorded before the upcoming revised deployment. Details and12-entry alternative matrix: `equivalent-worker-preflight.json`.
