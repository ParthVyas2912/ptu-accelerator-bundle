[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('repair','verify')][string]$Mode)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path -Parent $PSScriptRoot
$guard = Join-Path $bundle 'Invoke-LabAz.ps1'
$common = @('--name','ca-ptu-conversation-api','--resource-group','rg-ptu-conversation-demo',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70')
$active = @(& $guard -AzArguments (@('containerapp','revision','list') + $common +
    @('--all','--query','[?properties.active].name','-o','tsv')) | Where-Object { $_.Trim() })
if ($active.Count -ne 1) { throw 'Exactly one active own API revision is required.' }
$output = @(& $guard -AzArguments (@('containerapp','exec') + $common +
    @('--revision',$active[0].Trim(),'--container','api','--command',
      "timeout 90 env PYTHONPATH=/app python /app/src/api/ckm_sql_identity.py $Mode")))
$match = [regex]::Matches(($output -join "`n"), 'CKM_SQL_RESULT_BASE64=([A-Za-z0-9+/=]+)')
if ($match.Count -ne 1) { throw 'No unique SQL identity result received.' }
$json = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($match[0].Groups[1].Value))
$result = $json | ConvertFrom-Json
$destination = Join-Path $bundle "evidence\conversation\sql-identity-$Mode.json"
[IO.File]::WriteAllText($destination, $json + "`n", [Text.UTF8Encoding]::new($false))
$json
if ($result.status -ne 'succeeded') { throw 'SQL identity operation failed; evidence saved.' }
