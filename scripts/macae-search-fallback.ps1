[CmdletBinding()]
param([ValidateSet('validate','create')][string]$Action = 'validate')
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$contract = Get-Content (Join-Path $b 'deployment-contract.json') -Raw | ConvertFrom-Json
if ($contract.subscriptionId -ne '1feb53b2-854a-4ea7-b5a6-709b7d804f70' -or -not $contract.approvedExceptions.macae) {
    throw 'MACAE subscription/approval mismatch.'
}
$repo = Join-Path $contract.repoRoot 'Multi-Agent-Custom-Automation-Engine-Solution-Accelerator'
# Parent explicitly approved US/Canadian Basic regional fallback on 2026-09-11.
# Invoke the official full-properties resource module directly: the two-stage
# wrapper would initially omit PNA/Entra settings. Original source is unchanged.
Write-Output 'Canada Central Basic1x1 semantic-free fixed baseline: USD0.101/hour (~USD73.73/730h), retail API verified. Cross-region from EastUS2 data/Foundry; synthetic data only. No SKU escalation.'
& (Join-Path $b 'Invoke-LabAz.ps1') -AzArguments @(
    'deployment','group',$Action,'--subscription',$contract.subscriptionId,
    '--resource-group','rg-ptu-macae-demo','--name','ptu-macae-search-canadacentral',
    '--template-file',(Join-Path $repo 'infra\bicep\modules\ai\ai-search-identity.bicep'),
    '--parameters',('@'+(Join-Path $PSScriptRoot 'macae-search-canadacentral.parameters.json')),
    '--query','{state:properties.provisioningState,error:error,outputs:properties.outputs}','-o','json'
)
if ($LASTEXITCODE -ne 0) { throw "Search $Action failed; no automatic regional retry or upgrade." }
