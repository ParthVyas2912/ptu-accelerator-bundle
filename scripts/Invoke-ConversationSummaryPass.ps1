[CmdletBinding()]
param([switch]$ExportOnly)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$bundle = Split-Path -Parent $PSScriptRoot
$destination = Join-Path $bundle 'evidence\conversation\summary-results.json'
if ((Test-Path $destination) -and -not $ExportOnly) {
    throw 'A live pass is already exported. Do not repeat model calls; review the global12-request budget.'
}
$mode = if ($ExportOnly) { 'export' } else { 'run --counterfactuals' }
$command = "env PYTHONPATH=/app python /app/src/api/ckm_summary_eval.py $mode"
$output = @(& (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec','--name','ca-ptu-conversation-api',
    '--resource-group','rg-ptu-conversation-demo',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--container','api','--command',$command
))
$text = $output -join "`n"
$start = $text.IndexOf('{"scope": "Original CKM')
if ($start -lt 0) {
    throw 'No structured result received. Do not repeat the live command; use ExportOnly while the replica remains running.'
}
$depth = 0
$quoted = $false
$escaped = $false
$end = -1
for ($i = $start; $i -lt $text.Length; $i++) {
    $character = $text[$i]
    if ($quoted) {
        if ($escaped) { $escaped = $false }
        elseif ($character -eq '\') { $escaped = $true }
        elseif ($character -eq '"') { $quoted = $false }
    } elseif ($character -eq '"') {
        $quoted = $true
    } elseif ($character -eq '{') {
        $depth++
    } elseif ($character -eq '}') {
        $depth--
        if ($depth -eq 0) { $end = $i; break }
    }
}
if ($end -lt 0) {
    throw 'Incomplete result. Preserve the running replica and use ExportOnly; never blindly rerun inference.'
}
$json = $text.Substring($start, $end - $start + 1)
$result = $json | ConvertFrom-Json
if ($result.scope -ne 'Original CKM /api/processing/summarize in-process API component') {
    throw 'Unexpected result scope.'
}
[IO.File]::WriteAllText($destination, $json + "`n", [Text.UTF8Encoding]::new($false))
[pscustomobject]@{
    status = $result.status
    requests = $result.actual_model_requests
    tests = @($result.tests).Count
    sdkRetries = $result.sdk_retries
    evidence = $destination
} | ConvertTo-Json
if ($result.actual_model_requests -gt 7 -or $result.actual_model_requests -gt 12) {
    throw 'Unexpected request-count invariant violation; evidence preserved.'
}
if ($result.status -ne 'completed_pending_manual_review') {
    throw 'Native pass stopped or failed. Evidence preserved; do not repeat automatically.'
}
