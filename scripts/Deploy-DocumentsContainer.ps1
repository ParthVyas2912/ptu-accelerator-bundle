[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('backend', 'kernelmemory', 'frontend')]
    [string]$Component,
    [ValidateSet(0, 1)]
    [int]$MinimumReplicas = 0,
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')]
    [string]$ImageTag = '7df8ed3-aca20260911',
    [ValidateSet('', '0', '1', '2', '3')]
    [string]$EvaluationMaxModelRetries = '',
    [switch]$ValidateOnly
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$platform = Get-Content (Join-Path $root 'evidence\preflight\lab-platform-outputs.json') -Raw | ConvertFrom-Json
$ingress = Get-Content (Join-Path $root 'evidence\preflight\lab-ingress.json') -Raw | ConvertFrom-Json
$subscription = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$identity = "/subscriptions/$subscription/resourceGroups/accel-dkm-20260911/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id-dkmeval0911a"
$registry = $platform.registryLoginServer.value
$image = "$registry/dkm/${Component}:$ImageTag"
if ($platform.environmentName.value -ne 'cae-ptu-bundle' -or $registry -ne 'acrptubundle7d804f70.azurecr.io') {
    throw 'Unexpected shared platform; refusing deployment.'
}
if ($ingress.clientCidr -ne '174.112.74.34/32') {
    throw 'Client CIDR changed: review approved ingress before exposing frontend.'
}
$common = @(
    '--resource-group', 'accel-dkm-20260911',
    '--name', "dkm-aca-$Component",
    '--template-file', (Join-Path $root 'infra\documents-containerapp.bicep'),
    '--subscription', $subscription,
    '--parameters',
    "component=$Component",
    "image=$image",
    "environmentId=$($platform.environmentId.value)",
    "runtimeIdentityId=$identity",
    'runtimeClientId=a8b91884-b691-4445-846d-e3642418e2a2',
    "registryServer=$registry",
    "clientCidr=$($ingress.clientCidr)",
    "minimumReplicas=$MinimumReplicas",
    "evaluationMaxModelRetries=$EvaluationMaxModelRetries"
)
$operation = if ($ValidateOnly) { 'validate' } else { 'create' }
& (Join-Path $root 'Invoke-LabAz.ps1') -AzArguments (@('deployment', 'group', $operation) + $common +
    @('--query', '{state:properties.provisioningState,outputs:properties.outputs,error:properties.error}', '-o', 'json'))
