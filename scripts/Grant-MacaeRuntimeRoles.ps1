[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$b = Split-Path $PSScriptRoot -Parent
$guard = Join-Path $b 'Invoke-LabAz.ps1'
$s = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$root = "/subscriptions/$s/resourceGroups/rg-ptu-macae-demo/providers"
$identity = (& $guard -AzArguments @('identity','show','--subscription',$s,'-g','rg-ptu-macae-demo','-n','id-ptu-macae','-o','json')) | ConvertFrom-Json
$principal = $identity.principalId
if (-not $principal -or $identity.id -notmatch '/resourcegroups/rg-ptu-macae-demo/') { throw 'Unexpected MACAE identity.' }
$roles = @(
    @{role='AcrPull';scope="/subscriptions/$s/resourceGroups/rg-ptu-bundle-platform/providers/Microsoft.ContainerRegistry/registries/acrptubundle7d804f70"},
    @{role='53ca6127-db72-4b80-b1b0-d745d6d5456d';scope="$root/Microsoft.CognitiveServices/accounts/ptumacae7d804f70/projects/ptu-macae-project"},
    @{role='5e0bd9bd-7b93-4f28-af87-19fc36ad61bd';scope="$root/Microsoft.CognitiveServices/accounts/ptumacae7d804f70"},
    @{role='Storage Blob Data Contributor';scope="$root/Microsoft.Storage/storageAccounts/ptumacae7d804f70st/blobServices/default/containers/ptu-macae-rfp"},
    @{role='Storage Blob Data Contributor';scope="$root/Microsoft.Storage/storageAccounts/ptumacae7d804f70st/blobServices/default/containers/ptu-macae-contract"},
    @{role='Search Service Contributor';scope="$root/Microsoft.Search/searchServices/ptu-macae-7d804f70-srch"},
    @{role='Search Index Data Contributor';scope="$root/Microsoft.Search/searchServices/ptu-macae-7d804f70-srch"}
)
$records = @()
foreach ($r in $roles) {
    $existing = @((& $guard -AzArguments @('role','assignment','list','--subscription',$s,'--scope',$r.scope,'--query',"[?principalId=='$principal']",'-o','json')) | ConvertFrom-Json)
    $match = @($existing | Where-Object { $_.roleDefinitionName -eq $r.role -or $_.roleDefinitionId.EndsWith('/'+$r.role) })
    if ($match.Count) {
        $assignment = $match[0]
    } else {
        $assignment = (& $guard -AzArguments @('role','assignment','create','--subscription',$s,'--assignee-object-id',$principal,'--assignee-principal-type','ServicePrincipal','--role',$r.role,'--scope',$r.scope,'-o','json')) | ConvertFrom-Json
    }
    $records += @{role=$r.role;scope=$r.scope;assignmentId=$assignment.id}
    Write-Output ("MACAE role ready: "+$r.role+" at "+$r.scope)
}
$cosmosRoleId = "$root/Microsoft.DocumentDB/databaseAccounts/ptu-macae-7d804f70-cosmos/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
$existingCosmos = @((& $guard -AzArguments @('cosmosdb','sql','role','assignment','list','--subscription',$s,'-g','rg-ptu-macae-demo','--account-name','ptu-macae-7d804f70-cosmos','--query',"[?principalId=='$principal']",'-o','json')) | ConvertFrom-Json)
if (-not $existingCosmos.Count) {
    $cosmos = (& $guard -AzArguments @('cosmosdb','sql','role','assignment','create','--subscription',$s,'-g','rg-ptu-macae-demo','--account-name','ptu-macae-7d804f70-cosmos','--principal-id',$principal,'--role-definition-id',$cosmosRoleId,'--scope','/dbs/ptu-macae','-o','json')) | ConvertFrom-Json
} else { $cosmos = $existingCosmos[0] }
$records += @{role='Cosmos DB Built-in Data Contributor';scope=$cosmos.scope;assignmentId=$cosmos.id}
$evidence = @{identity=$identity;assignments=$records;recordedAtUtc=[datetime]::UtcNow.ToString('o');purpose='Native runtime and bounded bootstrap only; own new data/model scopes plus parent ACR pull'}
[IO.File]::WriteAllText((Join-Path $b 'evidence\macae\runtime-identity.json'),($evidence|ConvertTo-Json -Depth 12))
