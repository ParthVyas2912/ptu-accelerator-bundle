$ErrorActionPreference='Stop'
$B=Split-Path $PSScriptRoot -Parent
$repo=Join-Path (Split-Path (Split-Path $B -Parent) -Parent) 'repo\Modernize-your-code-solution-accelerator'
$source=Join-Path $repo 'src\frontend'
$context=Join-Path $env:LOCALAPPDATA 'ptu-modernize-container-build\frontend-runtime'
if (Test-Path $context) { throw 'Inspect existing runtime context before retry.' }
New-Item -ItemType Directory -Path $context | Out-Null
Copy-Item (Join-Path $source 'dist') $context -Recurse
Copy-Item (Join-Path $source 'requirements.txt') $context
Copy-Item (Join-Path $source 'frontend_server.py') $context
Copy-Item (Join-Path $PSScriptRoot 'modernize_cloud\frontend-runtime.Dockerfile') (Join-Path $context 'Dockerfile')
$hashes=Get-ChildItem (Join-Path $context 'dist') -File -Recurse | ForEach-Object {
    @{file=$_.FullName.Substring($context.Length+1);sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash}
}
docker buildx build --builder ptu-modernize-builder --load --progress plain `
    --tag ptu-modernize-frontend:7592ea9 $context
if ($LASTEXITCODE -ne 0) { throw 'Original frontend runtime-stage build failed.' }
$tag='acrptubundle7d804f70.azurecr.io/modernize/frontend:7592ea9'
docker tag ptu-modernize-frontend:7592ea9 $tag
if ($LASTEXITCODE -ne 0) { throw 'UI image tag failed.' }
docker push $tag
if ($LASTEXITCODE -ne 0) { throw 'UI image push failed.' }
$image=(docker image inspect $tag | ConvertFrom-Json)[0]
$path=Join-Path $B 'evidence\modernize\cloud-images.json'
$manifest=Get-Content $path -Raw | ConvertFrom-Json
$manifest.images+=@{tag=$tag;id=$image.Id;repoDigests=$image.RepoDigests;sizeBytes=$image.Size}
$manifest | Add-Member -NotePropertyName frontendPublished -NotePropertyValue $true -Force
$manifest | Add-Member -NotePropertyName frontendBuild -NotePropertyValue @{
    source='Original Python runtime stage + already successful original native React production build';
    reason='Official container npm install reported Exit handler never called, then vite missing';
    assetHashes=$hashes;newUiImplementation=$false} -Force
[System.IO.File]::WriteAllText($path,($manifest | ConvertTo-Json -Depth 12))
'Original frontend runtime image published; reused verified production assets, not a replacement UI.'
