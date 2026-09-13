[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$context = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-advisory-remote-24'
if(Test-Path $context){throw 'One-off context already exists; inspect the recorded run rather than blindly retrying.'}
[IO.Directory]::CreateDirectory($context)|Out-Null
Copy-Item (Join-Path $PSScriptRoot 'macae-advisory24.Dockerfile') (Join-Path $context 'Dockerfile')
foreach($name in @('macae_model_guard.py','macae_cosmos_budget.py','macae_advisory.py')){
    Copy-Item (Join-Path $PSScriptRoot $name) $context
}
foreach($name in @('advisory-team.json','advisory-request.txt')){
    Copy-Item (Join-Path $b "test-data\macae\$name") $context
}
$files=@(Get-ChildItem -LiteralPath $context -Force)
if($files.Count -ne 6 -or ($files|Where-Object PSIsContainer)){throw 'Unexpected clean build context'}
$manifest=@($files|ForEach-Object{[ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash $_.FullName).Hash.ToLowerInvariant()}})
[IO.File]::WriteAllText((Join-Path $b 'evidence\macae\advisory-build-context.json'),($manifest|ConvertTo-Json))
$output=[Collections.Generic.List[string]]::new()
$failed=$false
try{
    & (Join-Path $b 'Invoke-LabAz.ps1') -AzArguments @(
        'acr','build','--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
        '--registry','acrptubundle7d804f70','--image','macae/backend:8ac703a7-advisory-cap24',
        '--platform','linux','--timeout','600','--file',(Join-Path $context 'Dockerfile'),$context
    ) 2>&1|ForEach-Object{$output.Add($_.ToString())}
}catch{$failed=$true;$output.Add($_.ToString())}
$safe=($output|Out-String)-replace '(?i)([?&](?:sig|token|access_token)=)[^&\s]+','$1[REDACTED]'
[IO.File]::WriteAllText((Join-Path $b 'evidence\macae\advisory-remote-build.log'),$safe)
$safe
if($failed){throw 'Remote advisory build failed; full sanitized output saved, no automatic retry.'}
