$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'Assert-ModernizeBudgetOpen.ps1')
$guard = Join-Path (Split-Path $PSScriptRoot -Parent) 'Invoke-LabAz.ps1'
$scope = @(
    '-g', 'rg-ptu-modernize-demo', '-n', 'ca-ptu-modernize-api',
    '--subscription', '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
)
$revision = & $guard -AzArguments (@('containerapp', 'show') + $scope + @(
    '--query', 'properties.latestRevisionName', '-o', 'tsv'
))
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($revision)) {
    throw 'Cannot determine the Modernize API revision; no activation attempted.'
}
& $guard -AzArguments (@('containerapp', 'revision', 'activate') + $scope + @(
    '--revision', $revision.Trim(), '-o', 'none'
))
if ($LASTEXITCODE -ne 0) { throw 'Modernize API revision activation failed.' }
& $guard -AzArguments (@('containerapp', 'update') + $scope + @(
    '--min-replicas', '1', '--max-replicas', '1', '-o', 'none'
))
if ($LASTEXITCODE -ne 0) { throw 'Modernize API replica configuration failed.' }
