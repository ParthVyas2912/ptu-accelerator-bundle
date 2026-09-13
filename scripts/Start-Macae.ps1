[CmdletBinding()]
param([ValidateSet('backend','mcp')][string]$Component = 'backend')
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$contract = Get-Content (Join-Path $b 'deployment-contract.json') -Raw | ConvertFrom-Json
$env:MACAE_REPO = Join-Path $contract.repoRoot 'Multi-Agent-Custom-Automation-Engine-Solution-Accelerator'
$env:MACAE_STATE_DIR = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-state'
if ($Component -eq 'backend' -and (Test-Path (Join-Path $env:MACAE_STATE_DIR 'cloud-budget-active'))) {
    throw 'Cloud evaluation ledger is active. Do not run a separate local inference budget; use the cloud runbook.'
}
$env:MACAE_EVIDENCE_DIR = Join-Path $b 'evidence\macae'
$env:MACAE_FRONTEND_DIR = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-ui-source\src\App'
$env:APP_ENV = 'dev'
$env:AZURE_TENANT_ID = 'a600acd0-3028-4689-8402-3b471d7d924d'
$env:AZURE_AI_SUBSCRIPTION_ID = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$env:AZURE_AI_RESOURCE_GROUP = 'rg-ptu-macae-demo'
$env:AZURE_AI_PROJECT_NAME = 'ptu-macae-project'
$env:AZURE_OPENAI_ENDPOINT = 'https://ptumacae7d804f70.openai.azure.com/'
$env:AZURE_AI_PROJECT_ENDPOINT = 'https://ptumacae7d804f70.services.ai.azure.com/api/projects/ptu-macae-project'
$env:AZURE_AI_AGENT_ENDPOINT = $env:AZURE_AI_PROJECT_ENDPOINT
$env:AZURE_OPENAI_DEPLOYMENT_NAME = 'gpt-5.4-mini'
$env:AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME = 'gpt-5.4-mini'
$env:AZURE_OPENAI_RAI_DEPLOYMENT_NAME = 'gpt-5.4'
$env:AZURE_OPENAI_API_VERSION = '2024-12-01-preview'
$env:ORCHESTRATOR_MODEL_NAME = 'gpt-5.4-mini'
$env:SUPPORTED_MODELS = '["gpt-5.4-mini","gpt-5.4"]'
$env:COSMOSDB_ENDPOINT = 'https://ptu-macae-7d804f70-cosmos.documents.azure.com:443/'
$env:COSMOSDB_DATABASE = 'ptu-macae'
$env:COSMOSDB_CONTAINER = 'memory'
$env:MCP_SERVER_ENDPOINT = 'http://127.0.0.1:5111/mcp'
$env:MCP_SERVER_NAME = 'MacaeMcpServer'
$env:FRONTEND_SITE_NAME = 'http://127.0.0.1:8111'
$env:BACKEND_API_URL = 'http://127.0.0.1:8111'
$env:BACKEND_URL = 'http://127.0.0.1:8111' # Native MCP ask_user callback on subsequent starts.
$env:PROXY_API_REQUESTS = 'false'
$env:AUTH_ENABLED = 'false' # Native dev UI only; never bind beyond loopback.
$env:HOST = '127.0.0.1'
$env:FASTMCP_ENABLE_TELEMETRY = 'false'
$env:AZURE_BASIC_LOGGING_LEVEL = 'WARNING'
$env:AZURE_PACKAGE_LOGGING_LEVEL = 'WARNING'
$env:AZURE_TOKEN_CREDENTIALS = 'AzureCliCredential'
# No secrets or credential files are generated. Existing `az login` is required.
# Run one service per terminal. No detached background process is created.
if ($Component -eq 'backend') {
    $python = Join-Path $env:MACAE_REPO 'src\backend\.venv\Scripts\python.exe'
} else {
    $python = Join-Path $env:LOCALAPPDATA 'ptu-eval\macae-mcp\Scripts\python.exe'
}
& $python (Join-Path $PSScriptRoot 'macae_run.py') $Component
exit $LASTEXITCODE
