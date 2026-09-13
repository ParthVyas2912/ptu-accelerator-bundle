[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:LOCALAPPDATA 'ptu-content-eval'
$state = Get-Content (Join-Path $root 'native-state.json') -Raw | ConvertFrom-Json
$process = Get-Process -Id $state.supervisorPid -ErrorAction SilentlyContinue
if (-not $process) { 'Content supervisor is already stopped.'; return }
$created = ([DateTimeOffset]$process.StartTime.ToUniversalTime()).ToUnixTimeMilliseconds() / 1000
if ([Math]::Abs($created - $state.supervisorCreated) -gt 2) { throw 'PID reused; refusing to stop.' }
$request = @{supervisorPid=$state.supervisorPid; requested=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()}
[IO.File]::WriteAllText((Join-Path $root 'native-stop.json'), ($request | ConvertTo-Json))
'Stop requested for the verified Content supervisor and its owned descendants.'
