[CmdletBinding()]
param([switch]$BackendOnly)
$ErrorActionPreference = 'Stop'
$B = Split-Path $PSScriptRoot -Parent
$root = Join-Path $env:LOCALAPPDATA 'ptu-modernize-container-build'
$builder = 'ptu-modernize-builder'
docker buildx inspect $builder
if ($LASTEXITCODE -ne 0) {
    docker buildx create --name $builder --driver docker-container `
        --driver-opt 'memory=2g,memory-swap=2g,cpu-period=100000,cpu-quota=200000' `
        --buildkitd-config (Join-Path $PSScriptRoot 'modernize-buildkitd.toml')
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create bounded Modernize-only local builder.' }
}
$results = @()
$historyPath=Join-Path $B 'evidence\modernize\container-build-results.json'
if (Test-Path $historyPath) {
    $prior=Get-Content $historyPath -Raw | ConvertFrom-Json
    $results += @($prior.results)
}
$services=@('backend','frontend')
if ($BackendOnly) { $services=@('backend') }
foreach ($service in $services) {
    $tag = if ($service -eq 'backend') { 'ptu-modernize-backend:7592ea9-base' } else { 'ptu-modernize-frontend:7592ea9' }
    $started = Get-Date
    docker buildx build --builder $builder --load --progress plain --tag $tag (Join-Path $root $service)
    $exit = $LASTEXITCODE
    $results += @{ service=$service; tag=$tag; exitCode=$exit; elapsedSeconds=((Get-Date)-$started).TotalSeconds }
    [System.IO.File]::WriteAllText($historyPath,
        (@{ app='Modernize Your Code'; builder=$builder; builderMemory='2GiB'; builderCpu=2;
            buildsSequential=$true; cloudPushed=$false; results=$results } | ConvertTo-Json -Depth 8))
    if ($exit -ne 0) { throw "Official $service image build failed; see attached tool output." }
}
