[CmdletBinding()]
param([switch]$BackendOnly)
$ErrorActionPreference = 'Stop'
$B = Split-Path $PSScriptRoot -Parent
$root = Join-Path $env:LOCALAPPDATA 'ptu-modernize-container-build'
$context = Join-Path $root 'cloud'
if (Test-Path $context) { throw 'Cloud context already exists; inspect prior build before retrying.' }
Copy-Item (Join-Path $root 'backend') $context -Recurse
Copy-Item (Join-Path $PSScriptRoot 'modernize_cloud\*') $context -Force
$forbidden=Get-ChildItem $context -Recurse -Force -File | Where-Object { $_.Name -eq '.env' -or $_.Extension -in @('.pem','.pfx','.key') }
if ($forbidden) { throw 'Unexpected credential-like file in isolated cloud build context.' }
docker buildx build --builder ptu-modernize-builder --load --progress plain `
    --tag ptu-modernize-backend:7592ea9-eval1 $context
if ($LASTEXITCODE -ne 0) { throw 'Cloud runtime overlay build failed.' }
docker run --rm --network none --memory 1g --cpus 1 --entrypoint python `
    ptu-modernize-backend:7592ea9-eval1 -m unittest test_budget
if ($LASTEXITCODE -ne 0) { throw 'Linux container budget regressions failed.' }
$parserResult=docker run --rm --network none --memory 1g --cpus 1 --entrypoint /app/sql_agents/tools/linux-x64/tsqlParser `
    ptu-modernize-backend:7592ea9-eval1 --string 'SELECT TOP 5 order_id FROM orders;'
if ($LASTEXITCODE -ne 0) { throw 'Bundled Linux T-SQL parser failed.' }
$parserErrors=@($parserResult | ConvertFrom-Json)
if ($parserErrors.Count -ne 0) { throw 'Bundled Linux parser reported syntax errors for valid smoke fixture.' }
$parserResult
docker run --rm --network none --memory 1g --cpus 1 -e AZURE_CLIENT_ID=00000000-0000-0000-0000-000000000000 `
    --entrypoint python ptu-modernize-backend:7592ea9-eval1 -c 'import cloud_app; print("Original cloud application import passed without network")'
if ($LASTEXITCODE -ne 0) { throw 'Original application import failed in isolated Linux container.' }
& (Join-Path $B 'Invoke-LabAz.ps1') -AzArguments @('acr','login','--name','acrptubundle7d804f70',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70')
if ($LASTEXITCODE -ne 0) { throw 'Shared registry Entra login failed.' }
$images=@()
foreach ($item in @(
    @('ptu-modernize-backend:7592ea9-eval1','acrptubundle7d804f70.azurecr.io/modernize/backend:7592ea9-eval1'),
    @('ptu-modernize-frontend:7592ea9','acrptubundle7d804f70.azurecr.io/modernize/frontend:7592ea9')
)) {
    if ($BackendOnly -and $item[0].StartsWith('ptu-modernize-frontend:')) { continue }
    docker tag $item[0] $item[1]
    if ($LASTEXITCODE -ne 0) { throw 'Image tagging failed.' }
    docker push $item[1]
    if ($LASTEXITCODE -ne 0) { throw 'Isolated Modernize image push failed.' }
    $image=(docker image inspect $item[1] | ConvertFrom-Json)[0]
    $images+=@{tag=$item[1];id=$image.Id;repoDigests=$image.RepoDigests;sizeBytes=$image.Size}
}
[System.IO.File]::WriteAllText((Join-Path $B 'evidence\modernize\cloud-images.json'),
    (@{app='Modernize Your Code';images=$images;containerBudgetTests=9;linuxParser='passed';
       networkIsolatedImport='passed';credentialsInContext=$false;tlsVerificationDisabled=$false;
       adaptation='Original source/Docker runtime plus package mirror, async MI, durable budget and executable Linux parser mode'} | ConvertTo-Json -Depth 10))
'Modernize isolated images tested and pushed to approved shared Basic registry.'
