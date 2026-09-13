[CmdletBinding()]
param([ValidateSet('probe','run','export')][string]$Mode = 'probe')
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$bundle = Split-Path -Parent $PSScriptRoot
$destination = Join-Path $bundle 'evidence\conversation\data-workflow-results.json'
if ($Mode -eq 'run' -and (Test-Path -LiteralPath $destination)) {
    throw 'An exported data-workflow result already exists. Review cumulative budget and persisted SQL data; do not rerun.'
}
$command = "timeout 240 env PYTHONPATH=/app python /app/src/api/ckm_data_eval.py $Mode"
$output = @(& (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec','--name','ca-ptu-conversation-api',
    '--resource-group','rg-ptu-conversation-demo',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--container','api','--command',$command
))
$encoded = [regex]::Matches(($output -join "`n"), 'CKM_DATA_RESULT_BASE64=([A-Za-z0-9+/=]+)')
if ($encoded.Count -ne 1) {
    throw 'No complete unique result received. Do not repeat inference; use export while the original replica runs.'
}
$json = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded[0].Groups[1].Value))
$result = $json | ConvertFrom-Json
if ($Mode -eq 'probe') { $destination = Join-Path $bundle 'evidence\conversation\data-auth-probe.json' }
[IO.File]::WriteAllText($destination, $json + "`n", [Text.UTF8Encoding]::new($false))
[pscustomobject]@{
    status = $result.status
    additionalModelRequests = $result.actual_additional_model_requests
    cumulativeModelRequests = $result.cumulative_model_requests
    tests = $(if ($null -eq $result.tests) { 0 } else { @($result.tests).Count })
    errorType = $result.error_type
    errorMessage = $result.error_message
    evidence = $destination
} | ConvertTo-Json
if ($Mode -eq 'probe' -and $result.status -ne 'authorized') { throw 'Private data authorization probe failed; evidence saved.' }
if ($Mode -ne 'probe' -and $result.status -ne 'completed_pending_manual_review') { throw 'Native workflow incomplete; evidence saved. Do not blindly rerun.' }
