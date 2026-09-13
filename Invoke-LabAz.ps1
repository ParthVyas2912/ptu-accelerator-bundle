[CmdletBinding()]
param(
    [switch]$ValidateOnly,
    [Parameter(Mandatory, ValueFromRemainingArguments)]
    [string[]]$AzArguments
)

$ErrorActionPreference = 'Stop'
$contract = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'deployment-contract.json') -Raw | ConvertFrom-Json
$inventory = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'evidence\protected-resources.json') -Raw | ConvertFrom-Json
$joined = $AzArguments -join ' '

if ($AzArguments | Where-Object { $_ -in @('delete', 'purge', 'destroy', 'down') }) {
    throw 'Automatic destructive Azure commands are disabled for this lab.'
}
if ($joined -match 'GlobalProvisionedManaged|DataZoneProvisionedManaged|ProvisionedManaged|reservations?') {
    throw 'Provisioned capacity and reservation operations are disabled for this lab.'
}

$readOnly = ($AzArguments | Where-Object { $_ -in @('show', 'list', 'list-skus', 'list-usages', 'get-credentials') }).Count -gt 0
if ($AzArguments[0] -eq 'rest') {
    $readOnly = $false
    $methodIndex = [Array]::IndexOf($AzArguments, '--method')
    if ($methodIndex -ge 0 -and $methodIndex + 1 -lt $AzArguments.Length) {
        $readOnly = $AzArguments[$methodIndex + 1] -in @('get', 'GET')
    }
}
if (-not $readOnly) {
    $subscriptionIndex = [Array]::IndexOf($AzArguments, '--subscription')
    if ($subscriptionIndex -lt 0 -or $subscriptionIndex + 1 -ge $AzArguments.Length -or
        $AzArguments[$subscriptionIndex + 1] -ne $contract.subscriptionId) {
        throw "Mutating commands must explicitly target subscription $($contract.subscriptionId)."
    }
    $protectedGroups = @($contract.protectedResourceGroups) + @($inventory.resourceGroup) | Sort-Object -Unique
    foreach ($group in $protectedGroups) {
        if ($joined -match "(?i)(?<![\w-])$([regex]::Escape($group))(?![\w-])") {
            throw "Mutation rejected: protected resource group $group."
        }
    }
    if ($AzArguments[0] -eq 'rest') {
        throw 'Mutating REST requests need separate inspection of their payload and are not supported by this wrapper.'
    }
}

if ($ValidateOnly) {
    'Command passed the lab guard. This is not a cost estimate or deployment approval.'
    return
}

& az @AzArguments
if ($LASTEXITCODE -ne 0) {
    throw "Azure CLI failed with exit code $LASTEXITCODE."
}
