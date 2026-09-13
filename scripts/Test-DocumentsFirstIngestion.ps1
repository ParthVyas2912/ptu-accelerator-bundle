# Exactly one approved synthetic upload; does not retry and never retrieves credentials.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$file = Join-Path $root 'test-data\documents\01-policy-2025.txt'
if ((Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne '12a5a842e6d44db9758be011d45099865c74123592f4c07dd3c4477281343f30') {
    throw 'Synthetic fixture hash changed; refuse unreviewed input.'
}
$payload = [Convert]::ToBase64String([IO.File]::ReadAllBytes($file))
$js = "const f=new FormData();f.append('file',new Blob([Buffer.from('$payload','base64')],{type:'text/plain'}),'01-policy-2025.txt');const t=Date.now();fetch('http://ca-dkm-api/Documents/ImportDocument',{method:'POST',body:f,signal:AbortSignal.timeout(180000)}).then(async r=>console.log(JSON.stringify({status:r.status,ms:Date.now()-t,body:await r.text()}))).catch(e=>console.log(JSON.stringify({error:String(e),ms:Date.now()-t})))"
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($js))
# Compact encoding is solely to preserve quotes through ACA console command parsing.
# A numeric byte-array command exceeded the console's IIS URL/query limit.
$command = "node -e eval(atob('$encoded'))"
& (Join-Path $root 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp', 'exec',
    '--name', 'ca-dkm-web',
    '--resource-group', 'accel-dkm-20260911',
    '--command', $command,
    '--subscription', '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
)
