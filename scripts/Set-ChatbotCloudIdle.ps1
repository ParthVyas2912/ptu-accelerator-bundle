[CmdletBinding()]
param(
    [ValidateSet('chat-api','scenario-api','chat-ui','scenario-ui')]
    [string[]]$Service = @('chat-api','scenario-api','chat-ui','scenario-ui')
)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path $PSScriptRoot -Parent
foreach($name in $Service) {
    $raw = & (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
        'containerapp','show','--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
        '--resource-group','accel-chatbot-eval-0911','--name',"chatbot-$name",
        '--output','json','--only-show-errors'
    )
    if($LASTEXITCODE -ne 0){throw "Could not inspect chatbot-$name."}
    $app = ($raw -join "`n") | ConvertFrom-Json
    # The CLI update path was observed blanking HTTP scaler metadata. Reapply
    # the checked-in template instead, preserving ingress, identity and rules.
    & (Join-Path $PSScriptRoot 'Deploy-ChatbotCloud.ps1') -Service $name `
        -Image $app.properties.template.containers[0].image -MinimumReplicas 0
    if($LASTEXITCODE -ne 0){throw "Could not return chatbot-$name to scale-to-zero."}
}
# Does not delete/deactivate resources or reset the Cosmos-backed model budget.
