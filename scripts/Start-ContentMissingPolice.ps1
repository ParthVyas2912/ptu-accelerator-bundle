[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('api','processor','workflow')][string]$Service)
$ErrorActionPreference='Stop'
$bundle=Split-Path $PSScriptRoot -Parent
$guard=Join-Path $bundle 'Invoke-LabAz.ps1'
$subscription='1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$contract=Get-Content -Raw (Join-Path $bundle 'deployment-contract.json') | ConvertFrom-Json
if($contract.modelAttemptBudget.contentApprovedTotal -ne 17){throw 'Exact cap17 approval required'}
$evaluation=Get-Content -Raw -Encoding utf8 (Join-Path $bundle 'evidence\content\result.json') | ConvertFrom-Json
if($evaluation.measuredTraffic.sdkReservedModelAttempts -ge 17){throw 'Content cap17 exhausted; no further activation authorized'}
$legacyPath=Join-Path $bundle 'evidence\content\isolated-legacy-revisions.json'
if(-not (Test-Path $legacyPath)){
    $initial=Get-Content -Raw (Join-Path $bundle 'evidence\content\cloud-stop-all-all-revisions.json') | ConvertFrom-Json
    if(@($initial.services).Count -ne 4){throw 'All-service shutdown evidence required'}
    $initial | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 $legacyPath
}
$legacy=Get-Content -Raw $legacyPath | ConvertFrom-Json
function Confirm-LegacyStopped {
    foreach($entry in $legacy.services){
        $rows=@(& $guard -AzArguments @('containerapp','revision','list','--all','-g','rg-ptu-content-demo',
            '-n',("ca-ptu-content-"+$entry.service),'--subscription',$subscription,'-o','json') | ConvertFrom-Json)
        foreach($old in $entry.revisions){
            $found=@($rows | Where-Object name -eq $old.name)
            if($found.Count -ne 1 -or $found[0].properties.active -or $found[0].properties.replicas -ne 0){
                throw "Legacy revision not preserved inactive/zero: $($old.name)"
            }
        }
        if(@($rows | Where-Object {$_.properties.active}).Count -gt 1){throw 'Multiple active revisions for one service'}
        foreach($active in @($rows | Where-Object {$_.properties.active})){
            if($active.properties.template.containers[0].image -notmatch ':659eaa1-scope-r[12]$'){
                throw "Unscoped active revision: $($active.name)"
            }
        }
    }
}
Confirm-LegacyStopped
$name="ca-ptu-content-$Service"
& $guard -AzArguments @('containerapp','revision','set-mode','-g','rg-ptu-content-demo','-n',$name,
    '--mode','multiple','--subscription',$subscription,'-o','none')
Confirm-LegacyStopped
$root=Join-Path $env:LOCALAPPDATA 'ptu-content-eval'
$template=Join-Path $root 'content-isolated-apps.json'
$parameters=Join-Path $root "content-isolated-$Service.parameters.json"
@{parameters=@{services=@{value=@($Service)};warmForTest=@{value=$true};pauseWorkers=@{value=$true}}} |
    ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 $parameters
& "$env:USERPROFILE\.azure\bin\bicep.exe" build (Join-Path $PSScriptRoot 'content-cloud-apps.bicep') --outfile $template
if($LASTEXITCODE -ne 0){throw 'Bicep compile failed'}
& $guard -AzArguments @('deployment','group','create','-g','rg-ptu-content-demo',
    '--name',"content-isolated-$Service",'--subscription',$subscription,'--template-file',$template,
    '--parameters',"@$parameters",'-o','none')
Confirm-LegacyStopped
$app=& $guard -AzArguments @('containerapp','show','-g','rg-ptu-content-demo','-n',$name,
    '--subscription',$subscription,'--query','{name:name,mode:properties.configuration.activeRevisionsMode,revision:properties.latestRevisionName,ready:properties.latestReadyRevisionName,image:properties.template.containers[0].image,scale:properties.template.scale}','-o','json') | ConvertFrom-Json
if($app.mode -ne 'Multiple' -or $app.image -notmatch ':659eaa1-scope-r[12]$' -or $app.scale.maxReplicas -ne 1){
    throw 'Scoped deployment invariant failed; stop all services'
}
$app | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 (Join-Path $bundle "evidence\content\isolated-$Service-deployment.json")
$app | ConvertTo-Json -Depth 8
