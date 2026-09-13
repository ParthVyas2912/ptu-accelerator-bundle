[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('Pause','Resume','Status')][string]$Action)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$guard = Join-Path $root 'Invoke-LabAz.ps1'
$subscription = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$group = 'accel-dkm-20260911'
$names = if ($Action -eq 'Resume') {
    @('ca-dkm-kernel','ca-dkm-api','ca-dkm-web')
} else {
    @('ca-dkm-web','ca-dkm-api','ca-dkm-kernel')
}
foreach ($name in $names) {
    $common = @('--name',$name,'--resource-group',$group,'--subscription',$subscription)
    if ($Action -eq 'Pause') {
        $active = @(& $guard -AzArguments (@('containerapp','revision','list') + $common +
            @('--query','[?properties.active].name','-o','tsv')))
        foreach ($revision in $active) {
            if (-not [string]::IsNullOrWhiteSpace($revision)) {
                & $guard -AzArguments (@('containerapp','revision','deactivate') + $common +
                    @('--revision',$revision.Trim(),'-o','none'))
            }
        }
    } elseif ($Action -eq 'Resume') {
        $revision = (& $guard -AzArguments (@('containerapp','show') + $common +
            @('--query','properties.latestReadyRevisionName','-o','tsv'))) -join ''
        if ([string]::IsNullOrWhiteSpace($revision)) { throw "No ready revision for $name" }
        $isActive = (& $guard -AzArguments (@('containerapp','revision','show') + $common +
            @('--revision',$revision.Trim(),'--query','properties.active','-o','tsv'))) -join ''
        if ($isActive.Trim() -ne 'true') {
            & $guard -AzArguments (@('containerapp','revision','activate') + $common +
                @('--revision',$revision.Trim(),'-o','none'))
        }
    }
    Write-Output "APP:$name"
    & $guard -AzArguments (@('containerapp','revision','list','--all') + $common +
        @('--query','[].{name:name,active:properties.active,replicas:properties.replicas,health:properties.healthState}','-o','json'))
}
