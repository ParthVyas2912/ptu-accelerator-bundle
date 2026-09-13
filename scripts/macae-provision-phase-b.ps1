[CmdletBinding()]
param([ValidateSet('Search','Storage')][string]$Step)
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$contract = Get-Content (Join-Path $b 'deployment-contract.json') -Raw | ConvertFrom-Json
if (-not $contract.approvedExceptions.macae) { throw 'MACAE approval missing.' }
$repo = Join-Path $contract.repoRoot 'Multi-Agent-Custom-Automation-Engine-Solution-Accelerator'
$template = if ($Step -eq 'Search') { 'infra\bicep\modules\ai\ai-search.bicep' } else { 'infra\bicep\modules\data\storage-account.bicep' }
$parameters = Join-Path $PSScriptRoot ("macae-"+$Step.ToLower()+".parameters.json")
Write-Output 'Approved fixed baseline before creation: Search Basic East US 2 USD 0.101/hour (retail API verified); Blob Storage and Cosmos are metered. No paid upgrade authorized.'
& (Join-Path $b 'Invoke-LabAz.ps1') -AzArguments @('deployment','group','create','--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70','--resource-group','rg-ptu-macae-demo','--name',("ptu-macae-"+$Step.ToLower()),'--template-file',(Join-Path $repo $template),'--parameters',('@'+$parameters),'--query','{state:properties.provisioningState,outputs:properties.outputs}','-o','json')
