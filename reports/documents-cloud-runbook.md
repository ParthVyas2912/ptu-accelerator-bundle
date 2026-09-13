# DKM cloud runtime — controlled restart and pause

## Scope and known state

This is the **approved hosting adaptation of the original DKM services**, not the stock AKS deployment. Stock AKS creation failed with `AKSCapacityHeavyUsage`; no AKS resource exists.

Own RG: `accel-dkm-20260911`, subscription `1feb53b2-854a-4ea7-b5a6-709b7d804f70`. Shared Consumption environment/ACR are referenced, not recreated. Cosmos/Storage PNA remain Disabled. No secrets are required in local files or printed commands.

Verified: actual Kernel Memory health200, internal Mongo-backed API200, **two real ingestions**, PDF table values, metadata filters, persisted source hashes, and document-scoped `/Documents/Ask` with the correct2025/10-day answer and citation. **Full browser E2E is not verified:** approved client received403 despite the matching CIDR allowlist. Both summaries contain an unrelated greeting preface. The original corpus response was lost, but the explicitly approved2-attempt repeat is now verified with both citations and correct10-to15/+5/+50% comparison; fullJSON is durable in ownedBlob.

## Pause, resume, status

From the bundle directory:

```powershell
.\scripts\Set-DocumentsRuntime.ps1 -Action Pause
.\scripts\Set-DocumentsRuntime.ps1 -Action Status
.\scripts\Set-DocumentsRuntime.ps1 -Action Resume
```

Pause deactivates only active revisions of `ca-dkm-web`, `ca-dkm-api`, and `ca-dkm-kernel`, preserving resources/images/configuration/data. Resume activates each latest ready revision, in kernel/API/frontend order, skipping already-active revisions. Existing test revisions use min1/max1; when inactive they consume no replica compute. Wait for status/replica readiness before health checks. Activation command success alone is not a health test.

**This cycle was executed and verified:** Pause → Resume → actual Kernel Memory health200 plus original backend200 with the persisted document count2 and both downloaded source hashes matching → Pause again. Latest verification is stored in`evidence/documents/comparison14-final-runtime-state.json` and`comparison14-persistence.json`; the earlier restart proof is retained. The full public browser route remains unverified/403; restart verification is specifically for the original service core and persisted data.

The exact image/configuration deployment can also be reproduced with:

```powershell
.\scripts\Deploy-DocumentsContainer.ps1 -Component kernelmemory -MinimumReplicas 1 -ImageTag 7df8ed3-evalretry-r1 -EvaluationMaxModelRetries 0
.\scripts\Deploy-DocumentsContainer.ps1 -Component backend -MinimumReplicas 1 -ImageTag 7df8ed3-evalretry-r1 -EvaluationMaxModelRetries 0
.\scripts\Deploy-DocumentsContainer.ps1 -Component frontend -MinimumReplicas 1 -ImageTag 7df8ed3-aca20260911
```

All three allocations are1CPU/2GiB, max1. For on-demand operation, use `-MinimumReplicas 0`, but do not mistake min0 for immediate deactivation. Explicit Pause is the stop procedure.

## Endpoints and private routing

- Frontend: `https://ca-dkm-web.victoriouscliff-b4bf9ff1.eastus2.azurecontainerapps.io` — public only through the configured `174.112.74.34/32` allowlist; currently observed403. **Never widen this allowlist as a workaround.**
- Backend, environment-internal: `http://ca-dkm-api:80`
- Kernel Memory, environment-internal: `http://ca-dkm-kernel:80`; `/health` returns200.
- Actual containers listen9001 for backend/KM and5900 for Vite.
- Frontend uses original `/backend` proxy to the internal backend.
- App Configuration's documented `Application:Services:KernelMemory:Endpoint` key is `http://ca-dkm-kernel`.
- No new local listener is exposed on8117/5117. This cloud adaptation is not represented as a locally running app.

Private DNS was verified **inside the original backend container**: Mongo`10.246.2.11`, Blob`10.246.2.13`, Queue`10.246.2.10`. Exact resource/group/DNS requirements and helper parameters are in `evidence/documents/private-endpoint-requirements.json` and `private-endpoints.parameters.json`. No extra private endpoints are needed.

## Model budget and test safety

**14/14 OpenAI attempts used; guard disarmed; no further inference authorized.** All account statuses200. Total9836tokens (2412input,7424output), including the original12 attempts. DI remains separate:1processed page,3successfulHTTPcalls. See`comparison14-final-metrics-summary.json`.

Do not repeat any ingestion or QA case: it would duplicate a completed/attempted operation and exceed the cap. Do not run a load test or the unbounded upstream E2E suite. Resume is authorized for read-only health/persistence verification, not new inference.

The approved `DKM_EVAL_MAX_MODEL_RETRIES=0` opt-in is deployed on both backend/KM. Unset/empty preserves original production construction; invalid values fail before client creation. Remote regression run`chg` passed29 assertions with fake-only transports. Original Dockerfiles rebuilt remotely: backend`che`; Kernel Memory`chh` used native Buildx in an ACR task because ACR's older dependency parser rejected the unchanged Dockerfile syntax.

Real request accounting:4first ingestion +4second ingestion +2document QA +2lost corpus attempt +2approved repeat =14. Both actual document-scoped and corpus comparison /Documents/Ask routes are verified; full/chat synthesis/suggestions remain untested. Recovery first found no previous result in ownedBlob/Mongo/history or stored responseID. The repeat saved fullJSON to `https://stdkmeval0911a.blob.core.windows.net/smemory/_dkm-evaluation/comparison14-result.json` before console export, then verified readback SHA256`99a60b96a6867bf9f96ff9297daf2d7497158b79f3cfa57f11a9357619327704` (9493bytes). Blob access uses existing managed identity over private networking, never keys/SAS. The permanent attempt-lock blob and `comparison14-guard.json` prevent an accidental repeat. Do not remove the lock or re-arm the guard to run more inference.

After a future authorized read-only Resume, durable response retrieval can restage the evaluator without inference:

```powershell
.\scripts\Invoke-DocumentsComparison14.ps1 -Mode read-result -Container smemory -EvidenceLabel operator-recovery-1 -Stage
```

Use a unique read-only evidence label; the command refuses overwriting existing local evidence. Console staging uses short chunks; honor any429Retry-After600 response rather than changing identities or ingress. No future comparison request is authorized by this runbook.

Safe read-only checks after Resume, with a unique evidence label:

```powershell
.\scripts\Invoke-DocumentsEvaluation.ps1 -Case health -Label operator-health-1
.\scripts\Invoke-DocumentsEvaluation.ps1 -Case sources -Label operator-sources-1
.\scripts\Set-DocumentsRuntime.ps1 -Action Pause
```

The controller and probes use authenticated control-plane exec; no new Entra application or widened public ingress is required.

## Costs that continue while paused

- Initial seven-PaaS baseline: **$0.183/hour**.
- The real app automatically created `DPS/Documents` at400RU/s: **+$0.032/hour**.
- Three PEs: approximately **+$0.03/hour**.
- Current paused subtotal: **~$0.245/hour (~$5.88/day)**, plus storage/operations/DNS/shared-platform allocation.
- Three fully active1CPU/2GiB replicas add approximately **$0.324/hour**; active subtotal **~$0.569/hour**, before shared allocations and variable usage.

These are retail estimates, not an invoice. Free grants are not assumed. No automatic deletion of any cloud resources is authorized.
