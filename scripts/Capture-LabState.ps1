[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$contract = Get-Content -LiteralPath (Join-Path $root 'deployment-contract.json') -Raw | ConvertFrom-Json
$baseline = Get-Content -LiteralPath (Join-Path $root 'azure-resources-before.json') -Raw | ConvertFrom-Json
$raw = az resource list --subscription $contract.subscriptionId -o json
if ($LASTEXITCODE -ne 0) {
    throw 'Azure resource inventory failed; no final snapshot was written.'
}
$current = $raw | ConvertFrom-Json
$baselineIds = @{}
foreach ($resource in $baseline) {
    $baselineIds[$resource.id.ToLowerInvariant()] = $true
}
$newResources = @($current | Where-Object {
    -not $baselineIds.ContainsKey($_.id.ToLowerInvariant())
} | Select-Object id, name, type, location, resourceGroup, sku, tags)
$currentIds = @{}
foreach ($resource in $current) {
    $currentIds[$resource.id.ToLowerInvariant()] = $true
}
$missingBaseline = @($baseline | Where-Object {
    -not $currentIds.ContainsKey($_.id.ToLowerInvariant())
} | Select-Object id, name, type, resourceGroup)

$snapshot = [ordered]@{
    observedAtUtc = [DateTime]::UtcNow.ToString('o')
    subscriptionId = $contract.subscriptionId
    newResourcesSinceBaseline = $newResources
    baselineResourcesNoLongerListed = $missingBaseline
    attributionCaveat = 'A subscription is shared. Additions or removals are not automatically attributable to this lab; compare per-app evidence and tags. This inventory does not detect all configuration or data-plane changes.'
}
$snapshot | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $root 'evidence\azure-resource-delta.json') -Encoding utf8
$newResources | Select-Object name, type, resourceGroup | Format-Table -AutoSize
if ($missingBaseline.Count -gt 0) {
    Write-Warning "$($missingBaseline.Count) baseline resources are no longer listed; investigate attribution before making preservation claims."
}
