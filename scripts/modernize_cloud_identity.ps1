$ErrorActionPreference = 'Stop'
$B = Split-Path $PSScriptRoot -Parent
$guard = Join-Path $B 'Invoke-LabAz.ps1'
$sub = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$rg = 'rg-ptu-modernize-demo'
$platform = Get-Content (Join-Path $B 'evidence\preflight\lab-platform-outputs.json') -Raw | ConvertFrom-Json
function LabAz([string[]]$Arguments) {
    $output = & $guard -AzArguments ($Arguments + @('--subscription',$sub,'-o','json'))
    if ($LASTEXITCODE -ne 0) { throw 'Guarded Modernize cloud identity operation failed.' }
    return ($output | ConvertFrom-Json)
}
$backend = LabAz @('identity','create','--resource-group',$rg,'--name','id-ptu-modernize','--location','eastus2')
# Frontend receives image-pull permission only, not model or data permissions.
$frontend = LabAz @('identity','create','--resource-group',$rg,'--name','id-ptu-modernize-ui','--location','eastus2')
$blobScope="/subscriptions/$sub/resourceGroups/$rg/providers/Microsoft.Storage/storageAccounts/stptumodernize0911pv/blobServices/default/containers/ptu-modernize-files"
$foundryScope="/subscriptions/$sub/resourceGroups/rg-edc-foundry-hack/providers/Microsoft.CognitiveServices/accounts/edcfoundryhack01"
$grants = @(
    @{principal=$backend.principalId;role='ba92f5b4-2d11-453d-a403-e96b0029c9fe';scope=$blobScope},
    @{principal=$backend.principalId;role='53ca6127-db72-4b80-b1b0-d745d6d5456d';scope="$foundryScope/projects/edc-hack-proj"},
    @{principal=$backend.principalId;role='5e0bd9bd-7b93-4f28-af87-19fc36ad61bd';scope=$foundryScope},
    @{principal=$backend.principalId;role='7f951dda-4ed3-4680-a7ca-43fe172d538d';scope=$platform.registryId.value},
    @{principal=$frontend.principalId;role='7f951dda-4ed3-4680-a7ca-43fe172d538d';scope=$platform.registryId.value}
)
$assignments=@()
foreach ($g in $grants) {
    $existing = @(LabAz @('role','assignment','list','--scope',$g.scope))
    $match = @($existing | Where-Object { $_.principalId -eq $g.principal -and $_.roleDefinitionId.EndsWith($g.role) })
    if ($match.Count) { $assignment=$match[0] }
    else {
        $assignment=LabAz @('role','assignment','create','--assignee-object-id',$g.principal,
            '--assignee-principal-type','ServicePrincipal','--role',$g.role,'--scope',$g.scope)
    }
    $assignments += @{id=$assignment.id; principalId=$g.principal; role=$g.role; scope=$g.scope}
}
$cosmosRoles = @(LabAz @('cosmosdb','sql','role','assignment','list','--account-name','cosmos-ptu-modernize-eus20911','--resource-group',$rg))
$cosmosRole = @($cosmosRoles | Where-Object { $_.principalId -eq $backend.principalId -and $_.scope.EndsWith('/dbs/ptu-modernize') })
if ($cosmosRole.Count) { $cosmosRole=$cosmosRole[0] }
else {
    $cosmosRole=LabAz @('cosmosdb','sql','role','assignment','create','--account-name','cosmos-ptu-modernize-eus20911',
        '--resource-group',$rg,'--principal-id',$backend.principalId,
        '--role-definition-id','00000000-0000-0000-0000-000000000002','--scope','/dbs/ptu-modernize')
}
$result=@{app='Modernize Your Code'; backendIdentity=$backend; frontendPullOnlyIdentity=$frontend;
    assignments=$assignments; cosmosRole=$cosmosRole;
    approval='Parent shared-platform ready / scoped MI and AcrPull approval 2026-09-11T20:54:31-04:00'}
[System.IO.File]::WriteAllText((Join-Path $B 'evidence\modernize\cloud-identities.json'),($result | ConvertTo-Json -Depth 15))
'Modernize backend scoped roles and frontend pull-only identity configured.'
