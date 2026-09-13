[CmdletBinding()]
param(
    [ValidateSet('chat-api','chat-ui','scenario-ui')][string]$Component = 'chat-api',
    [ValidatePattern('^cb86d11-eval[0-9]+$')][string]$ImageTag = 'cb86d11-eval1'
)
$ErrorActionPreference = 'Stop'
$stage = Join-Path $env:LOCALAPPDATA "ptu-chatbot\cloud-images\$Component"
$tag = "acrptubundle7d804f70.azurecr.io/chatbot/${Component}:$ImageTag"
docker buildx build --builder ptu-chatbot-eval --platform linux/amd64 --load --progress plain --tag $tag $stage
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
if($Component -eq 'chat-api') {
    docker run --rm --network none --memory 512m --cpus 1 --entrypoint python $tag -m pip check
    if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
} else {
    docker run --rm --network none --memory 128m --cpus 0.25 --entrypoint /bin/sh $tag -n /docker-entrypoint.d/startup.sh
    if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
    docker run --rm --network none --memory 128m --cpus 0.25 --entrypoint nginx $tag -t
    if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
}
docker push $tag
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
docker image inspect --format '{{json .RepoDigests}}' $tag
exit $LASTEXITCODE
