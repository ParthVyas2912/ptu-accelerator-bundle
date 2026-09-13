[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('inventory','probe','compare','read-result')][string]$Mode,
    [ValidatePattern('^[a-z0-9-]*$')][string]$Container = '',
    [ValidatePattern('^[a-z0-9-]+$')][string]$EvidenceLabel = 'comparison14',
    [switch]$Stage
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if ($EvidenceLabel -ne 'comparison14' -and $Mode -ne 'read-result') {
    throw 'Alternative evidence labels are allowed only for read-only durable response retrieval.'
}
$path = Join-Path $root "evidence\documents\$EvidenceLabel-$Mode.json"
if (Test-Path $path) { throw 'Evidence already exists; no automatic repeat.' }
if ($Mode -eq 'compare') {
    $guardPath = Join-Path $root 'evidence\documents\comparison14-guard.json'
    $guard = Get-Content $guardPath -Raw | ConvertFrom-Json
    if (!$guard.armed -or $guard.cap -ne 14 -or $guard.baseline -ne 12 -or !$guard.recovery_checked -or !$guard.capture_verified) {
        throw 'Comparison-only approval, recovery and verified capture required.'
    }
    $guard.armed = $false
    $guard | Add-Member consumed_utc ([DateTime]::UtcNow.ToString('o')) -Force
    [IO.File]::WriteAllText($guardPath,($guard | ConvertTo-Json -Depth 15))
}
$source = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'documents-comparison14.cjs'))
$bytes = [Text.Encoding]::UTF8.GetBytes($source)
$memory = [IO.MemoryStream]::new()
$gzip = [IO.Compression.GZipStream]::new($memory,[IO.Compression.CompressionLevel]::SmallestSize,$true)
$gzip.Write($bytes,0,$bytes.Length); $gzip.Dispose()
$encoded = [Convert]::ToBase64String($memory.ToArray()); $memory.Dispose()
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
if ($Stage) {
    # Small chunks avoid the ACA console gateway's URL-length limit.
    for ($offset=0; $offset -lt $encoded.Length; $offset+=1200) {
        $chunk = $encoded.Substring($offset,[Math]::Min(1200,$encoded.Length-$offset))
        $method = if ($offset -eq 0) { 'writeFileSync' } else { 'appendFileSync' }
        $stageCommand = "node -e require('fs').$method('/tmp/dkm14-source.b64','$chunk')"
        & (Join-Path $root 'Invoke-LabAz.ps1') -AzArguments @(
            'containerapp','exec','-n','ca-dkm-web','-g','accel-dkm-20260911','--command',$stageCommand,
            '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70') | Out-Null
    }
}
$command = "node -e require('fs').writeFileSync('/tmp/dkm14.cjs',require('zlib').gunzipSync(Buffer.from(require('fs').readFileSync('/tmp/dkm14-source.b64','utf8'),'base64')));process.argv[2]='$Mode';process.argv[3]='$Container';require('/tmp/dkm14.cjs')"
$out = & (Join-Path $root 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec','-n','ca-dkm-web','-g','accel-dkm-20260911','--command',$command,
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70')
$text = [regex]::Replace(($out -join "`n"),'\x1B\[[0-?]*[ -/]*[@-~]','')
$match = [regex]::Match($text,'\{"case":.*\}')
if (!$match.Success) { throw 'No structured response; recover persisted Blob, never rerun inference.' }
$result = $match.Value | ConvertFrom-Json
# Preserve the exact JSON values; PowerShell's date auto-conversion can trim ISO fractions.
[IO.File]::WriteAllText($path,$match.Value)
$result | ConvertTo-Json -Depth 50
if ($result.error) { throw 'Operation failed; persisted failure evidence is not a pass.' }
