[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('chat-api','scenario-api','chat-ui','scenario-ui')][string]$Service,
    [Parameter(Mandatory)][string]$Image,
    [ValidateRange(0,1)][int]$MinimumReplicas = 0
)
$ErrorActionPreference = 'Stop'
if($Image -notmatch '^acrptubundle7d804f70\.azurecr\.io/chatbot/[a-z-]+@sha256:[a-f0-9]{64}$') {
    throw 'Deploy only immutable image digests in the approved chatbot registry namespace.'
}
$bundle = Split-Path $PSScriptRoot -Parent
$desktop = Split-Path (Split-Path $bundle -Parent) -Parent
$repo = Join-Path $desktop 'repo\customer-chatbot-solution-accelerator'
$ingress = Get-Content (Join-Path $bundle 'evidence\preflight\lab-ingress.json') -Raw | ConvertFrom-Json
$template = Join-Path $env:LOCALAPPDATA "ptu-chatbot\chatbot-cloud-$Service.json"
& "$env:USERPROFILE\.azure\bin\bicep.exe" build (Join-Path $repo 'infra\chatbot-cloud.bicep') --outfile $template
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
$raw = & (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
    'deployment','group','create',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--resource-group','accel-chatbot-eval-0911',
    '--name',"ptu-chatbot-$Service",
    '--template-file',$template,
    '--parameters',"service=$Service","image=$Image","minimumReplicas=$MinimumReplicas","clientCidr=$($ingress.clientCidr)",
    '--output','json','--only-show-errors'
)
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
$result = ($raw -join "`n") | ConvertFrom-Json
[pscustomobject]@{service=$Service;state=$result.properties.provisioningState;outputs=$result.properties.outputs}|ConvertTo-Json -Depth 8
