[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ScriptFile,
    [ValidateSet('backend','mcp','frontend')][string]$Container = 'backend'
)
$ErrorActionPreference = 'Stop'
$path = (Resolve-Path $ScriptFile).Path
if (-not $path.StartsWith($PSScriptRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or
    [IO.Path]::GetFileName($path) -notmatch '^macae_[a-z_]+\.py$') {
    throw 'Only MACAE-owned local evaluation scripts are supported.'
}
$env:MACAE_EVAL_PROGRAM = $path
$code = @'
import os,zlib
from pathlib import Path
b=zlib.compress(Path(os.environ["MACAE_EVAL_PROGRAM"]).read_bytes(),9)
print(f'exec(__import__(bytes([122,108,105,98]).decode()).decompress(({int.from_bytes(b,"big")}).to_bytes({len(b)})))')
'@ | python -
$exe = if ($Container -eq 'frontend') { '/usr/local/bin/python' } else { '/app/.venv/bin/python' }
$command = "$exe -c "+$code.Trim()
Write-Output ("Compact native-test command length="+$command.Length)
if ($command.Length -gt 2000) { throw 'Program too large for safe Azure exec command URI; package it into an image instead.' }
$b = Split-Path $PSScriptRoot -Parent
$output = @(& (Join-Path $b 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec','--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '-g','rg-ptu-macae-demo','-n','ptu-macae','--container',$Container,'--command',$command
))
foreach ($line in $output) {
    Write-Output $line
    if ($line -match 'MACAE_RESULT (?<payload>\{.*\})') {
        $result = $Matches.payload | ConvertFrom-Json
        if ($result.name -notmatch '^cloud-[a-z-]+$') { throw 'Unexpected evidence label.' }
        [IO.File]::WriteAllText((Join-Path $b ('evidence\macae\'+$result.name+'.json')),
            ($result.data | ConvertTo-Json -Depth 80))
    }
}
