[CmdletBinding()]
param(
    [ValidateSet('api','processor','workflow','web','all')]
    [string]$Service = 'api',
    [switch]$WarmForTest,
    [switch]$PauseWorkers
)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path $PSScriptRoot -Parent
$statePath = Join-Path $bundle 'evidence\content\result.json'
if ((Test-Path $statePath) -and (Get-Content -Raw -Encoding utf8 $statePath | ConvertFrom-Json).modelCallsOnHold) {
    throw 'Content deployment is on inference hold. A rollout can activate an older armed revision. Resolve the ledger/scope incident with the coordinator before any deployment; Stop-ContentCloud.ps1 remains available.'
}
$root = Join-Path $env:LOCALAPPDATA 'ptu-content-eval'
$services = if ($Service -eq 'all') { @('api','processor','workflow','web') } else { @($Service) }
$parameters = @{parameters=@{
    services=@{value=@($services)}
    warmForTest=@{value=[bool]$WarmForTest}
    pauseWorkers=@{value=[bool]$PauseWorkers}
}}
$path = Join-Path $root ("content-app-parameters-" + [guid]::NewGuid().ToString() + '.json')
[IO.File]::WriteAllText($path, ($parameters | ConvertTo-Json -Depth 6))
& "$env:USERPROFILE\.azure\bin\bicep.exe" build (Join-Path $PSScriptRoot 'content-cloud-apps.bicep') --outfile (Join-Path $root 'content-cloud-apps.json')
if ($LASTEXITCODE -ne 0) { throw 'Content cloud template compile failed.' }
& (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
    'deployment','group','create','--resource-group','rg-ptu-content-demo',
    '--name',"ptu-content-app-$Service",
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--template-file',(Join-Path $root 'content-cloud-apps.json'),
    '--parameters',"@$path",'--query','properties.outputs','-o','json'
)
# ARM success is not an E2E result. Use baked probes and real exercise_app via exec.
