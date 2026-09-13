[CmdletBinding()]
param(
    [datetime]$StartDate = [datetime]'2026-09-11'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$contract = Get-Content -LiteralPath (Join-Path $root 'deployment-contract.json') -Raw | ConvertFrom-Json
$delta = Get-Content -LiteralPath (Join-Path $root 'evidence\azure-resource-delta.json') -Raw | ConvertFrom-Json
$directory = Join-Path $root 'evidence\costs'
New-Item -ItemType Directory -Force -Path $directory | Out-Null
$anchorNames = @(
    'cae-ptu-bundle', 'ptumacae7d804f70', 'aif-ccptu1feb0911',
    'aif-ptuv-content-260911', 'ca-ptu-modernize-api',
    'ca-ptu-conversation-api', 'oai-dkmeval0911a'
)
$groups = @($delta.newResourcesSinceBaseline |
    Where-Object { $_.name -in $anchorNames } |
    Select-Object -ExpandProperty resourceGroup -Unique)
$environment = az containerapp env show --name cae-ptu-bundle --resource-group rg-ptu-bundle-platform `
    --subscription $contract.subscriptionId -o json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Unable to read the lab environment managed-resource-group association.' }
$managedGroup = $environment.properties.infrastructureResourceGroup
if (-not $managedGroup) { throw 'Missing managed-resource-group association; do not silently omit shared networking costs.' }
$groups += $managedGroup
$body = @{
    type = 'ActualCost'
    timeframe = 'Custom'
    timePeriod = @{
        from = $StartDate.ToString('yyyy-MM-ddT00:00:00Z')
        to = [datetime]::UtcNow.Date.AddDays(1).ToString('yyyy-MM-ddT00:00:00Z')
    }
    dataset = @{
        granularity = 'Daily'
        aggregation = @{ totalCost = @{ name = 'PreTaxCost'; function = 'Sum' } }
        grouping = @(
            @{ type = 'Dimension'; name = 'ResourceGroupName' },
            @{ type = 'Dimension'; name = 'ServiceName' }
        )
    }
}
$requestPath = Join-Path $directory 'request.json'
$body | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $requestPath -Encoding utf8
$url = "https://management.azure.com/subscriptions/$($contract.subscriptionId)/providers/Microsoft.CostManagement/query?api-version=2023-03-01"
$credential = az account get-access-token --resource https://management.azure.com/ `
    --subscription $contract.subscriptionId -o json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or -not $credential.accessToken) {
    throw 'Unable to obtain the authorized ARM token for the read-only cost query.'
}
# A stable application identifier avoids sharing the anonymous ClientType quota.
$headers = @{
    Authorization = "Bearer $($credential.accessToken)"
    ClientType = 'PTU-Bundle-Accelerator-Report'
}
try {
    $httpResponse = Invoke-WebRequest -Method Post -Uri $url -Headers $headers `
        -ContentType 'application/json' -Body ($body | ConvertTo-Json -Depth 10) `
        -SkipHttpErrorCheck -TimeoutSec 90
}
finally {
    $headers.Remove('Authorization')
    $credential = $null
}
$raw = $httpResponse.Content
if ($httpResponse.StatusCode -lt 200 -or $httpResponse.StatusCode -ge 300) {
    $retryHeaders = @{}
    foreach ($name in $httpResponse.Headers.Keys) {
        if ($name -match 'retry-after') { $retryHeaders[$name] = $httpResponse.Headers[$name] -join ',' }
    }
    [ordered]@{
        observedAtUtc = [datetime]::UtcNow.ToString('o')
        statusCode = [int]$httpResponse.StatusCode
        retryHeaders = $retryHeaders
        interpretation = 'Actual spending is unavailable, not zero. Honor returned retry intervals before another query.'
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $directory 'failure.json') -Encoding utf8
    throw "Cost query returned HTTP $($httpResponse.StatusCode); see evidence\costs\failure.json for retry guidance."
}
$raw | Set-Content -LiteralPath (Join-Path $directory 'response.json') -Encoding utf8
$response = $raw | ConvertFrom-Json
if ($response.properties.nextLink) {
    throw 'Cost response is paginated. Follow nextLink before reporting totals; the first page has been retained.'
}
$columns = @{}
for ($i = 0; $i -lt $response.properties.columns.Count; $i++) {
    $columns[$response.properties.columns[$i].name] = $i
}
foreach ($name in @('PreTaxCost', 'UsageDate', 'ResourceGroupName', 'ServiceName', 'Currency')) {
    if (-not $columns.ContainsKey($name)) { throw "Unexpected cost response: missing $name." }
}
$rows = @(foreach ($row in $response.properties.rows) {
    [pscustomobject]@{
        cost = [double]$row[$columns.PreTaxCost]
        usageDate = $row[$columns.UsageDate]
        resourceGroup = $row[$columns.ResourceGroupName]
        service = $row[$columns.ServiceName]
        currency = $row[$columns.Currency]
        labGroupMatch = $row[$columns.ResourceGroupName] -in $groups
    }
})
$currencies = @($rows.currency | Sort-Object -Unique)
if ($currencies.Count -gt 1) { throw 'Multiple currencies returned; do not combine unlike monetary units.' }
$labRows = @($rows | Where-Object labGroupMatch)
$summary = [ordered]@{
    observedAtUtc = [datetime]::UtcNow.ToString('o')
    queryStatus = 'Succeeded'
    clientType = $headers.ClientType
    requestedPeriod = $body.timePeriod
    matchedResourceGroups = $groups
    currency = if ($currencies.Count -eq 1) { $currencies[0] } else { $null }
    reportedSubscriptionSubtotal = if ($rows.Count) { ($rows | Measure-Object cost -Sum).Sum } else { $null }
    reportedLabGroupSubtotal = if ($labRows.Count) { ($labRows | Measure-Object cost -Sum).Sum } else { $null }
    returnedLabRows = $labRows.Count
    coverage = 'Reported usage only, subject to billing delay; not a final invoice or remaining-credit balance. Subscription subtotal includes pre-existing and concurrent workloads. Missing lab rows do not mean zero cost. Lab-group subtotal excludes any model usage billed to pre-existing shared EDC groups.'
    labRows = $labRows
}
$summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $directory 'summary.json') -Encoding utf8
[pscustomobject]$summary | Select-Object observedAtUtc, currency, reportedSubscriptionSubtotal, reportedLabGroupSubtotal, returnedLabRows, coverage | Format-List
