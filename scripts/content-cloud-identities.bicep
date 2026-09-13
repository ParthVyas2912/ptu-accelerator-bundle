targetScope = 'resourceGroup'
var services = ['api', 'processor', 'workflow', 'web']
resource identities 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = [for service in services: {
  name: 'id-ptu-content-${service}'
  location: 'eastus2'
  tags: { workload: 'accelerator-eval', owner: 'parth', environment: 'mcaps-nonprod', accelerator: 'content', protected: 'false' }
}]
resource storage 'Microsoft.Storage/storageAccounts@2025-01-01' existing = {
  name: 'stptuvcontent260911'
}
resource config 'Microsoft.AppConfiguration/configurationStores@2024-05-01' existing = {
  name: 'appcs-ptuv-content-260911'
}
resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2025-04-15' existing = {
  name: 'cosmos-ptuv-content-260911'
}
resource ai 'Microsoft.CognitiveServices/accounts@2025-12-01' existing = {
  name: 'aif-ptuv-content-260911'
}
// This action returns the approved Mongo credential into runtime memory only.
// No listKeys permission, database write, throughput change or network action.
resource mongoRuntimeReader 'Microsoft.Authorization/roleDefinitions@2022-04-01' = {
  name: guid(resourceGroup().id, 'content-mongo-runtime-reader')
  properties: {
    roleName: 'PTU Content Mongo Runtime Connection Reader'
    description: 'Read only Content Mongo connection strings into runtime process memory.'
    type: 'CustomRole'
    assignableScopes: [resourceGroup().id]
    permissions: [{
      actions: [
        'Microsoft.DocumentDB/databaseAccounts/read'
        'Microsoft.DocumentDB/databaseAccounts/listConnectionStrings/action'
      ]
      notActions: []
      dataActions: []
      notDataActions: []
    }]
  }
}
resource mongoRead 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for i in range(0, 3): {
  scope: cosmos
  name: guid(cosmos.id, identities[i].id, mongoRuntimeReader.id)
  properties: {
    principalId: identities[i].properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: mongoRuntimeReader.id
  }
}]
resource configRead 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for i in range(0, 3): {
  scope: config
  name: guid(config.id, identities[i].id, '516239f1-63e1-4d78-a4de-a74fb236a071')
  properties: {
    principalId: identities[i].properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '516239f1-63e1-4d78-a4de-a74fb236a071')
  }
}]
resource blobAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for i in range(0, 3): {
  scope: storage
  name: guid(storage.id, identities[i].id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    principalId: identities[i].properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}]
resource queueAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for i in range(0, 3): {
  scope: storage
  name: guid(storage.id, identities[i].id, '974c5e8b-45b9-4653-ba55-5f855dd0fb88')
  properties: {
    principalId: identities[i].properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')
  }
}]
resource modelAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for i in range(1, 2): {
  scope: ai
  name: guid(ai.id, identities[i].id, '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
  properties: {
    principalId: identities[i].properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
  }
}]
resource cuAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: ai
  name: guid(ai.id, identities[1].id, 'a97b65f3-24c7-4388-baec-2e87135dc908')
  properties: {
    principalId: identities[1].properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
  }
}
module sharedRegistryPull 'content-cloud-acrpull.bicep' = {
  scope: resourceGroup('rg-ptu-bundle-platform')
  name: 'ptu-content-acrpull'
  params: { principalIds: [for i in range(0, 4): identities[i].properties.principalId] }
}
output apps array = [for i in range(0, 4): {
  service: services[i]
  identityId: identities[i].id
  clientId: identities[i].properties.clientId
  principalId: identities[i].properties.principalId
}]
