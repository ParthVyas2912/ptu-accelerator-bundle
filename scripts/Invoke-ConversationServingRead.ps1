[CmdletBinding()]
param([ValidateRange(1,2)][int]$Attempt = 1)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$bundle = Split-Path -Parent $PSScriptRoot
$guard = Join-Path $bundle 'Invoke-LabAz.ps1'
$destination = Join-Path $bundle "evidence\conversation\serving-http-attempt-$Attempt.json"
if (Test-Path -LiteralPath $destination) { throw 'This HTTP verification is already exported; do not repeat.' }
$common = @('--name','ca-ptu-conversation-api','--resource-group','rg-ptu-conversation-demo',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70')
$active = @(& $guard -AzArguments (@('containerapp','revision','list') + $common +
    @('--all','--query','[?properties.active].name','-o','tsv')))
if ($active.Count -ne 1 -or $active[0] -ne "ca-ptu-conversation-api--serving-ro$Attempt") {
    throw 'Expected exactly the corresponding guarded serving revision.'
}
$output = @(& $guard -AzArguments (@('containerapp','exec') + $common +
    @('--revision',$active[0],'--container','api','--command',
      'timeout 240 python /app/src/api/ckm_serving_probe.py')))
$matches = [regex]::Matches(($output -join "`n"), 'CKM_SERVING_RESULT_BASE64=([A-Za-z0-9+/=]+)')
if ($matches.Count -ne 1) { throw 'No complete serving result. Do not rerun blindly; honor any exec429 backoff.' }
$json = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($matches[0].Groups[1].Value))
[IO.File]::WriteAllText($destination, $json + "`n", [Text.UTF8Encoding]::new($false))
$result = $json | ConvertFrom-Json
[pscustomobject]@{status=$result.status; tests=@($result.tests).Count; servingPID=$result.serving_pid;
    modelRequests=$result.model_requests; error=$result.error; evidence=$destination} | ConvertTo-Json
if ($result.status -ne 'passed') { throw 'Serving HTTP validation failed; full individual results saved.' }
