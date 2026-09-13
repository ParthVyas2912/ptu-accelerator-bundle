[CmdletBinding()]
param(
    [string]$StartTime = '2026-09-11T22:52:00Z'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$contract = Get-Content -LiteralPath (Join-Path $root 'deployment-contract.json') -Raw | ConvertFrom-Json
$baseline = Get-Content -LiteralPath (Join-Path $root 'azure-resources-before.json') -Raw | ConvertFrom-Json
$baselineIds = @{}
foreach ($resource in $baseline) {
    $baselineIds[$resource.id.ToLowerInvariant()] = $true
}
$directory = Join-Path $root 'evidence\model-metrics'
New-Item -ItemType Directory -Force -Path $directory | Out-Null
$endTime = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
$accounts = az cognitiveservices account list --subscription $contract.subscriptionId -o json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to inventory model accounts.'
}
$dedicatedAccounts = @($accounts | Where-Object {
    $_.kind -in @('OpenAI', 'AIServices') -and
    -not $baselineIds.ContainsKey($_.id.ToLowerInvariant()) -and
    ($_.resourceGroup -like 'rg-ptu-*' -or $_.resourceGroup -like 'accel-*')
})
$summary = foreach ($account in $dedicatedAccounts) {
    $raw = az monitor metrics list --subscription $contract.subscriptionId --resource $account.id `
        --metric AzureOpenAIRequests ProcessedPromptTokens GeneratedTokens `
        --aggregation Total --interval PT1M --filter "ModelDeploymentName eq '*'" `
        --start-time $StartTime --end-time $endTime -o json
    if ($LASTEXITCODE -ne 0) {
        throw "Metrics query failed for $($account.name); do not interpret missing metrics as zero."
    }
    $raw | Set-Content -LiteralPath (Join-Path $directory "$($account.name).json") -Encoding utf8
    $response = $raw | ConvertFrom-Json
    $metrics = foreach ($metric in $response.value) {
        if ($metric.errorCode -and $metric.errorCode -ne 'Success') {
            throw "Metric $($metric.name.value) failed for $($account.name): $($metric.errorCode) $($metric.errorMessage)"
        }
        $deployments = @(foreach ($series in $metric.timeseries) {
            $deployment = @($series.metadatavalues | Where-Object { $_.name.value -eq 'ModelDeploymentName' })
            $seriesPoints = @($series.data | Where-Object { $null -ne $_.total })
            $seriesTotal = if ($seriesPoints.Count -gt 0) { ($seriesPoints | Measure-Object -Property total -Sum).Sum } else { $null }
            $deploymentName = if ($deployment.Count -eq 1) { $deployment[0].value } else { $null }
            if (-not $deploymentName -and $seriesPoints.Count -gt 0) {
                Write-Warning "Unattributed model series: $($account.name), $($metric.name.value). Preserve it separately from named deployments."
            }
            [ordered]@{
                deploymentName = $deploymentName
                total = $seriesTotal
                returnedNonNullPoints = $seriesPoints.Count
            }
        })
        $points = @($metric.timeseries | ForEach-Object { $_.data } | Where-Object { $null -ne $_.total })
        $total = if ($points.Count -gt 0) { ($points | Measure-Object -Property total -Sum).Sum } else { $null }
        [ordered]@{
            metric = $metric.name.value
            unit = $metric.unit
            total = $total
            returnedNonNullPoints = $points.Count
            deployments = $deployments
        }
    }
    [ordered]@{
        account = $account.name
        resourceGroup = $account.resourceGroup
        resourceId = $account.id
        startTimeUtc = $StartTime
        endTimeUtc = $endTime
        metrics = @($metrics)
        attribution = 'New dedicated lab account only, split by ModelDeploymentName. Account totals and deployment series are the same observations, not additive. Includes service-mediated calls visible to these metrics. Reporting delay and differing instrumentation boundaries can cause differences from SDK evidence.'
    }
}
@($summary) | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $directory 'summary.json') -Encoding utf8
$summary | ForEach-Object {
    $account = $_
    $_.metrics | ForEach-Object {
        [pscustomobject]@{ account = $account.account; metric = $_.metric; total = $_.total; points = $_.returnedNonNullPoints }
    }
} | Format-Table -AutoSize
