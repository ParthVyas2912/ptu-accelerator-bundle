targetScope = 'resourceGroup'

resource search 'Microsoft.Search/searchServices@2025-05-01' existing = {
  name: 'srch-ccptu1feb0911'
}
resource foundry 'Microsoft.CognitiveServices/accounts@2025-12-01' existing = {
  name: 'aif-ccptu1feb0911'
}
resource project 'Microsoft.CognitiveServices/accounts/projects@2025-12-01' existing = {
  parent: foundry
  name: 'proj-ccptu1feb0911'
}
resource chat 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: 'mi-chatbot-chat-api'
}
resource scenario 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: 'mi-chatbot-scenario-api'
}

var reader = '1407120a-92aa-4202-b7e9-c0e197c71c8f'
var dataContributor = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
var serviceContributor = '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
var openaiUser = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
var principalIds = [
  project.identity.principalId
  chat.properties.principalId
  scenario.properties.principalId
  foundry.identity.principalId
]
var grants = [
  { identityId: project.id, principalIndex: 0, role: reader }
  { identityId: project.id, principalIndex: 0, role: serviceContributor }
  { identityId: chat.id, principalIndex: 1, role: dataContributor }
  { identityId: chat.id, principalIndex: 1, role: serviceContributor }
  { identityId: scenario.id, principalIndex: 2, role: reader }
  // Current Foundry Search-tool guidance also requires the account identity.
  { identityId: foundry.id, principalIndex: 3, role: dataContributor }
  { identityId: foundry.id, principalIndex: 3, role: serviceContributor }
]
resource searchRoles 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for grant in grants: {
  name: guid(search.id, grant.identityId, grant.role)
  scope: search
  properties: {
    principalId: principalIds[grant.principalIndex]
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', grant.role)
  }
}]
resource vectorizerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundry.id, search.id, openaiUser)
  scope: foundry
  properties: {
    principalId: search.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', openaiUser)
  }
}
module connection './bicep/modules/ai/ai-foundry-connection.bicep' = {
  name: 'ptu-chatbot-search-connection'
  params: {
    aiServicesAccountName: foundry.name
    projectName: project.name
    solutionName: 'ccptu1feb0911'
    connectionName: 'aifp-srch-connection-ccptu1feb0911'
    category: 'CognitiveSearch'
    target: 'https://${search.name}.search.windows.net'
    authType: 'AAD'
    metadata: {
      ApiType: 'Azure'
      ResourceId: search.id
    }
  }
}
output connectionId string = connection.outputs.connectionId
output projectPrincipalId string = project.identity.principalId
