[CmdletBinding()]
param([switch]$Retry)
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$repo = 'C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\Multi-Agent-Custom-Automation-Engine-Solution-Accelerator'
$context = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-serialization-remote-22'
$manifestFile = Join-Path $b 'evidence\macae\remote-build-context.json'
$retryMarker = Join-Path $b 'evidence\macae\remote-build-retry-used'
if ($Retry) {
    if (Test-Path $retryMarker) { throw 'The one permitted corrected retry has already been used.' }
    $prior = Get-Content $manifestFile -Raw | ConvertFrom-Json
    $entries = @(Get-ChildItem -LiteralPath $context -Force)
    if ($entries.Count -ne 6 -or ($entries | Where-Object PSIsContainer)) { throw 'Unexpected retry context contents.' }
    foreach ($entry in $entries) {
        $expected = $prior | Where-Object name -EQ $entry.Name
        if (-not $expected -or (Get-FileHash $entry.FullName).Hash.ToLowerInvariant() -ne $expected.sha256) {
            throw 'Retry context differs from the recorded clean-source manifest.'
        }
    }
    [IO.File]::WriteAllText($retryMarker, [DateTime]::UtcNow.ToString('o'))
} else {
    if (Test-Path $context) { throw 'Use the explicit bounded retry; do not silently reuse an existing context.' }
    [IO.Directory]::CreateDirectory($context) | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo 'src\backend\orchestration\connection_config.py') -Destination $context
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'macae-serialization-patch.Dockerfile') -Destination (Join-Path $context 'Dockerfile')
    foreach ($name in @('macae_model_guard.py','macae_cosmos_budget.py','macae_cloud_run.py','macae_second_pass_admin.py')) {
        Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination $context
    }
}
$manifest = @(Get-ChildItem -LiteralPath $context -File | ForEach-Object {
    [ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
})
if ($manifest.Count -ne 6) { throw 'Unexpected clean build context; refuse upload.' }
[IO.File]::WriteAllText($manifestFile, ($manifest | ConvertTo-Json -Depth 6))
$output = [Collections.Generic.List[string]]::new()
$failed = $false
try {
    & (Join-Path $b 'Invoke-LabAz.ps1') -AzArguments @(
    'acr','build','--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--registry','acrptubundle7d804f70','--image','macae/backend:8ac703a7-serialize-cap22',
    '--platform','linux','--timeout','600','--file',(Join-Path $context 'Dockerfile'),$context
    ) 2>&1 | ForEach-Object { $output.Add($_.ToString()) }
} catch {
    $failed = $true
    $output.Add($_.ToString())
}
$safe = ($output | Out-String) -replace '(?i)([?&](?:sig|token|access_token)=)[^&\s]+', '$1[REDACTED]'
[IO.File]::WriteAllText((Join-Path $b 'evidence\macae\remote-build-serialization.log'),$safe)
Write-Output $safe
if ($failed) { throw 'Remote build failed; full sanitized output saved. No automatic retry.' }
