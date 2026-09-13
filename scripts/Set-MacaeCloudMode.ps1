[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('Start','Pause','EnableInference')][string]$Mode)
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$file = Join-Path $PSScriptRoot 'macae-cloud.parameters.json'
$p = Get-Content $file -Raw | ConvertFrom-Json
$p.parameters.liveRequestsEnabled.value = $false
$p.parameters.minReplicas.value = if ($Mode -eq 'Pause') { 0 } else { 1 }
if ($Mode -eq 'EnableInference') {
    $readiness = Get-Content (Join-Path $b 'evidence\macae\cloud-readiness.json') -Raw | ConvertFrom-Json
    if (-not $readiness.success) { throw 'Actual cloud private-readiness proof required.' }
    if (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8111 -State Listen -ErrorAction SilentlyContinue) {
        throw 'Separate local inference process must remain stopped.'
    }
    & (Join-Path $PSScriptRoot 'Invoke-MacaeCloudTest.ps1') -Action ledger
    $ledger = Get-Content (Join-Path $b 'evidence\macae\cloud-model-ledger.json') -Raw | ConvertFrom-Json
    if ($ledger.limit -ne 24 -or $ledger.used -ge 24) { throw 'Approved total24 live model allowance unavailable.' }
    $p.parameters.liveRequestsEnabled.value = $true
}
[IO.File]::WriteAllText($file,($p | ConvertTo-Json -Depth 15))
& (Join-Path $PSScriptRoot 'Deploy-MacaeCloud.ps1')
