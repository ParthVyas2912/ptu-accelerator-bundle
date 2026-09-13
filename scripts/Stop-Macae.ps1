[CmdletBinding()]
param([ValidateSet('backend','mcp','all')][string]$Component = 'all')
$ErrorActionPreference = 'Stop'
$state = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-state'
$components = if ($Component -eq 'all') { @('backend','mcp') } else { @($Component) }
foreach ($service in $components) {
    $file = Join-Path $state "$service.pid"
    if (-not (Test-Path $file)) { continue }
    $processId = [int](Get-Content $file -Raw)
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$processId"
    if (-not $process) { continue }
    if ($process.CommandLine -notmatch 'macae_run\.py' -or $process.CommandLine -notmatch $service) {
        throw "PID $processId no longer identifies the expected MACAE process; refusing to stop it."
    }
    Stop-Process -Id $processId
    Write-Output "Stopped MACAE $service PID $processId"
}
# No Azure resources, agents, data or model deployments are deleted.
