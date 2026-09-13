$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$path = Join-Path $root 'evidence\documents\comparison14-persistence.json'
if (Test-Path $path) { throw 'Persistence evidence exists; use the existing result.' }
$js = @'
(async()=>{const h=await fetch('http://ca-dkm-kernel/health');const r=await fetch('http://ca-dkm-api/Documents/GetDocuments',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pageNumber:1,pageSize:10})});const d=await r.json();const files=[];for(const [id,name] of [['3951c54f0a974f79b9d8fc3d7e4591ad202609120125365840455','01-policy-2025.txt'],['cb45ef9f464f4569ac7c4bc523ef1aab202609120215417274224','02-policy-2026-table.pdf']]){const f=await fetch('http://ca-dkm-api/Documents/'+id+'/'+name);const b=Buffer.from(await f.arrayBuffer());files.push({id,name,status:f.status,bytes:b.length,sha256:require('crypto').createHash('sha256').update(b).digest('hex')})}return {case:'comparison14-persistence',utc:new Date().toISOString(),kernel_status:h.status,backend_status:r.status,total_documents:d.totalRecords,documents:d.documents,files,inference_calls:0}})().then(x=>console.log(JSON.stringify(x).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0')))).catch(e=>console.log(JSON.stringify({case:'comparison14-persistence',error:String(e)})))
'@
$bytes = [Text.Encoding]::UTF8.GetBytes($js)
$m=[IO.MemoryStream]::new();$z=[IO.Compression.GZipStream]::new($m,[IO.Compression.CompressionLevel]::SmallestSize,$true)
$z.Write($bytes,0,$bytes.Length);$z.Dispose();$encoded=[Convert]::ToBase64String($m.ToArray());$m.Dispose()
$command="node -e eval(require('zlib').gunzipSync(Buffer.from('$encoded','base64')).toString())"
$env:PYTHONUTF8='1';$env:PYTHONIOENCODING='utf-8'
$out=& (Join-Path $root 'Invoke-LabAz.ps1') -AzArguments @(
 'containerapp','exec','-n','ca-dkm-web','-g','accel-dkm-20260911','--command',$command,
 '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70')
$text=[regex]::Replace(($out -join "`n"),'\x1B\[[0-?]*[ -/]*[@-~]','')
$match=[regex]::Match($text,'\{"case":.*\}')
if(!$match.Success){throw 'No actual persistence response.'}
[IO.File]::WriteAllText($path,$match.Value)
$result=$match.Value|ConvertFrom-Json
$result|ConvertTo-Json -Depth 30
if($result.error -or $result.kernel_status -ne 200 -or $result.backend_status -ne 200 -or $result.total_documents -ne 2){throw 'Persistence check failed.'}
