param(
    [Parameter(Mandatory)]
    [ValidateSet('backend','worker','frontend','database','storage')]
    [string]$Service
)
$ErrorActionPreference='Stop'
$Repo='C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\chat-with-your-data-solution-accelerator'
$Python=Join-Path $env:LOCALAPPDATA 'ptu-eval\cwyd\runtime\Scripts\python.exe'
$env:CWYD_USE_ACCOUNT_OPENAI_ENDPOINT='true'
$env:CWYD_INFERENCE_DISABLED='true'
if ($Service -in @('backend','worker')) {
    & $Python (Join-Path $PSScriptRoot 'cwyd_runtime.py') budget-status
    if ($LASTEXITCODE -ne 0) { throw 'CWYD budget policy validation failed; refusing startup.' }
}
switch ($Service) {
    'backend' {
        & $Python (Join-Path $PSScriptRoot 'cwyd_runtime.py') backend
        if ($LASTEXITCODE -ne 0) { throw 'CWYD backend exited with an error.' }
    }
    'worker' { throw 'CWYD evaluation is closed at16/16. Worker remains stopped and queued data preserved; explicit new authorization is required.' }
    'frontend' {
        Set-Location "$Repo\src\frontend"
        $env:VITE_BACKEND_URL='http://127.0.0.1:8112'
        node --input-type=module -e "import {createServer} from 'vite'; const server=await createServer({server:{host:'127.0.0.1',port:5112,strictPort:true,proxy:{'/api':{target:'http://127.0.0.1:8112',changeOrigin:true}}}}); await server.listen(); server.printUrls();"
    }
    'database' { docker start --attach ptu-cwyd-postgres }
    'storage' { docker start --attach ptu-cwyd-azurite }
}
