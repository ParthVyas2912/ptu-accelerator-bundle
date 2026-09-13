[CmdletBinding()]
param(
    [Parameter(Mandatory)][int[]]$ProcessId,
    [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'
$repo = 'customer-chatbot-solution-accelerator'
$runtime = Join-Path $env:LOCALAPPDATA 'ptu-chatbot'
foreach ($id in $ProcessId) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $id"
    if (-not $process) {
        Write-Output "PID $id is already stopped."
        continue
    }
    $command = [string]$process.CommandLine
    if (-not ($command.Contains($runtime) -or $command.Contains($repo) -or $command.Contains('chatbot_runtime\local_app.py'))) {
        throw "Refusing PID ${id}: command does not identify the isolated Chatbot runtime."
    }
    if ($WhatIf) {
        Write-Output "Would stop verified Chatbot PID $id ($($process.Name))."
    } else {
        Stop-Process -Id $id -ErrorAction Stop
        Write-Output "Stopped Chatbot PID $id."
    }
}
# Stops only supplied, verified PIDs. Never stops cloud resources or other apps.
