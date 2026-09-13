[CmdletBinding()]
param(
    [ValidateSet('readiness','cosmos','products','policies','agents','usage')]
    [string]$Stage = 'readiness',
    [switch]$ConfirmModelCalls
)
$ErrorActionPreference = 'Stop'
if($Stage -in @('products','policies','agents')) {
    throw 'Chatbot allowance is closed. Ingestion and agent setup require a new explicit operator allowance.'
}
if($Stage -in @('products','policies') -and -not $ConfirmModelCalls) {
    throw 'Embedding ingestion consumes the durable shared 12-unit budget; pass -ConfirmModelCalls deliberately.'
}
$bundle = Split-Path $PSScriptRoot -Parent
& (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
    'containerapp','exec',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--resource-group','accel-chatbot-eval-0911',
    '--name','chatbot-chat-api',
    '--command',"python /opt/chatbot-eval/runtime/cloud_check.py $Stage"
)
exit $LASTEXITCODE
