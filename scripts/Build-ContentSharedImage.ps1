[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('api','processor','workflow','web')]
    [string]$Service,
    [switch]$PlatformReady
)
$ErrorActionPreference = 'Stop'
if (-not $PlatformReady) {
    throw 'Parent has not confirmed shared platform readiness. No build/upload was started.'
}
$bundle = Split-Path $PSScriptRoot -Parent
$manifest = Get-Content (Join-Path $bundle 'evidence\content\container-contexts.json') -Raw | ConvertFrom-Json
$context = $manifest.contexts.$Service
if (-not $context) { throw 'Prepared, inspected image context not found.' }
$tag = "content/official-${Service}:659eaa1"
# One selected image at a time. No azd hooks, no network relaxation, no ACR
# admin credentials, no source .env files, no latest tags, no automatic deletes.
& (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
    'acr','build','--registry','acrptubundle7d804f70',
    '--resource-group','rg-ptu-bundle-platform',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--image',$tag,'--file',(Join-Path $context.path 'Dockerfile'),'--platform','linux',
    '--timeout','1800','--no-logs',$context.path
)
'Official source image built. Do not deploy Python services without the runtime-only credential/shared-budget overlay.'
