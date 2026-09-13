[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$guard = Join-Path $b 'Invoke-LabAz.ps1'
$sub = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$query = '{state:properties.provisioningState,revision:properties.latestReadyRevisionName,scale:properties.template.scale,ingress:properties.configuration.ingress,containers:properties.template.containers[].{name:name,image:image,resources:resources,gate:env[?name==`MACAE_LIVE_REQUESTS_ENABLED`].value}}'
$raw = & $guard -AzArguments @('containerapp','show','--subscription',$sub,'-g','rg-ptu-macae-demo','-n','ptu-macae','--query',$query,'-o','json')
if ($LASTEXITCODE -ne 0) { throw 'Cannot read MACAE cloud state.' }
$state = ($raw | Out-String) | ConvertFrom-Json
$raw = & $guard -AzArguments @('containerapp','replica','list','--subscription',$sub,'-g','rg-ptu-macae-demo','-n','ptu-macae','--query','[].{name:name,state:properties.runningState}','-o','json')
if ($LASTEXITCODE -ne 0) { throw 'Cannot read MACAE replicas.' }
$replicas = @(($raw | Out-String) | ConvertFrom-Json)
$listeners = @(Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8111,5111 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess)
$evidence = [ordered]@{
    observedAtUtc = [DateTime]::UtcNow.ToString('o')
    app = $state
    replicas = $replicas
    replicaCount = $replicas.Count
    localListeners = $listeners
    modelRequestsMadeByThisCheck = 0
}
$json = $evidence | ConvertTo-Json -Depth 20
[IO.File]::WriteAllText((Join-Path $b 'evidence\macae\cloud-final-state.json'), $json)
Write-Output $json
