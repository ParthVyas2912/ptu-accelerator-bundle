[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$desktop = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$repo = Join-Path $desktop 'repo\customer-chatbot-solution-accelerator'
$runtime = Join-Path $env:LOCALAPPDATA 'ptu-chatbot'
$stage = Join-Path $runtime 'cloud-images'
function Copy-SourceTree([string]$Source,[string]$Destination,[string[]]$Extensions) {
    $sourceRoot = (Resolve-Path $Source).Path
    foreach($file in Get-ChildItem -LiteralPath $sourceRoot -Recurse -File) {
        if ($Extensions.Count -gt 0 -and $file.Extension -notin $Extensions) { continue }
        if ($file.FullName -match '[\\/](\.azure|\.git|\.venv|node_modules|__pycache__)[\\/]' -or $file.Name -like '.env*') { continue }
        $relative = [IO.Path]::GetRelativePath($sourceRoot,$file.FullName)
        $target = Join-Path $Destination $relative
        New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $target
    }
}
$chat = Join-Path $stage 'chat-api'
Copy-SourceTree (Join-Path $repo 'infra\scripts\post-provision\data_scripts') (Join-Path $chat 'native\infra\scripts\post-provision\data_scripts') @('.py','.txt')
Copy-SourceTree (Join-Path $repo 'infra\scripts\post-provision\agent_scripts') (Join-Path $chat 'native\infra\scripts\post-provision\agent_scripts') @('.py','.txt')
Copy-SourceTree (Join-Path $repo 'scenarios') (Join-Path $chat 'native\scenarios') @('.py','.txt','.json','.csv')
Copy-SourceTree (Join-Path $repo 'chat-app\backend\app') (Join-Path $chat 'app') @('.py')
New-Item -ItemType Directory -Path (Join-Path $chat 'runtime') -Force | Out-Null
foreach($file in @('sitecustomize.py','chatbot_metering.py','cosmos_budget.py','approved_environment.py','cloud_entrypoint.py','cloud_check.py')) {
    Copy-Item (Join-Path $PSScriptRoot "chatbot_runtime\$file") (Join-Path $chat "runtime\$file")
}
Copy-Item (Join-Path $PSScriptRoot 'chatbot_runtime\Dockerfile.cloud-chat') (Join-Path $chat 'Dockerfile')
foreach($component in @('chat','scenario')) {
    $destination = Join-Path $stage "$component-ui"
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Copy-SourceTree (Join-Path $runtime "$component-frontend\dist") (Join-Path $destination 'dist') @()
    foreach($file in @('nginx.conf','startup.sh')) {
        Copy-Item (Join-Path $repo "$component-app\frontend\$file") (Join-Path $destination $file)
    }
    Copy-Item (Join-Path $PSScriptRoot 'chatbot_runtime\Dockerfile.native-frontend-runtime') (Join-Path $destination 'Dockerfile')
}
$bad = @(Get-ChildItem -LiteralPath $stage -Recurse -Force | Where-Object {
    $_.Name -like '.env*' -or $_.Name -in @('.azure','.git','.docker','secrets.json') -or $_.Extension -in @('.key','.pfx','.pem')
})
if($bad.Count -gt 0) { throw 'Forbidden credential/configuration material found in the staged image context.' }
[pscustomobject]@{stage=$stage;files=@(Get-ChildItem $stage -Recurse -File).Count;secretsExcluded=$true}|ConvertTo-Json
