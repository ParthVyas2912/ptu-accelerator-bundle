[CmdletBinding()]
param([switch]$Deploy, [switch]$BackendOnly)
$ErrorActionPreference='Stop'
$B=Split-Path $PSScriptRoot -Parent
if ($Deploy) { & (Join-Path $PSScriptRoot 'Assert-ModernizeBudgetOpen.ps1') }
$guard=Join-Path $B 'Invoke-LabAz.ps1'
$sub='1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$platform=Get-Content (Join-Path $B 'evidence\preflight\lab-platform-outputs.json') -Raw | ConvertFrom-Json
$identity=Get-Content (Join-Path $B 'evidence\modernize\cloud-identities.json') -Raw | ConvertFrom-Json
$ingress=Get-Content (Join-Path $B 'evidence\preflight\lab-ingress.json') -Raw | ConvertFrom-Json
$images=Get-Content (Join-Path $B 'evidence\modernize\cloud-images.json') -Raw | ConvertFrom-Json
if ($ingress.clientCidr -notmatch '^\d+\.\d+\.\d+\.\d+/32$') { throw 'Exact single-client IPv4 restriction is required.' }
if ($platform.environmentId.value -notlike "/subscriptions/$sub/resourceGroups/rg-ptu-bundle-platform/*") { throw 'Unexpected shared environment scope.' }
$parameters=@{parameters=@{
    environmentId=@{value=$platform.environmentId.value}
    registryServer=@{value=$platform.registryLoginServer.value}
    backendIdentityId=@{value=$identity.backendIdentity.id}
    backendClientId=@{value=$identity.backendIdentity.clientId}
    frontendIdentityId=@{value=$identity.frontendPullOnlyIdentity.id}
    clientCidr=@{value=$ingress.clientCidr}
    backendImage=@{value='acrptubundle7d804f70.azurecr.io/modernize/backend:7592ea9-eval1'}
    frontendImage=@{value='acrptubundle7d804f70.azurecr.io/modernize/frontend:7592ea9'}
    backendMinReplicas=@{value=1}
    deployFrontend=@{value=(-not $BackendOnly)}
}}
$path=Join-Path $B 'evidence\modernize\cloud-apps.parameters.json'
[System.IO.File]::WriteAllText($path,($parameters | ConvertTo-Json -Depth 8))
$common=@('--subscription',$sub,'--resource-group','rg-ptu-modernize-demo',
    '--name','ptu-modernize-cloud','--template-file',(Join-Path $PSScriptRoot 'modernize_cloud_apps.bicep'),
    '--parameters',"@$path",'-o','json')
& $guard -AzArguments (@('deployment','group','validate')+$common)
if ($LASTEXITCODE -ne 0) { throw 'Modernize cloud template validation failed.' }
if ($Deploy) {
    $output=& $guard -AzArguments (@('deployment','group','create')+$common+@('--query','properties.outputs'))
    if ($LASTEXITCODE -ne 0) { throw 'Modernize deployment failed; inspect before retrying.' }
    [System.IO.File]::WriteAllText((Join-Path $B 'evidence\modernize\cloud-deployment-outputs.json'),($output -join "`n"))
    $output
}
