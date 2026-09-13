[CmdletBinding()]
param([ValidateSet('Group','Foundry','Cosmos','Models')][string]$Step)
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$contract = Get-Content (Join-Path $b 'deployment-contract.json') -Raw | ConvertFrom-Json
if (-not $contract.approvedExceptions.macae) { throw 'MACAE approval missing.' }
$sub = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$rg = 'rg-ptu-macae-demo'
$repo = Join-Path $contract.repoRoot 'Multi-Agent-Custom-Automation-Engine-Solution-Accelerator'
$guard = Join-Path $b 'Invoke-LabAz.ps1'
$tags = '{"workload":"accelerator-eval","owner":"parth","environment":"mcaps-nonprod","accelerator":"macae","protected":"false"}'
switch ($Step) {
  'Group' {
    & $guard -AzArguments @('group','create','--subscription',$sub,'--name',$rg,'--location','eastus2','--tags','workload=accelerator-eval','owner=parth','environment=mcaps-nonprod','accelerator=macae','protected=false','--query','{id:id,location:location,tags:tags}','-o','json')
  }
  'Foundry' {
    & $guard -AzArguments @('deployment','group','create','--subscription',$sub,'--resource-group',$rg,'--name','ptu-macae-foundry','--template-file',(Join-Path $repo 'infra\bicep\modules\ai\ai-foundry-project.bicep'),'--parameters',('@'+(Join-Path $PSScriptRoot 'macae-foundry.parameters.json')),'--query','{state:properties.provisioningState,outputs:properties.outputs}','-o','json')
  }
  'Cosmos' {
    & $guard -AzArguments @('deployment','group','create','--subscription',$sub,'--resource-group',$rg,'--name','ptu-macae-cosmos','--template-file',(Join-Path $repo 'infra\bicep\modules\data\cosmos-db-nosql.bicep'),'--parameters',('@'+(Join-Path $PSScriptRoot 'macae-cosmos.parameters.json')),'--query','{state:properties.provisioningState,outputs:properties.outputs}','-o','json')
  }
  'Models' {
    foreach ($m in @(@{name='gpt-5.4';version='2026-03-05'},@{name='gpt-5.4-mini';version='2026-03-17'})) {
      & $guard -AzArguments @('cognitiveservices','account','deployment','create','--subscription',$sub,'--resource-group',$rg,'--name','ptumacae7d804f70','--deployment-name',$m.name,'--model-format','OpenAI','--model-name',$m.name,'--model-version',$m.version,'--sku-name','GlobalStandard','--sku-capacity','10','--query','{id:id,model:properties.model,sku:sku,state:properties.provisioningState}','-o','json')
    }
  }
}
