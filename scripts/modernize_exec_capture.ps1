[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('Preflight','Evaluate','Snapshot','Disarm')]
    [string]$Action
)
$ErrorActionPreference='Stop'
$B=Split-Path $PSScriptRoot -Parent
if ($Action -eq 'Evaluate') { & (Join-Path $PSScriptRoot 'Assert-ModernizeBudgetOpen.ps1') }
$commands=@{
    Preflight=@('python /app/control.py preflight','cloud-preflight.json')
    Evaluate=@('python /app/cloud_e2e.py --execute','cloud-e2e.json')
    Snapshot=@('python /app/control.py snapshot','cloud-budget-snapshot.json')
    Disarm=@('python /app/control.py disarm','cloud-disarm.json')
}
if ($Action -eq 'Evaluate' -and (Test-Path (Join-Path $B 'evidence\modernize\cloud-e2e.json'))) {
    throw 'Prior cloud evaluation evidence exists. Inspect it; do not repeat automatically.'
}
$output=& (Join-Path $B 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec','-g','rg-ptu-modernize-demo','-n','ca-ptu-modernize-api',
    '--command',$commands[$Action][0],
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70')
$exit=$LASTEXITCODE
$lines=@($output | Where-Object { $_.Trim().StartsWith('{') })
if (-not $lines.Count) { throw "No structured exec result returned (exit $exit); inspect remote state before retrying." }
$result=$lines[-1] | ConvertFrom-Json
$result | Add-Member -NotePropertyName execProcessExitCode -NotePropertyValue $exit -Force
[System.IO.File]::WriteAllText((Join-Path $B "evidence\modernize\$($commands[$Action][1])"),
    ($result | ConvertTo-Json -Depth 100))
$result | ConvertTo-Json -Depth 100
if ($exit -ne 0) { throw "Authenticated exec returned $exit; evidence preserved." }
