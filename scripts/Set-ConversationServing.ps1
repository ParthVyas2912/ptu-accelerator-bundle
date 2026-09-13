[CmdletBinding()]
param([ValidateRange(1,2)][int]$Attempt = 1)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path -Parent $PSScriptRoot
$guard = Join-Path $bundle 'Invoke-LabAz.ps1'
$folder = Join-Path $bundle 'evidence\conversation'
$receipt = Join-Path $folder "serving-configure-attempt-$Attempt.json"
if (Test-Path -LiteralPath $receipt) { throw 'This configure attempt already has a receipt. Do not repeat it.' }
$budget = Get-Content (Join-Path $folder 'budget-handoff.json') -Raw | ConvertFrom-Json
if ($budget.current_model_request_cap -ne 9 -or $budget.actual_model_attempts_used -ne 9 -or
    $budget.remaining_ckm_model_request_allowance -ne 0) { throw 'Expected closed9/9 model budget.' }
$common = @('--name','ca-ptu-conversation-api','--resource-group','rg-ptu-conversation-demo',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70')
$image = 'acrptubundle7d804f70.azurecr.io/conversation/api@sha256:84ff9d2a31ddf2e71a75d26ca58433ce29e41af0eb46823c0a0c5d5ca4bbcaf0'
$before = & $guard -AzArguments (@('containerapp','show') + $common +
    @('--query','{external:properties.configuration.ingress.external,mode:properties.configuration.activeRevisionsMode,scale:properties.template.scale}','-o','json')) | ConvertFrom-Json
if ($before.external -or $before.mode -ne 'Multiple' -or $before.scale.maxReplicas -ne 1) {
    throw 'Unexpected API exposure/revision/scaling settings; refusing configuration.'
}
$revisions = @(& $guard -AzArguments (@('containerapp','revision','list') + $common +
    @('--all','--query','[].{active:properties.active,replicas:properties.replicas}','-o','json')) | ConvertFrom-Json)
if (@($revisions | Where-Object { $_.active -or $_.replicas -gt 0 }).Count) { throw 'Pause all old API revisions first.' }
$config = Get-Content (Join-Path $folder 'serving-native-config.json') -Raw | ConvertFrom-Json
$entries = @($config.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" })
$state = [ordered]@{attempt=$Attempt; startedAt=[DateTimeOffset]::UtcNow.ToString('o'); status='configuring';
    image=$image; nonsecretNativeConfiguration=$config; modelRequests=0; originalCapClosed=9}
$state | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $receipt -Encoding utf8
try {
    & $guard -AzArguments (@('containerapp','update') + $common +
        @('--image',$image,'--min-replicas','1','--max-replicas','1',
          '--revision-suffix',"serving-ro$Attempt",'--set-env-vars') + $entries + @('-o','none'))
    $state.status = 'configured'
} catch {
    $state.status = 'failed'
    $state.error = $_.Exception.Message
    throw
} finally {
    $state.finishedAt = [DateTimeOffset]::UtcNow.ToString('o')
    $state | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $receipt -Encoding utf8
}
$after = @(& $guard -AzArguments (@('containerapp','revision','list') + $common +
    @('--all','--query','[].{name:name,active:properties.active,replicas:properties.replicas,health:properties.healthState}','-o','json')) | ConvertFrom-Json)
if (@($after | Where-Object active).Count -gt 1 -or ($after | Measure-Object replicas -Sum).Sum -gt 1) {
    & (Join-Path $PSScriptRoot 'Manage-ConversationCloud.ps1') -Action Pause
    throw 'Unexpected rollout overlap; paused owned apps.'
}
$after | Where-Object active | ConvertTo-Json
