[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('probe','seed-hr','plan','ledger','init-budget','approve','ingest','authorize-budget','second-pass-admin','advisory-prepare','advisory-plan','advisory-approve')][string]$Action,
    [string]$MPlanId,
    [string]$PlanId,
    [ValidateSet('true','false')][string]$Approved = 'false'
)
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$command = "/app/.venv/bin/python /eval/macae_cloud_test.py $Action"
if ($Action -eq 'ingest') { $command = '/app/.venv/bin/python /eval/macae_cloud_ingest.py' }
if ($Action -eq 'authorize-budget') { $command = '/app/.venv/bin/python /eval/macae_cloud_run.py authorize-22' }
if ($Action -eq 'second-pass-admin') { $command = '/app/.venv/bin/python /eval/macae_second_pass_admin.py' }
if ($Action -like 'advisory-*') { $command = '/app/.venv/bin/python /eval/macae_advisory.py ' + $Action.Substring(9) }
if ($Action -eq 'init-budget') {
    if (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8111 -State Listen -ErrorAction SilentlyContinue) {
        throw 'Stop the local backend before cloud budget migration.'
    }
    $localLedger = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-state\model-budget.sqlite'
    if (Test-Path $localLedger) {
        throw 'Local ledger exists; inspect/export its consumed total and explicitly coordinate migration, never assume zero.'
    }
    $command = 'env MACAE_PREVIOUS_LIVE_CALLS=0 /app/.venv/bin/python /eval/macae_cloud_run.py init-budget'
}
if ($Action -in @('approve','advisory-approve')) {
    if ($MPlanId -notmatch '^[a-zA-Z0-9-]+$' -or $PlanId -notmatch '^[a-zA-Z0-9-]+$') {
        throw 'Explicit observed native plan identifiers required.'
    }
    $command += " --mplan $MPlanId --plan $PlanId --approved $Approved"
}
$output = @(& (Join-Path $b 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec','--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '-g','rg-ptu-macae-demo','-n','ptu-macae','--container','backend','--command',$command
))
if ($Action -eq 'init-budget' -and ($output -match 'MACAE durable ledger initialized once')) {
    $state = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-state'
    [IO.Directory]::CreateDirectory($state) | Out-Null
    [IO.File]::WriteAllText((Join-Path $state 'cloud-budget-active'), 'Use the persistent Cosmos ledger; local inference startup disabled.')
}
foreach ($line in $output) {
    if ($line -match 'MACAE_RESULT (?<payload>\{.*\})') {
        $result = $Matches.payload | ConvertFrom-Json
        if ($result.name -notmatch '^cloud-[a-z-]+$') { throw 'Unexpected evidence label.' }
        [IO.File]::WriteAllText(
            (Join-Path $b ("evidence\macae\"+$result.name+'.json')),
            ($result.data | ConvertTo-Json -Depth 80)
        )
        Write-Output ("Saved " + $result.name)
    } else {
        Write-Output $line
    }
}
