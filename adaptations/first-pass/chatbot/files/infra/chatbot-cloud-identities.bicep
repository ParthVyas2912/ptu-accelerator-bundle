targetScope = 'resourceGroup'
var appNames = ['chatbot-chat-api', 'chatbot-scenario-api', 'chatbot-chat-ui', 'chatbot-scenario-ui']
resource identities 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = [for app in appNames: {
  name: 'mi-${app}'
  location: 'eastus2'
  tags: {
    workload: 'accelerator-eval'
    accelerator: 'chatbot'
    environment: 'mcaps-nonprod'
    owner: 'parth'
    protected: 'false'
  }
}]
module registryAccess './chatbot-registry-access.bicep' = {
  name: 'ptu-chatbot-registry-pull'
  scope: resourceGroup('rg-ptu-bundle-platform')
  params: {
    principalIds: [for (app, i) in appNames: identities[i].properties.principalId]
  }
}
resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2025-10-15' existing = {
  name: 'cosmos-ccptu1feb0911'
}
resource cosmosRoles 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2025-10-15' = [for i in range(0, 2): {
  parent: cosmos
  name: guid(cosmos.id, identities[i].id, 'native-data-contributor')
  properties: {
    principalId: identities[i].properties.principalId
    roleDefinitionId: '${cosmos.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002'
    scope: cosmos.id
  }
}]
resource foundry 'Microsoft.CognitiveServices/accounts@2025-12-01' existing = {
  name: 'aif-ccptu1feb0911'
}
// Native Foundry agent access and direct ingestion embeddings; no keys.
var modelRoleIds = ['53ca6127-db72-4b80-b1b0-d745d6d5456d', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd']
resource modelRoles 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for role in modelRoleIds: {
  name: guid(foundry.id, identities[0].id, role)
  scope: foundry
  properties: {
    principalId: identities[0].properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', role)
  }
}]
output appIdentities array = [for (app, i) in appNames: {
  appName: app
  id: identities[i].id
  principalId: identities[i].properties.principalId
  clientId: identities[i].properties.clientId
}]
