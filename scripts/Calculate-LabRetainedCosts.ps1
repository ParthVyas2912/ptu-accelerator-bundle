[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$directory = Join-Path $root 'evidence\costs'
$assumptions = Get-Content -LiteralPath (Join-Path $directory 'retained-cost-assumptions.json') -Raw | ConvertFrom-Json
$delta = Get-Content -LiteralPath (Join-Path $root 'evidence\azure-resource-delta.json') -Raw | ConvertFrom-Json
$expectedCounts = @{
    'Microsoft.Search/searchServices' = 4
    'Microsoft.AppConfiguration/configurationStores' = 2
    'Microsoft.Network/privateEndpoints' = 18
    'Microsoft.Network/privateDnsZones' = 10
    'Microsoft.ContainerRegistry/registries' = 1
}
foreach ($type in $expectedCounts.Keys) {
    $actual = @($delta.newResourcesSinceBaseline | Where-Object type -eq $type).Count
    if ($actual -ne $expectedCounts[$type]) {
        throw "Inventory changed for $type ($actual); review assumptions instead of publishing a stale estimate."
    }
}
$items = @(foreach ($item in $assumptions.items) {
    $hours = switch ($item.period) {
        'hour' { 1 }
        'day' { 24 }
        'month' { $assumptions.hoursPerMonth }
        default { throw "Unsupported price period: $($item.period)" }
    }
    [pscustomobject]@{
        component = $item.component
        quantity = $item.quantity
        hourlyEquivalent = $item.quantity * $item.unitPrice / $hours
        basis = $item.basis
    }
})
$base = ($items | Measure-Object hourlyEquivalent -Sum).Sum
$scenarios = @(foreach ($vcores in @(0, $assumptions.sqlCompute.minimumConfiguredVcores, $assumptions.sqlCompute.maximumConfiguredVcores)) {
    $hourly = $base + $vcores * $assumptions.sqlCompute.unitPricePerBilledVcoreHour
    [pscustomobject]@{
        sqlBilledVcores = $vcores
        condition = if ($vcores -eq 0) { 'SQL actually paused' } else { "SQL billed at $vcores vCores; not measured usage" }
        usdPerHour = $hourly
        usdPer24Hours = $hourly * 24
        usdPer730Hours = $hourly * $assumptions.hoursPerMonth
    }
})
[ordered]@{
    calculatedAtUtc = [datetime]::UtcNow.ToString('o')
    resourceSnapshotAtUtc = $delta.observedAtUtc
    currency = $assumptions.currency
    items = $items
    scenarios = $scenarios
    caveat = $assumptions.caveat
    exclusions = $assumptions.exclusions
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $directory 'retained-cost-estimate.json') -Encoding utf8
$scenarios | Format-Table -AutoSize
