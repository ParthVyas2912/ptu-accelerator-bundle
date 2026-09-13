[CmdletBinding()]
param(
    [ValidateSet('chat-backend','chat-frontend','scenario-backend','scenario-frontend')]
    [string]$Component = 'chat-backend'
)
$ErrorActionPreference = 'Stop'
$desktop = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$repo = Join-Path $desktop 'repo\customer-chatbot-solution-accelerator'
$builder = 'ptu-chatbot-eval'
$names = @(docker buildx ls --format '{{.Name}}')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($builder -notin $names) {
    # Do not change the shared default builder or run concurrent Chatbot builds.
    docker buildx create --name $builder --driver docker-container `
        --driver-opt 'memory=1536m,memory-swap=1536m,cpu-period=100000,cpu-quota=100000'
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
$definitions = @{
    'chat-backend' = @{ Dockerfile='chat-app\backend\Dockerfile'; Context='' }
    'chat-frontend' = @{ Dockerfile='chat-app\frontend\Dockerfile'; Context='chat-app\frontend' }
    'scenario-backend' = @{ Dockerfile='scenario-app\backend\Dockerfile'; Context='scenario-app\backend' }
    'scenario-frontend' = @{ Dockerfile='scenario-app\frontend\Dockerfile'; Context='' }
}
$definition = $definitions[$Component]
$context = if($definition.Context){Join-Path $repo $definition.Context}else{$repo}
foreach ($directory in @($repo,$context,(Join-Path $repo 'chat-app\backend'),(Join-Path $repo 'scenario-app\backend'))) {
    if (Test-Path (Join-Path $directory '.env')) {
        throw 'Refusing to build while local .env configuration exists in a native build directory.'
    }
}
$tag = "ptu-chatbot/${Component}:cb86d11-native"
# Native repository Dockerfile. No registry push or cloud deployment.
# The later cloud evaluation overlay must add durable metering/identity config
# before a model-enabled deployment; this base tag alone is NOT deployment-ready.
docker buildx build --builder $builder --platform linux/amd64 --load `
    --progress plain --tag $tag --file (Join-Path $repo $definition.Dockerfile) $context
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker image inspect --format '{{.Id}}' $tag
exit $LASTEXITCODE
