[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateSet('backend','worker','frontend','database','storage')]
    [string]$Service
)
$ErrorActionPreference='Stop'
if ($Service -eq 'database') {
    if ($PSCmdlet.ShouldProcess('ptu-cwyd-postgres', 'Stop container and preserve data')) {
        docker stop ptu-cwyd-postgres
        if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL stop failed.' }
    }
    return
}
if ($Service -eq 'storage') {
    if ($PSCmdlet.ShouldProcess('ptu-cwyd-azurite', 'Stop container and preserve data')) {
        docker stop ptu-cwyd-azurite
        if ($LASTEXITCODE -ne 0) { throw 'Azurite stop failed.' }
    }
    return
}
if ($Service -eq 'frontend') {
    $listener=Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 5112 -State Listen -ErrorAction SilentlyContinue
    if (-not $listener) { Write-Host 'CWYD frontend is not listening.'; return }
    $ProcessIdToStop=[int]($listener | Select-Object -First 1).OwningProcess
} else {
    $PidFile=Join-Path $env:LOCALAPPDATA "ptu-eval\cwyd\$Service.pid"
    if (-not (Test-Path -LiteralPath $PidFile)) { throw "No CWYD PID file for $Service. Inspect current process before stopping." }
    $ProcessIdToStop=[int](Get-Content -LiteralPath $PidFile -Raw)
}
$ProcessInfo=Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessIdToStop"
if (-not $ProcessInfo) { Write-Host "CWYD $Service is already stopped."; return }
$CommandLine=$ProcessInfo.CommandLine
if ($Service -eq 'frontend') {
    if ($CommandLine -notmatch 'createServer' -or $CommandLine -notmatch '5112') {
        throw 'Refusing to stop an unrecognized process on the CWYD frontend port.'
    }
} elseif ($CommandLine -notmatch 'cwyd_runtime\.py' -or $CommandLine -notmatch "\b$Service\b") {
    throw "Refusing to stop an unrecognized process from the $Service PID file."
}
if ($PSCmdlet.ShouldProcess("CWYD $Service PID $ProcessIdToStop", 'Stop verified process')) {
    Stop-Process -Id $ProcessIdToStop
    Write-Host "Stopped CWYD $Service PID $ProcessIdToStop. No Azure resources or local data were deleted."
}
