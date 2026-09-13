[CmdletBinding()]
param([switch]$Approved)
$ErrorActionPreference = 'Stop'
if (-not $Approved) { throw 'Parent-approved native persistence envelope required.' }
$B = Split-Path $PSScriptRoot -Parent
if (Test-Path (Join-Path $B 'evidence\modernize\network-policy-blocker.json')) {
    throw 'Governance enforces disabled public endpoints. Do not retry this update or bypass policy; obtain an approved connectivity design.'
}
$guard = Join-Path $B 'Invoke-LabAz.ps1'
$sub = '1feb53b2-854a-4ea7-b5a6-709b7d804f70'
$rg = 'rg-ptu-modernize-demo'
# Exact source IP reported by Cosmos in the real native application's 403.
# This is not an all-networks or Azure-services bypass.
$ip = '20.236.11.102'
& $guard -AzArguments @('cosmosdb','update','--name','cosmos-ptu-modernize-eus20911',
    '--resource-group',$rg,'--subscription',$sub,'--public-network-access','Enabled',
    '--ip-range-filter',$ip,'--query','{id:id,publicNetworkAccess:publicNetworkAccess,ipRules:ipRules,disableLocalAuth:disableLocalAuth}','-o','json')
$cosmosExit = $LASTEXITCODE
if ($cosmosExit -ne 0) { throw "Cosmos scoped network update failed: $cosmosExit" }
# Keep public access disabled until the exact allowlist and default-deny exist.
& $guard -AzArguments @('storage','account','network-rule','add','--account-name','stptumodernize0911pv',
    '--resource-group',$rg,'--subscription',$sub,'--ip-address',$ip,'-o','none')
if ($LASTEXITCODE -ne 0) { throw 'Storage IP allowlist update failed.' }
& $guard -AzArguments @('storage','account','update','--name','stptumodernize0911pv',
    '--resource-group',$rg,'--subscription',$sub,'--default-action','Deny','--bypass','None',
    '--public-network-access','Enabled','--query',
    '{id:id,publicNetworkAccess:publicNetworkAccess,networkRuleSet:networkRuleSet,allowSharedKeyAccess:allowSharedKeyAccess,allowBlobPublicAccess:allowBlobPublicAccess}','-o','json')
if ($LASTEXITCODE -ne 0) { throw 'Storage scoped network update failed.' }
[System.IO.File]::WriteAllText((Join-Path $B 'evidence\modernize\network-configuration.json'),
    (@{app='Modernize Your Code'; sourceIp=$ip; scope='Only approved new Cosmos EUS2 and Storage accounts';
       authentication='Entra only, local/shared-key and anonymous Blob access remain disabled';
       requestedIngress='Exact observed lab egress IPv4 only; no service bypass';
       actualIngress='Must verify returned publicNetworkAccess; successful ARM update does not prove connectivity';
       approval='Required routine setup within parent-approved native persistence envelope';
       sharedFoundryNetworkChanged=$false } | ConvertTo-Json))
