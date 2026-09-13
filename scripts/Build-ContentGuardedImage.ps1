[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('api','processor','workflow')]
    [string]$Service
)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path $PSScriptRoot -Parent
$manifest = Get-Content (Join-Path $bundle 'evidence\content\cloud-overlays.json') -Raw | ConvertFrom-Json
$context = $manifest.contexts.$Service
& (Join-Path $bundle 'Invoke-LabAz.ps1') -AzArguments @(
    'acr','build','--registry','acrptubundle7d804f70',
    '--resource-group','rg-ptu-bundle-platform',
    '--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--image',"content/eval-${Service}:$($manifest.revision)",
    '--file',(Join-Path $context.path 'Dockerfile'),
    '--platform','linux','--timeout','900','--no-logs',$context.path
)
