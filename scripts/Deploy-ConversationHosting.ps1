[CmdletBinding()]
param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path -Parent $PSScriptRoot
$platform = Get-Content (Join-Path $bundle 'evidence\preflight\lab-platform-outputs.json') -Raw | ConvertFrom-Json
$ingress = Get-Content (Join-Path $bundle 'evidence\preflight\lab-ingress.json') -Raw | ConvertFrom-Json
$sub = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$registry = $platform.registryLoginServer.value
if ($registry -ne 'acrptubundle7d804f70.azurecr.io' -or
    $platform.environmentName.value -ne 'cae-ptu-bundle') {
    throw 'Unexpected shared platform; inspect before deployment.'
}
if ($ingress.clientCidr -ne '174.112.74.34/32') {
    throw 'Evaluator CIDR changed; review and update this guard, never broaden ingress automatically.'
}
$guard = Join-Path $bundle 'Invoke-LabAz.ps1'
$mi = & $guard -AzArguments @('identity','show','--name','id-ptu-conversation',
    '--resource-group','rg-ptu-conversation-demo','--subscription',$sub,'-o','json') | ConvertFrom-Json
$argsCommon = @('--subscription',$sub,'--resource-group','rg-ptu-conversation-demo',
    '--name','ptu-conversation-component-hosting',
    '--template-file',(Join-Path $bundle 'infra\conversation-hosting.bicep'),
    '--parameters',"environmentId=$($platform.environmentId.value)",
    "registryServer=$registry","identityResourceId=$($mi.id)","identityClientId=$($mi.clientId)",
    "clientCidr=$($ingress.clientCidr)",
    "apiImage=$registry/conversation/api:8a00aa5-base",
    "uiImage=$registry/conversation/ui:8a00aa5-runtime")
& $guard -AzArguments (@('deployment','group','validate') + $argsCommon +
    @('--query','properties.provisioningState','-o','tsv'))
if (-not $ValidateOnly) {
    & $guard -AzArguments (@('deployment','group','create') + $argsCommon +
        @('--query','properties.outputs','-o','json'))
}
