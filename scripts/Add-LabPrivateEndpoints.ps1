[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('macae', 'modernize', 'content', 'conversation', 'chatbot', 'documents')]
    [string]$App,
    [Parameter(Mandatory)]
    [string]$ParametersFile,
    [switch]$ValidateOnly
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$contract = Get-Content -LiteralPath (Join-Path $root 'deployment-contract.json') -Raw | ConvertFrom-Json
$parametersPath = (Resolve-Path -LiteralPath $ParametersFile).Path
$parameters = Get-Content -LiteralPath $parametersPath -Raw | ConvertFrom-Json
$endpoints = @($parameters.parameters.endpoints.value)
$allowedGroups = @{
    macae = @('rg-ptu-macae-demo')
    modernize = @('rg-ptu-modernize-demo')
    content = @('rg-ptu-content-demo')
    conversation = @('rg-ptu-conversation-demo')
    chatbot = @('rg-ptu-chatbot-eval')
    documents = @('accel-dkm-20260911')
}
$zoneMap = @{
    Sql = 'privatelink.documents.azure.com'
    MongoDB = 'privatelink.mongo.cosmos.azure.com'
    blob = 'privatelink.blob.core.windows.net'
    queue = 'privatelink.queue.core.windows.net'
    configurationStores = 'privatelink.azconfig.io'
    searchService = 'privatelink.search.windows.net'
    sqlServer = 'privatelink.database.windows.net'
    account = @('privatelink.cognitiveservices.azure.com', 'privatelink.openai.azure.com', 'privatelink.services.ai.azure.com')
}
if ($endpoints.Count -lt 1 -or $endpoints.Count -gt 4) {
    throw 'Supply one to four approved private endpoints for this app.'
}
foreach ($endpoint in $endpoints) {
    if ($endpoint.app -ne $App -or $endpoint.name -notmatch "^pe-$([regex]::Escape($App))-[a-z0-9-]+$") {
        throw 'Every endpoint must carry this app name and a pe-<app>- prefix.'
    }
    if ($endpoint.resourceId -notmatch '(?i)^/subscriptions/(?<subscription>[^/]+)/resourceGroups/(?<group>[^/]+)/providers/') {
        throw 'Invalid target Azure resource ID.'
    }
    if ($Matches.subscription -ne $contract.subscriptionId) {
        throw 'Cross-subscription private endpoints are not allowed.'
    }
    $targetGroup = $Matches.group
    $appScopedAlternative = ($App -eq 'chatbot' -and $targetGroup -like 'accel-chatbot-*') -or
        ($App -eq 'conversation' -and $targetGroup -like 'accel-conversation-*')
    if ($targetGroup -notin $allowedGroups[$App] -and -not $appScopedAlternative) {
        throw "Target resource group $targetGroup is not approved for $App."
    }
    $actualZones = if ($endpoint.PSObject.Properties.Name -contains 'zoneNames') { @($endpoint.zoneNames) } else { @($endpoint.zoneName) }
    if (-not $zoneMap.ContainsKey($endpoint.groupId) -or $actualZones.Count -eq 0 -or
        @($actualZones | Where-Object { [string]::IsNullOrWhiteSpace($_) }).Count -gt 0) {
        throw "Unapproved private-link group/DNS zone combination: $($endpoint.groupId)."
    }
    $expectedZones = @($zoneMap[$endpoint.groupId])
    if ($actualZones.Count -ne $expectedZones.Count -or
        @(Compare-Object -ReferenceObject $expectedZones -DifferenceObject $actualZones).Count -gt 0) {
        throw "Unapproved private-link group/DNS zone combination: $($endpoint.groupId)."
    }
}

$template = Join-Path $root 'infra\app-private-endpoints.bicep'
$common = @(
    '--subscription', $contract.subscriptionId,
    '--resource-group', 'rg-ptu-bundle-platform',
    '--name', "ptu-$App-private-endpoints",
    '--template-file', $template,
    '--parameters', "@$parametersPath"
)
& az deployment group validate @common --query properties.provisioningState -o tsv
if ($LASTEXITCODE -ne 0) {
    throw 'Private endpoint template validation failed.'
}
if (-not $ValidateOnly) {
    & az deployment group create @common --query properties.outputs -o json
    if ($LASTEXITCODE -ne 0) {
        throw 'Private endpoint deployment failed; inspect its operations before retrying.'
    }
}
