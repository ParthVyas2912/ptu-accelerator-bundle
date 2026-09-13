[CmdletBinding()]
param(
    [Parameter(Mandatory)][uri]$FrontendUrl,
    [string]$PreviousParametersFile,
    [switch]$RollbackOnFailure
)
$ErrorActionPreference = 'Stop'
if ($FrontendUrl.Scheme -ne 'https' -or $FrontendUrl.Host -notlike 'ptu-macae.*.azurecontainerapps.io') {
    throw 'Expected parent-supplied MACAE HTTPS Container Apps URL.'
}
try {
    $health = Invoke-RestMethod ([uri]::new($FrontendUrl, '/health')) -TimeoutSec 30
    $config = Invoke-RestMethod ([uri]::new($FrontendUrl, '/config')) -TimeoutSec 30
    if ($health.status -ne 'healthy' -or $config.API_URL -ne '/api') {
        throw 'Native frontend health or same-origin API configuration failed.'
    }
    Write-Output 'MACAE deployment smoke passed (health/config only, NOT workflow or private-dependency proof).'
} catch {
    $status = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
    if ($status -in 401,403) {
        throw 'Ingress/authentication denied the evaluator. Do not roll back or weaken access controls; verify from the approved client or authenticated cloud exec.'
    }
    Write-Warning 'MACAE deployment smoke FAILED. Alert: review ACA revision/system logs and private dependency probes.'
    if (-not $RollbackOnFailure) { throw }
    if (-not $PreviousParametersFile -or -not (Test-Path $PreviousParametersFile)) {
        throw 'No previous verified release parameters; cannot invent a rollback target.'
    }
    $p = Get-Content $PreviousParametersFile -Raw | ConvertFrom-Json
    if ($p.parameters.liveRequestsEnabled.value -eq $true) {
        throw 'Rollback parameters must leave live inference disabled until ledger checks pass.'
    }
    # Explicit parent-controlled operation. This script has not been executed
    # against cloud compute during preparation. Never mutates network/data/models.
    $b = Split-Path $PSScriptRoot -Parent
    & (Join-Path $b 'Invoke-LabAz.ps1') -AzArguments @(
        'deployment','group','create','--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
        '--resource-group','rg-ptu-macae-demo','--name','macae-image-rollback',
        '--template-file',(Join-Path $PSScriptRoot 'macae-shared-aca.bicep'),
        '--parameters',('@'+(Resolve-Path $PreviousParametersFile).Path),
        '--query','properties.provisioningState','-o','tsv'
    )
    if ($LASTEXITCODE -ne 0) { throw 'Automatic image rollback failed; parent intervention required.' }
    throw 'Failed release rolled back to parent-supplied image parameters; investigate before retry.'
}
