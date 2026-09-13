[CmdletBinding()]
param(
    [switch]$Approved,
    [switch]$StorageOnly,
    [ValidateSet('cosmos-ptu-modernize-0911','cosmos-ptu-modernize-eus20911')]
    [string]$CosmosAccount = 'cosmos-ptu-modernize-eus20911'
)
$ErrorActionPreference = 'Stop'
if (-not $Approved) { throw 'Explicit Modernize persistence/RBAC approval is required.' }
$B = Split-Path $PSScriptRoot -Parent
$guard = Join-Path $B 'Invoke-LabAz.ps1'
$sub = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$rg = 'rg-ptu-modernize-demo'
$storage = 'stptumodernize0911pv'
$cosmos = $CosmosAccount
$expectedRegion = if ($cosmos -eq 'cosmos-ptu-modernize-eus20911') { 'eastus2' } else { 'canadacentral' }
function Invoke-ModernizeAz([string[]]$Arguments) {
    & $guard -AzArguments ($Arguments + @('--subscription', $sub, '-o', 'json'))
}
$identity = & $guard -AzArguments @('ad','signed-in-user','show','--query','{id:id}','-o','json')
$principal = ($identity | ConvertFrom-Json).id
if (-not $principal) { throw 'Cannot determine current Entra user object ID.' }
Invoke-ModernizeAz @('storage','container-rm','create','--storage-account',$storage,
    '--resource-group',$rg,'--name','ptu-modernize-files','--public-access','off',
    '--query','{id:id,name:name}') | Out-Host
$storageScope = "/subscriptions/$sub/resourceGroups/$rg/providers/Microsoft.Storage/storageAccounts/$storage/blobServices/default/containers/ptu-modernize-files"
$blobRole = Invoke-ModernizeAz @('role','assignment','list','--scope',$storageScope,
    '--query',"[?principalId=='$principal' && ends_with(roleDefinitionId,'ba92f5b4-2d11-453d-a403-e96b0029c9fe')] | [0].{id:id,roleDefinitionId:roleDefinitionId,scope:scope}")
if (-not ($blobRole | ConvertFrom-Json).id) {
    $blobRole = Invoke-ModernizeAz @('role','assignment','create','--assignee-object-id',$principal,
        '--assignee-principal-type','User','--role','ba92f5b4-2d11-453d-a403-e96b0029c9fe',
        '--scope',$storageScope,'--query','{id:id,roleDefinitionId:roleDefinitionId,scope:scope}')
}
if ($StorageOnly) {
    [System.IO.File]::WriteAllText((Join-Path $B 'evidence\modernize\storage-access.json'),
        (@{ app='Modernize Your Code'; storageAccount=$storage; blobRole=($blobRole | ConvertFrom-Json);
            credentialsPersisted=$false; approval='Parent explicit approval 2026-09-11T19:58:57-04:00' } | ConvertTo-Json -Depth 10))
    'Modernize approved private Blob container and container-scoped RBAC configured.'
    return
}
$account = Invoke-ModernizeAz @('cosmosdb','show','-g',$rg,'-n',$cosmos,
    '--query','{id:id,capabilities:capabilities,disableLocalAuth:disableLocalAuth,locations:locations[].locationName}')
$accountInfo = $account | ConvertFrom-Json
if ('EnableServerless' -notin $accountInfo.capabilities.name) { throw 'Expected approved Serverless Cosmos account.' }
if ($accountInfo.locations.Count -ne 1 -or
    ($accountInfo.locations[0]).Replace(' ','').ToLowerInvariant() -ne $expectedRegion) {
    throw 'Unexpected Cosmos region topology.'
}
if (-not $accountInfo.disableLocalAuth) { throw 'Cosmos local authentication must be disabled.' }

Invoke-ModernizeAz @('cosmosdb','sql','database','create','--account-name',$cosmos,
    '--resource-group',$rg,'--name','ptu-modernize','--query','{id:id,name:name}') | Out-Host
foreach ($item in @(
    @('ptu-modernize-batches','/batch_id'),
    @('ptu-modernize-files','/file_id'),
    @('ptu-modernize-logs','/log_id')
)) {
    Invoke-ModernizeAz @('cosmosdb','sql','container','create','--account-name',$cosmos,
        '--resource-group',$rg,'--database-name','ptu-modernize','--name',$item[0],
        '--partition-key-path',$item[1],'--query','{id:id,name:name,partitionKey:resource.partitionKey}') | Out-Host
}
$cosmosRole = Invoke-ModernizeAz @('cosmosdb','sql','role','assignment','create',
    '--account-name',$cosmos,'--resource-group',$rg,'--principal-id',$principal,
    '--role-definition-id','00000000-0000-0000-0000-000000000002','--scope','/dbs/ptu-modernize',
    '--query','{id:id,roleDefinitionId:roleDefinitionId,scope:scope}')
$evidence = @{
    app = 'Modernize Your Code'
    subscription = $sub
    resourceGroup = $rg
    storageAccount = $storage
    cosmosAccount = $cosmos
    cosmosDatabase = 'ptu-modernize'
    blobRole = ($blobRole | ConvertFrom-Json)
    cosmosRole = ($cosmosRole | ConvertFrom-Json)
    approval = 'Parent explicit approval received 2026-09-11T19:58:57-04:00'
    fallbackApproval = 'Parent East US 2 fallback approval 2026-09-11T20:11:19-04:00'
    residencyLimitation = 'US data persistence is for synthetic MCAPS tests only, not DND residency approval.'
    credentialsPersisted = $false
}
[System.IO.File]::WriteAllText((Join-Path $B 'evidence\modernize\persistence.json'),
    ($evidence | ConvertTo-Json -Depth 12))
'Modernize approved persistence and database/container-scoped RBAC configured.'
