[CmdletBinding()]
param(
    [ValidateSet('all','api','processor','workflow','web')][string]$Service = 'all'
)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path $PSScriptRoot -Parent
$guard = Join-Path $bundle 'Invoke-LabAz.ps1'
$services = if ($Service -eq 'all') { @('api','processor','workflow','web') } else { @($Service) }
$records = @()
function Invoke-StopAz {
    param([string[]]$Arguments)
    $output = & $guard -AzArguments $Arguments
    if ($LASTEXITCODE -ne 0) { throw 'Content stop command failed; zero replicas are not established.' }
    return $output
}
# Redeployment can activate an older image; stopping must only deactivate revisions.
foreach ($selected in $services) {
    $name = "ca-ptu-content-$selected"
    $scope = @('-g','rg-ptu-content-demo','-n',$name,
        '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70')
    $before = @(Invoke-StopAz -Arguments (@('containerapp','revision','list','--all') + $scope + @('-o','json')) | ConvertFrom-Json)
    if ($before.Count -eq 0) { throw "No revisions returned for $name; cannot verify shutdown." }
    foreach ($revision in $before) {
        if (-not $revision.properties.active) { continue }
        Invoke-StopAz -Arguments (@('containerapp','revision','deactivate') + $scope +
            @('--revision',$revision.name,'-o','none')) | Out-Null
    }
    $after = @(Invoke-StopAz -Arguments (@('containerapp','revision','list','--all') + $scope + @('-o','json')) | ConvertFrom-Json)
    if ($after.Count -eq 0) { throw "No post-stop revisions returned for $name." }
    foreach ($revision in $after) {
        if ($revision.properties.active -or $null -eq $revision.properties.replicas -or $revision.properties.replicas -ne 0) {
            throw "Revision $($revision.name) is not confirmed inactive with zero replicas. Recheck without redeploying."
        }
    }
    $records += [ordered]@{
        service = $selected
        replicas = 0
        revisions = @($after | ForEach-Object {
            [ordered]@{name=$_.name; active=$_.properties.active; replicas=$_.properties.replicas; runningState=$_.properties.runningState}
        })
    }
}
$result = [ordered]@{checkedUtc=[DateTime]::UtcNow.ToString('o'); source='All retained revisions, not only latest'; services=$records}
$json = $result | ConvertTo-Json -Depth 8
$json | Set-Content -Encoding utf8 (Join-Path $bundle "evidence\content\cloud-stop-$Service-all-revisions.json")
$json
