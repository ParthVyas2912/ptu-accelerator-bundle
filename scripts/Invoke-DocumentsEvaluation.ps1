[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('health','metadata','ingest-second','qa-document','qa-corpus','sources','encoding-probe')]
    [string]$Case,
    [ValidatePattern('^[a-z0-9-]+$')]
    [string]$Label = 'retry-phase'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$directory = Join-Path $root 'evidence\documents'
$resultPath = Join-Path $directory "$Label-$Case.json"
if (Test-Path $resultPath) { throw 'Case evidence exists; refusing accidental repeat.' }
$budgetPath = Join-Path $directory 'model-budget.json'
$budget = Get-Content $budgetPath -Raw | ConvertFrom-Json
$paid = $Case -in @('ingest-second','qa-document','qa-corpus')
if ($paid) {
    if (!$budget.retry_control_deployed_verified -or $budget.pending_operation) {
        throw 'Retry deployment must be verified and prior wire counters reconciled.'
    }
    # Small single-page ingestion normally4; reserve2 more for the stock empty-keyword fallback.
    $maximum = if ($Case -eq 'ingest-second') { 6 } else { 2 }
    if ($budget.actual_observed_attempts + $maximum -gt 12) { throw 'Remaining wire-attempt budget insufficient.' }
    $budget | Add-Member pending_operation ([ordered]@{
        case=$Case; baseline=$budget.actual_observed_attempts; maximum=$maximum
        started_utc=[DateTime]::UtcNow.ToString('o'); automatic_retry=$false
    }) -Force
    [IO.File]::WriteAllText($budgetPath, ($budget | ConvertTo-Json -Depth 20))
}
$first = '3951c54f0a974f79b9d8fc3d7e4591ad202609120125365840455'
$common = "const c='$Case',t=Date.now();const post=(p,b)=>fetch('http://ca-dkm-api'+p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b),signal:AbortSignal.timeout(180000)});"
$work = switch ($Case) {
    'encoding-probe' { "return {kind:'synthetic transport probe, not an AI answer',text:'minus \u2212 euro \u20ac snowman \u2603'};" }
    'health' { "const a=await fetch('http://ca-dkm-kernel/health');const b=await post('/Documents/GetDocuments',{pageNumber:1,pageSize:10});return {kernel:{status:a.status,body:await a.text()},backend:{status:b.status,body:await b.text()}};" }
    'metadata' { "const results=[];for(const tags of [{},{place:'Cedar Bay'},{place:'Neverland'},{person:'Omar Patel'}]){const r=await post('/Documents/GetDocuments',{pageNumber:1,pageSize:10,tags});results.push({tags,status:r.status,body:await r.text()})}return results;" }
    'ingest-second' {
        $file = Join-Path $root 'test-data\documents\02-policy-2026-table.pdf'
        if ((Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne '1b6786929592267c2d681de3f6afc6dab06dbb7e4f3a892c793194de8d96d2de') {
            throw 'Fixture hash mismatch; no request made.'
        }
        $memory = [IO.MemoryStream]::new()
        $gzip = [IO.Compression.GZipStream]::new($memory,[IO.Compression.CompressionLevel]::SmallestSize,$true)
        $bytes = [IO.File]::ReadAllBytes($file)
        $gzip.Write($bytes,0,$bytes.Length); $gzip.Dispose()
        $payload = [Convert]::ToBase64String($memory.ToArray()); $memory.Dispose()
        "const f=new FormData();f.append('file',new Blob([require('zlib').gunzipSync(Buffer.from('$payload','base64'))],{type:'application/pdf'}),'02-policy-2026-table.pdf');const r=await fetch('http://ca-dkm-api/Documents/ImportDocument',{method:'POST',body:f,signal:AbortSignal.timeout(180000)});return {status:r.status,body:await r.text()};"
    }
    'qa-document' {
        "const request={question:'According to this policy, what is the annual training allowance and policy year? Cite the source.',documents:['$first']};const r=await post('/Documents/Ask',request);return {request,status:r.status,body:await r.text()};"
    }
    'qa-corpus' {
        "const request={question:'Compare the 2025 and 2026 Cedar Bay policies: annual training days in each, the increase in days and percent, and which policy supersedes which. Cite both source documents.',documents:[]};const r=await post('/Documents/Ask',request);return {request,status:r.status,body:await r.text()};"
    }
    'sources' {
        $secondResult = Get-Content (Join-Path $directory 'retry-phase-ingest-second.json') -Raw | ConvertFrom-Json
        $second = ($secondResult.result.body | ConvertFrom-Json).documentId
        if ($second -notmatch '^[a-zA-Z0-9]+$') { throw 'No verified second document ID.' }
        "const results=[];for(const [id,name] of [['$first','01-policy-2025.txt'],['$second','02-policy-2026-table.pdf']]){const r=await fetch('http://ca-dkm-api/Documents/'+id+'/'+name);const b=Buffer.from(await r.arrayBuffer());results.push({id,name,status:r.status,bytes:b.length,sha256:require('crypto').createHash('sha256').update(b).digest('hex')})}return results;"
    }
}
$emit = "const emit=o=>{const s=JSON.stringify(o);require('fs').writeFileSync('/tmp/dkm-'+c+'-result.json',s);console.log(s.replace(/[\u007f-\uffff]/g,x=>'\\u'+x.charCodeAt(0).toString(16).padStart(4,'0')))};"
$js = "$common$emit(async()=>{$work})().then(result=>emit({case:c,utc:new Date().toISOString(),ms:Date.now()-t,result})).catch(e=>emit({case:c,ms:Date.now()-t,error:String(e)}))"
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($js))
$command = "node -e eval(atob('$encoded'))"
# Encoding/compression preserves console parsing and limits URL length, not access controls.
$output = & (Join-Path $root 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec','--name','ca-dkm-web','--resource-group','accel-dkm-20260911',
    '--command',$command,'--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70'
)
$text = $output -join "`n"
$text = [regex]::Replace($text, '\x1B\[[0-?]*[ -/]*[@-~]', '')
# Only synthetic responses are expected. Never persist accidental credential-shaped values.
$text = [regex]::Replace($text, '(?i)(AccountKey|Password|api-key)([=:]\s*)[^;\s"]+', '$1$2[REDACTED]')
$text = [regex]::Replace($text, '(?i)([?&]sig=)[^&\s"]+', '$1[REDACTED]')
$match = [regex]::Match($text, '\{"case":.*\}')
if (!$match.Success) { throw 'No structured app response; paid reservation remains pending.' }
$response = $match.Value | ConvertFrom-Json
[IO.File]::WriteAllText($resultPath, ($response | ConvertTo-Json -Depth 40))
$response | ConvertTo-Json -Depth 40
