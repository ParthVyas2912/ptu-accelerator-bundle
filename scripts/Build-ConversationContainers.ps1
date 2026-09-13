[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$workspace = Join-Path $env:LOCALAPPDATA 'ptu-eval\conversation\containers'
if (-not (Test-Path (Join-Path $workspace 'api\ApiApp.Dockerfile'))) {
    throw 'Run ckm-prepare-containers.py first.'
}

# Dedicated local builder only; never select/change another accelerator's builder.
docker buildx inspect ptu-conversation-eval
if ($LASTEXITCODE -ne 0) {
    docker buildx create --name ptu-conversation-eval --driver docker-container `
        --driver-opt memory=2147483648 --driver-opt cpu-period=100000 `
        --driver-opt cpu-quota=100000
    if ($LASTEXITCODE -ne 0) { throw 'CKM local builder creation failed.' }
}

docker buildx build --builder ptu-conversation-eval --load --progress plain `
    --label org.opencontainers.image.revision=8a00aa54bc25fd3624020648c63f2c069172d8ca `
    --file (Join-Path $workspace 'api\ApiApp.Dockerfile') `
    --tag ptu-conversation/api:8a00aa5-base (Join-Path $workspace 'api')
if ($LASTEXITCODE -ne 0) { throw 'Official CKM API image build failed; frontend build not started.' }

docker buildx build --builder ptu-conversation-eval --load --progress plain `
    --label org.opencontainers.image.revision=8a00aa54bc25fd3624020648c63f2c069172d8ca `
    --file (Join-Path $workspace 'ui\WebApp.Runtime.Dockerfile') `
    --tag ptu-conversation/ui:8a00aa5-runtime (Join-Path $workspace 'ui')
if ($LASTEXITCODE -ne 0) { throw 'CKM official frontend runtime-stage image build failed.' }

docker image inspect ptu-conversation/api:8a00aa5-base ptu-conversation/ui:8a00aa5-runtime `
    --format '{{.Id}} size={{.Size}}'
