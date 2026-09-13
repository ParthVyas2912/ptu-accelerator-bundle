param(
    [ValidateSet('Backend', 'Frontend', 'BuildFrontend')]
    [string]$Component = 'Backend'
)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path $PSScriptRoot -Parent
$desktop = Split-Path (Split-Path $bundle -Parent) -Parent
$repo = Join-Path $desktop 'repo\Conversation-Knowledge-Mining-Solution-Accelerator'
$python = Join-Path $env:LOCALAPPDATA 'ptu-eval\conversation\venv\Scripts\python.exe'
$frontend = Join-Path $env:LOCALAPPDATA 'ptu-eval\conversation\frontend'
if (-not (Test-Path (Join-Path $frontend 'package.json'))) {
    $frontend = Join-Path $repo 'src\app'
}
if ($Component -eq 'Backend') {
    & $python (Join-Path $PSScriptRoot 'ckm-local-evaluate.py')
} elseif ($Component -eq 'BuildFrontend') {
    Set-Location $frontend
    $env:REACT_APP_API_BASE_URL = 'http://127.0.0.1:8115/api'
    $env:GENERATE_SOURCEMAP = 'false'
    npm run build
} else {
    # Original compiled React app. Bind explicitly to loopback; no public ingress.
    if (-not (Test-Path (Join-Path $frontend 'build\index.html'))) {
        throw 'Original frontend build is not ready. Complete BuildFrontend before starting this endpoint.'
    }
    & $python -m http.server 5115 --bind 127.0.0.1 --directory (Join-Path $frontend 'build')
}
