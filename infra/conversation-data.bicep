targetScope = 'resourceGroup'

param location string = 'canadacentral'
param runtimePrincipalId string = 'b0c36c36-5b9f-4efa-9f01-0e19fb97aa25'
param sqlAdminPrincipalId string = '87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed'
param sqlAdminName string = 'CKM lab administrator'
@allowed(['User', 'Application'])
param sqlAdminType string = 'User'
param tags object = {
  workload: 'accelerator-eval'
  owner: 'parth'
  environment: 'mcaps-nonprod'
  accelerator: 'conversation'
  protected: 'false'
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stptuconv7d804f70'
  location: location
  tags: tags
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    publicNetworkAccess: 'Disabled'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    defaultToOAuthAuthentication: true
    accessTier: 'Hot'
    networkAcls: { defaultAction: 'Deny', bypass: 'None' }
  }
}

resource search 'Microsoft.Search/searchServices@2025-05-01' = {
  name: 'srch-ptu-conversation-7d804f70'
  location: location
  tags: tags
  sku: { name: 'basic' }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'Default'
    publicNetworkAccess: 'disabled'
    disableLocalAuth: true
    semanticSearch: 'free'
  }
}

resource server 'Microsoft.Sql/servers@2025-01-01' = {
  name: 'sql-ptu-conversation-7d804f70'
  location: location
  tags: tags
  properties: {
    version: '12.0'
    publicNetworkAccess: 'Disabled'
    minimalTlsVersion: '1.2'
    administrators: {
      administratorType: 'ActiveDirectory'
      principalType: sqlAdminType
      login: sqlAdminName
      sid: sqlAdminPrincipalId
      tenantId: subscription().tenantId
      azureADOnlyAuthentication: true
    }
  }
}

resource database 'Microsoft.Sql/servers/databases@2025-01-01' = {
  parent: server
  name: 'ptu-conversation'
  location: location
  tags: tags
  sku: {
    name: 'GP_S_Gen5'
    tier: 'GeneralPurpose'
    family: 'Gen5'
    capacity: 2
  }
  properties: {
    autoPauseDelay: 60
    minCapacity: json('0.5')
    maxSizeBytes: 34359738368
    zoneRedundant: false
    readScale: 'Disabled'
    requestedBackupStorageRedundancy: 'Local'
  }
}

resource blobRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, runtimePrincipalId, 'blob-data-contributor')
  scope: storage
  properties: {
    principalId: runtimePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}

resource searchServiceRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(search.id, runtimePrincipalId, 'search-service-contributor')
  scope: search
  properties: {
    principalId: runtimePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
  }
}

resource searchDataRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(search.id, runtimePrincipalId, 'search-index-data-contributor')
  scope: search
  properties: {
    principalId: runtimePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
  }
}

output storageId string = storage.id
output searchId string = search.id
output sqlServerId string = server.id
output databaseId string = database.id
