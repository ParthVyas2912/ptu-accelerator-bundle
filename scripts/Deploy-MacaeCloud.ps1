[CmdletBinding()]
param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$p = Get-Content (Join-Path $PSScriptRoot 'macae-cloud.parameters.json') -Raw | ConvertFrom-Json
$platform = Get-Content (Join-Path $b 'evidence\preflight\lab-platform-outputs.json') -Raw | ConvertFrom-Json
$ingress = Get-Content (Join-Path $b 'evidence\preflight\lab-ingress.json') -Raw | ConvertFrom-Json
if ($p.parameters.managedEnvironmentId.value -ne $platform.environmentId.value -or
    $p.parameters.registryServer.value -ne $platform.registryLoginServer.value -or
    $p.parameters.clientCidr.value -ne $ingress.clientCidr -or
    $p.parameters.clientCidr.value -notmatch '^\d+\.\d+\.\d+\.\d+/32$' -or
    $p.parameters.runtimeIdentityResourceId.value -notlike '*/resourceGroups/rg-ptu-macae-demo/providers/Microsoft.ManagedIdentity/userAssignedIdentities/*') {
    throw 'Parent platform, identity scope or single-client ingress mismatch.'
}
Write-Output ("MACAE: max1 replica, 1vCPU/2GiB total. Fully active ACA reference USD0.108/hour plus requests; Search USD0.101/hour separately. Other platform/data costs separate. Live inference flag="+$p.parameters.liveRequestsEnabled.value+"; minReplicas="+$p.parameters.minReplicas.value)
$action = if ($ValidateOnly) { 'validate' } else { 'create' }
& (Join-Path $b 'Invoke-LabAz.ps1') -AzArguments @(
    'deployment','group',$action,'--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--resource-group','rg-ptu-macae-demo','--name','ptu-macae-cloud',
    '--template-file',(Join-Path $PSScriptRoot 'macae-shared-aca.bicep'),
    '--parameters',('@'+(Join-Path $PSScriptRoot 'macae-cloud.parameters.json')),
    '--query','{state:properties.provisioningState,outputs:properties.outputs,error:error}','-o','json'
)
