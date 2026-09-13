[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
# Run in an attached async tool session. No secrets, .env files or detached processes.
$python = Join-Path $env:LOCALAPPDATA 'ptu-content-eval\api\Scripts\python.exe'
& $python (Join-Path $PSScriptRoot 'content-runtime\native_supervisor.py')
if ($LASTEXITCODE -ne 0) { throw "Native Content supervisor stopped with exit $LASTEXITCODE." }
