[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('Cosmos','Products','Policies','Agents')][string]$Stage,
    [switch]$ConfirmModelCalls
)
$ErrorActionPreference = 'Stop'
throw 'Chatbot allowance is closed. Seeding requires a new explicit operator allowance.'
if ($Stage -in @('Products','Policies') -and -not $ConfirmModelCalls) {
    throw 'Embedding ingestion consumes the shared 12-unit budget; explicitly pass -ConfirmModelCalls.'
}
$desktop = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$repo = Join-Path $desktop 'repo\customer-chatbot-solution-accelerator'
$runtime = Join-Path $env:LOCALAPPDATA 'ptu-chatbot'
$env:APP_ENV = 'dev'
$env:AZURE_TOKEN_CREDENTIALS = 'AzureCliCredential'
$env:PYTHON_DOTENV_DISABLED = '1'
$env:CHATBOT_METERING = '1'
$env:CHATBOT_USAGE_DB = Join-Path $runtime 'usage.sqlite'
$env:PYTHONPATH = Join-Path $PSScriptRoot 'chatbot_runtime'
$env:AZURE_COSMOSDB_DATABASE = 'ecommerce_db'
foreach ($name in @('AZURE_OPENAI_API_KEY','AZURE_VOICELIVE_API_KEY','AZURE_CLIENT_SECRET')) {
    Remove-Item "Env:$name" -ErrorAction SilentlyContinue
}
$python = Join-Path $runtime 'seed-venv\Scripts\python.exe'
if ($Stage -eq 'Cosmos') {
    $script = Join-Path $repo 'infra\scripts\post-provision\data_scripts\03_write_products_to_cosmos.py'
    $arguments = @('--cosmosdb_account','cosmos-ccptu1feb0911','--scenario','ecommerce')
} elseif ($Stage -eq 'Agents') {
    $python = Join-Path $runtime 'chat-venv\Scripts\python.exe'
    $script = Join-Path $repo 'infra\scripts\post-provision\agent_scripts\01_create_agents.py'
    $arguments = @('--ai_project_endpoint','https://aif-ccptu1feb0911.services.ai.azure.com/api/projects/proj-ccptu1feb0911',
        '--solution_name','eval','--gpt_model_name','gpt-5.4-mini',
        '--ai_search_endpoint','https://srch-ccptu1feb0911.search.windows.net','--scenario','ecommerce')
} else {
    $file = if($Stage -eq 'Products'){'01_create_products_search_index.py'}else{'02_create_policies_search_index.py'}
    $script = Join-Path $repo "infra\scripts\post-provision\data_scripts\$file"
    $arguments = @('--ai_search_endpoint','https://srch-ccptu1feb0911.search.windows.net',
        '--azure_openai_endpoint','https://aif-ccptu1feb0911.openai.azure.com/',
        '--embedding_model_name','text-embedding-3-small','--scenario','ecommerce')
}
& $python $script @arguments
exit $LASTEXITCODE
