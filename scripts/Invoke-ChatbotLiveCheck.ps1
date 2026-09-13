[CmdletBinding()]
param(
    [ValidateSet('search','live')][string]$Stage = 'search',
    [switch]$ConfirmModelCalls
)
$ErrorActionPreference = 'Stop'
if($Stage -eq 'live') {
    throw 'Chatbot allowance is closed at10; two units were reclaimed. A new explicit operator allowance is required.'
}
if($Stage -eq 'live' -and -not $ConfirmModelCalls) {
    throw 'The native catalog journey consumes the durable 12-unit budget; explicit confirmation is required.'
}
$bundle = Split-Path $PSScriptRoot -Parent
$file = if($Stage -eq 'search'){'search_check.py'}else{'live_check.py'}
$script = Join-Path $PSScriptRoot "chatbot_runtime\$file"
$buffer = [IO.MemoryStream]::new()
$gzip = [IO.Compression.GZipStream]::new($buffer, [IO.Compression.CompressionLevel]::Optimal, $true)
$gzip.Write([IO.File]::ReadAllBytes($script))
$gzip.Dispose()
$payload = [Convert]::ToBase64String($buffer.ToArray())
$buffer.Dispose()
# Whitespace-free argv avoids ACA console quote splitting; payload is audited source, not credentials.
$expression = 'exec(__import__(bytes([103,122,105,112]).decode()).decompress(__import__(bytes([98,97,115,101,54,52]).decode()).b64decode(__import__(bytes([115,121,115]).decode()).argv[1])))'
if($payload.Length + $expression.Length -gt 1700) {
    throw 'Payload exceeds the conservative ACA console URL size; use a baked helper in a remote-built native image.'
}
$raw = & (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--resource-group','accel-chatbot-eval-0911',
    '--name','chatbot-chat-api',
    '--command',"python -c $expression $payload"
)
$raw
$records = @($raw | Where-Object {([string]$_).Trim().StartsWith('{')} | ForEach-Object {$_ | ConvertFrom-Json})
if($Stage -eq 'live') {
    $result = $records | Where-Object check -eq 'native_catalog_and_negative_sku'
    if(-not $result) { throw 'No completed native result; inspect execution or budget-gate errors.' }
    & (Join-Path $PSScriptRoot 'Test-ChatbotNativeResult.ps1') -Result $result
} elseif(-not ($records | Where-Object check -eq 'keyless_private_search')) {
    throw 'Native private Search probe did not complete successfully.'
}
