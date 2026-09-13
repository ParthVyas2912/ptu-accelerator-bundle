[CmdletBinding()]
param(
    [ValidateSet('Status','Start','Idle','Pause')]
    [string]$Action = 'Status',
    [switch]$WarmForExec,
    [string]$ApiImage
)
$ErrorActionPreference = 'Stop'
if ($WarmForExec -and $Action -ne 'Start') {
    throw '-WarmForExec is only valid with -Action Start.'
}
if ($ApiImage -and (-not $WarmForExec -or $ApiImage -notmatch '^acrptubundle7d804f70\.azurecr\.io/conversation/api@sha256:[0-9a-f]{64}$')) {
    throw 'ApiImage requires WarmForExec and an immutable digest in the approved own API repository.'
}
$bundle = Split-Path -Parent $PSScriptRoot
$guard = Join-Path $bundle 'Invoke-LabAz.ps1'
$sub = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$rg = 'rg-ptu-conversation-demo'
$cidr = (Get-Content (Join-Path $bundle 'evidence\preflight\lab-ingress.json') -Raw |
    ConvertFrom-Json).clientCidr
$names = @('ca-ptu-conversation-api','ca-ptu-conversation-ui')
$guardedServingImage = 'acrptubundle7d804f70.azurecr.io/conversation/api@sha256:84ff9d2a31ddf2e71a75d26ca58433ce29e41af0eb46823c0a0c5d5ca4bbcaf0'
$durableServingConfigured = Test-Path -LiteralPath (Join-Path $bundle 'evidence\conversation\serving-configure-attempt-1.json')
if ($durableServingConfigured -and $ApiImage -and $ApiImage -ne $guardedServingImage) {
    throw 'Durable model binding exists: refusing any image except the offline-verified hard-disarmed serving image.'
}

function Suspend-ComponentRevisions([string[]]$CommonArgs) {
    $active = @(& $guard -AzArguments (@('containerapp','revision','list') + $CommonArgs +
        @('--all','--query','[?properties.active].name','-o','tsv')))
    foreach ($revision in $active) {
        if ($revision.Trim()) {
            & $guard -AzArguments (@('containerapp','revision','deactivate') + $CommonArgs +
                @('--revision',$revision.Trim(),'-o','none'))
        }
    }
    # This confirms shutdown, but does not prevent Azure rollout overlap on later template updates.
    for ($attempt = 0; $attempt -lt 6; $attempt++) {
        $remaining = @(& $guard -AzArguments (@('containerapp','revision','list') + $CommonArgs +
            @('--all','--query','[?properties.replicas > `0`].name','-o','tsv')) |
            Where-Object { $_.Trim() })
        if ($remaining.Count -eq 0) { return }
        Start-Sleep -Seconds 5
    }
    throw 'Replicas have not reached zero; no replacement revision will be started.'
}

foreach ($name in $names) {
    if ($WarmForExec -and $name.EndsWith('-ui')) { continue }
    $common = @('--name',$name,'--resource-group',$rg,'--subscription',$sub)
    $app = & $guard -AzArguments (@('containerapp','show') + $common +
        @('--query','{name:name,id:id,tags:tags,ingress:properties.configuration.ingress,scale:properties.template.scale,latestReady:properties.latestReadyRevisionName,state:properties.provisioningState,image:properties.template.containers[0].image}',
          '-o','json')) | ConvertFrom-Json

    if ($Action -eq 'Start') {
        if ($durableServingConfigured -and $name.EndsWith('-api') -and $app.image -ne $guardedServingImage) {
            throw 'Refusing to start an unguarded image with durable data/model configuration.'
        }
        if ($app.tags.phase -ne 'component-only') {
            throw 'This runbook is for the verified component phase. Review live budget/auth controls before starting a later phase.'
        }
        if ($app.scale.maxReplicas -ne 1 -or $app.scale.minReplicas -ne 0) {
            throw 'Unexpected scaling: review before activating any revision.'
        }
        if ($name.EndsWith('-api') -and $app.ingress.external) {
            throw 'Refusing to activate publicly exposed API.'
        }
        if ($name.EndsWith('-ui')) {
            $rules = @($app.ingress.ipSecurityRestrictions)
            if (-not $app.ingress.external -or $rules.Count -ne 1 -or
                $rules[0].action -ne 'Allow' -or $rules[0].ipAddressRange -ne $cidr) {
                throw 'UI ingress does not match the approved single-client restriction.'
            }
        }
        if (-not $app.latestReady) { throw 'No previously ready revision to activate.' }
        Suspend-ComponentRevisions $common
        if ($WarmForExec) {
            & $guard -AzArguments (@('containerapp','revision','set-mode') + $common +
                @('--mode','multiple','-o','none'))
            $updateArgs = @('containerapp','update') + $common +
                @('--min-replicas','1','--max-replicas','1','--scale-rule-name','http',
                  '--scale-rule-http-concurrency','5','-o','none')
            if ($ApiImage) { $updateArgs += @('--image',$ApiImage) }
            & $guard -AzArguments $updateArgs
        } else {
            & $guard -AzArguments (@('containerapp','revision','activate') + $common +
                @('--revision',$app.latestReady,'-o','none'))
        }
    } elseif ($Action -eq 'Pause') {
        Suspend-ComponentRevisions $common
    } elseif ($Action -eq 'Idle') {
        if ($app.scale.maxReplicas -ne 1) { throw 'Unexpected replica ceiling.' }
        if ($app.scale.minReplicas -ne 0) {
            Suspend-ComponentRevisions $common
            & $guard -AzArguments (@('containerapp','revision','set-mode') + $common +
                @('--mode','multiple','-o','none'))
            & $guard -AzArguments (@('containerapp','update') + $common +
                @('--min-replicas','0','--max-replicas','1','--scale-rule-name','http',
                  '--scale-rule-http-concurrency','5','-o','none'))
        }
    }

    $after = @(& $guard -AzArguments (@('containerapp','revision','list') + $common +
        @('--all','--query','[].{active:properties.active,replicas:properties.replicas}','-o','json')) | ConvertFrom-Json)
    if (@($after | Where-Object active).Count -gt 1 -or ($after | Measure-Object replicas -Sum).Sum -gt 1) {
        Suspend-ComponentRevisions $common
        throw 'Reported revision/replica ceiling exceeded; all owned service revisions stopped.'
    }
    & $guard -AzArguments (@('containerapp','show') + $common +
        @('--query','{name:name,state:properties.provisioningState,external:properties.configuration.ingress.external,restrictions:properties.configuration.ingress.ipSecurityRestrictions,scale:properties.template.scale,latestReady:properties.latestReadyRevisionName}',
          '-o','json'))
    & $guard -AzArguments (@('containerapp','revision','list') + $common +
        @('--all','--query','[].{name:name,active:properties.active,replicas:properties.replicas,health:properties.healthState}',
          '-o','json'))
}
# Multiple revision bookkeeping prevents Single-mode reactivation; only one revision may be active.
# Pause deactivates revisions without deleting resources; wait for replicas=0.
# Registry/platform charges and any future PaaS charges do not stop with revisions.
