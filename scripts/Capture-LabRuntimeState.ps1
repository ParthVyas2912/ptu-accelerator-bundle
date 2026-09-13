[CmdletBinding()]
param(
    [string[]]$Names = @(
        'ca-ptu-networkcheck', 'ptu-macae',
        'ca-ptu-modernize-api', 'ca-ptu-modernize-ui',
        'ca-ptu-content-api', 'ca-ptu-content-web',
        'ca-ptu-content-processor', 'ca-ptu-content-workflow',
        'chatbot-chat-api', 'chatbot-scenario-api',
        'chatbot-chat-ui', 'chatbot-scenario-ui',
        'ca-dkm-api', 'ca-dkm-web', 'ca-dkm-kernel',
        'ca-ptu-conversation-api', 'ca-ptu-conversation-ui'
    )
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$contract = Get-Content -LiteralPath (Join-Path $root 'deployment-contract.json') -Raw | ConvertFrom-Json
$delta = Get-Content -LiteralPath (Join-Path $root 'evidence\azure-resource-delta.json') -Raw | ConvertFrom-Json
$guard = Join-Path $root 'Invoke-LabAz.ps1'
$startedAt = [datetime]::UtcNow.ToString('o')

function Get-LabAzJson {
    param([string[]]$Arguments)
    $cliArguments = $Arguments + @('--subscription', $contract.subscriptionId, '--only-show-errors', '-o', 'json')
    $raw = & $guard -AzArguments $cliArguments
    $raw | ConvertFrom-Json
}

$apps = @(foreach ($name in $Names) {
    $matches = @($delta.newResourcesSinceBaseline | Where-Object {
        $_.type -eq 'Microsoft.App/containerApps' -and $_.name -eq $name
    })
    if ($matches.Count -ne 1) { throw "Expected exactly one new lab application named $name; refresh the resource delta." }
    $resource = $matches[0]
    $common = @('--name', $resource.name, '--resource-group', $resource.resourceGroup)
    $app = Get-LabAzJson -Arguments (@('containerapp', 'show') + $common + @(
        '--query', '{name:name,location:location,environmentId:properties.environmentId,fqdn:properties.configuration.ingress.fqdn,externalIngress:properties.configuration.ingress.external,minReplicas:properties.template.scale.minReplicas,maxReplicas:properties.template.scale.maxReplicas,containers:properties.template.containers[].{name:name,resources:resources}}'
    ))
    $revisions = @(Get-LabAzJson -Arguments (@('containerapp', 'revision', 'list') + $common + @(
        '--query', '[].{name:name,active:properties.active,runningState:properties.runningState}'
    )) | Where-Object { $null -ne $_ })
    $revisionStates = @(foreach ($revision in $revisions) {
        $replicas = @(Get-LabAzJson -Arguments (@('containerapp', 'replica', 'list') + $common + @(
            '--revision', $revision.name, '--query', '[].name'
        )) | Where-Object { $null -ne $_ })
        [ordered]@{
            revision = $revision.name
            active = $revision.active
            runningState = $revision.runningState
            replicaCount = $replicas.Count
        }
    })
    $replicaCount = 0
    foreach ($revision in $revisionStates) { $replicaCount += $revision.replicaCount }
    [pscustomobject]@{
        name = $name
        resourceGroup = $resource.resourceGroup
        observedAtUtc = [datetime]::UtcNow.ToString('o')
        configuration = $app
        revisions = $revisionStates
        totalReplicas = $replicaCount
    }
})
$snapshot = [ordered]@{
    startedAtUtc = $startedAt
    completedAtUtc = [datetime]::UtcNow.ToString('o')
    subscriptionId = $contract.subscriptionId
    apps = $apps
    interpretation = 'Read-only actual replica lists for explicitly selected new lab apps. This is a point-in-time observation, not a guarantee against future autoscaling or a claim of zero retained-service charges.'
}
$snapshot | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $root 'evidence\runtime-state.json') -Encoding utf8
$apps | Select-Object name, resourceGroup, totalReplicas, observedAtUtc | Format-Table -AutoSize
