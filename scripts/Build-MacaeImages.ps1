[CmdletBinding()]
param([ValidateSet('backend','mcp','frontend','all')][string]$Component = 'all')
$ErrorActionPreference = 'Stop'
$sha = '8ac703a71f10b622bd3c82a9cc2b5dfe921c3025'
$stage = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-container-source'
if ((git -C $stage rev-parse HEAD).Trim() -ne $sha) { throw 'Pinned source checkout missing/mismatched.' }
if (git -C $stage status --porcelain) { throw 'Build context must be a clean pinned worktree.' }
$builder = 'macae-eval'
$builders = @(docker buildx ls --format '{{.Name}}')
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect local Docker builders.' }
if ($builders -notcontains $builder) {
    docker buildx create --name $builder --driver docker-container --driver-opt memory=3g,memory-swap=3g,cpu-period=100000,cpu-quota=150000 --buildkitd-config (Join-Path $PSScriptRoot 'macae-buildkitd.toml')
    if ($LASTEXITCODE -ne 0) { throw 'Bounded local builder creation failed.' }
}
# Explicit builder selection does not change the default or touch another app's builder.
$map = @{backend='src/backend'; mcp='src/mcp_server'; frontend='src/App'}
$components = if ($Component -eq 'all') { @('mcp','backend','frontend') } else { @($Component) }
foreach ($part in $components) {
    $context = Join-Path $stage $map[$part]
    # Only public committed example env files may be present; no runtime env files.
    $envFiles = Get-ChildItem $context -Force -Recurse -File -Filter '.env*' |
        Where-Object { $_.Name -notin @('.env.sample','.env.example') }
    if ($envFiles) { throw 'Unexpected runtime env file in image context.' }
    docker buildx build --builder $builder --platform linux/amd64 --load --progress plain --label "org.opencontainers.image.revision=$sha" --tag "ptu-macae-${part}:8ac703a7" --file (Join-Path $context 'Dockerfile') $context
    if ($LASTEXITCODE -ne 0) { throw "Official $part image build failed; no cloud push/deploy performed." }
}
# Images remain local. Registry login/push and ACA deployment require parent-supplied IDs.
