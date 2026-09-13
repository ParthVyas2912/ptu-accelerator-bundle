[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('api','processor','workflow','web')][string]$Service,
    [string]$PreviousKnownGoodImage,
    [ValidateRange(60,300)][int]$TimeoutSeconds = 180
)
$ErrorActionPreference = 'Stop'
$guard = Join-Path (Split-Path $PSScriptRoot -Parent) 'Invoke-LabAz.ps1'
$name = "ca-ptu-content-$Service"
$deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
do {
    $state = & $guard -AzArguments @('containerapp','show','-g','rg-ptu-content-demo','-n',$name,
        '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
        '--query','{latest:properties.latestRevisionName,ready:properties.latestReadyRevisionName,status:properties.runningStatus}',
        '-o','json') | ConvertFrom-Json
    if ($state.latest -and $state.latest -eq $state.ready -and $state.status -eq 'Running') {
        "Revision ready: $name / $($state.latest). This is not a completed claim test."
        return
    }
    Start-Sleep -Seconds 15
} while ([DateTime]::UtcNow -lt $deadline)
Write-Warning "READINESS ALERT: $name did not become ready within the bounded interval."
if ($PreviousKnownGoodImage) {
    $prefix = "acrptubundle7d804f70.azurecr.io/content/"
    if (-not $PreviousKnownGoodImage.StartsWith($prefix) -or
        $PreviousKnownGoodImage -notmatch "(official|eval)-$Service(:|@sha256:)") {
        throw 'Rollback image must be an explicitly verified same-service image in the approved registry.'
    }
    & $guard -AzArguments @('containerapp','update','-g','rg-ptu-content-demo','-n',$name,
        '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
        '--image',$PreviousKnownGoodImage,'--min-replicas','0','--max-replicas','1','-o','none')
    throw "Readiness failed; automatically restored the supplied known-good image for $name at min0/max1."
}
throw "Readiness failed; no known-good image supplied. No fabricated fallback or network change was applied."
