[CmdletBinding()]
param(
    [ValidateSet('backend', 'frontend', 'scenario-backend', 'scenario-frontend')]
    [string]$Component = 'backend',
    [switch]$EnableApprovedCloud
)
$ErrorActionPreference = 'Stop'
if($EnableApprovedCloud) {
    throw 'Chatbot allowance is closed. The old cloud-enable flag is not a new operator allowance.'
}
$desktop = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$repo = Join-Path $desktop 'repo\customer-chatbot-solution-accelerator'
$runtime = Join-Path $env:LOCALAPPDATA 'ptu-chatbot'
$env:PYTHONPATH = Join-Path $PSScriptRoot 'chatbot_runtime'
$env:CHATBOT_METERING = '1'
$env:CHATBOT_USAGE_DB = Join-Path $runtime 'usage.sqlite'
$env:PYTHON_DOTENV_DISABLED = '1'
$venv = if ($Component -eq 'scenario-backend') { 'scenario-venv' } else { 'chat-venv' }
$arguments = @((Join-Path $PSScriptRoot 'chatbot_runtime\local_app.py'), $Component, '--repo', $repo)
if ($EnableApprovedCloud) { $arguments += '--enable-approved-cloud' }
# Intentionally foreground. Use separate attached terminal/tool sessions.
# Does not create Azure resources, reset the budget, or launch detached children.
& (Join-Path $runtime "$venv\Scripts\python.exe") @arguments
exit $LASTEXITCODE
