// Approved isolated evaluation composition of the accelerator's native modules.
// No shared-account reuse, hosted compute, ACR, realtime model, or PTU.
targetScope = 'resourceGroup'

param location string = 'eastus2'
param solutionName string = 'ccptu1feb0911'
param labPrincipalId string = '87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed'

var tags = {
  workload: 'accelerator-eval'
  owner: 'parth'
  environment: 'mcaps-nonprod'
  accelerator: 'chatbot'
  protected: 'false'
}

module foundry './bicep/modules/ai/ai-foundry-project.bicep' = {
  name: 'ptu-chatbot-foundry'
  params: {
    solutionName: solutionName
    location: location
    tags: tags
    skuName: 'S0'
    disableLocalAuth: true
  }
}

module textModel './bicep/modules/ai/ai-foundry-model-deployment.bicep' = {
  name: 'ptu-chatbot-text'
  params: {
    aiServicesAccountName: foundry.outputs.name
    deploymentName: 'gpt-5.4-mini'
    modelName: 'gpt-5.4-mini'
    modelVersion: '2026-03-17'
    skuName: 'GlobalStandard'
    skuCapacity: 10
  }
}

module embeddingModel './bicep/modules/ai/ai-foundry-model-deployment.bicep' = {
  name: 'ptu-chatbot-embedding'
  dependsOn: [textModel]
  params: {
    aiServicesAccountName: foundry.outputs.name
    deploymentName: 'text-embedding-3-small'
    modelName: 'text-embedding-3-small'
    modelVersion: '1'
    skuName: 'GlobalStandard'
    skuCapacity: 10
  }
}

module search './bicep/modules/ai/ai-search.bicep' = {
  name: 'ptu-chatbot-search'
  params: {
    solutionName: solutionName
    location: location
    tags: tags
    skuName: 'basic'
    replicaCount: 1
    partitionCount: 1
    semanticSearch: 'free'
    disableLocalAuth: true
  }
}

module cosmos './bicep/modules/data/cosmos-db-nosql.bicep' = {
  name: 'ptu-chatbot-cosmos'
  params: {
    solutionName: solutionName
    location: location
    tags: tags
    databaseName: 'ecommerce_db'
    containers: [
      { name: 'carts', partitionKeyPath: '/user_id' }
      { name: 'chat_sessions', partitionKeyPath: '/user_id' }
      { name: 'products', partitionKeyPath: '/productId' }
      { name: 'transactions', partitionKeyPath: '/user_id' }
      { name: 'users', partitionKeyPath: '/email' }
    ]
  }
}

module connection './bicep/modules/ai/ai-foundry-connection.bicep' = {
  name: 'ptu-chatbot-search-connection'
  params: {
    solutionName: solutionName
    aiServicesAccountName: foundry.outputs.name
    projectName: foundry.outputs.projectName
    connectionName: 'ptu-chatbot-search-connection'
    category: 'CognitiveSearch'
    target: search.outputs.endpoint
    authType: 'AAD'
    isDefault: false
    metadata: {
      ApiType: 'Azure'
      ResourceId: search.outputs.resourceId
    }
  }
}

module roles './bicep/modules/identity/role-assignments.bicep' = {
  name: 'ptu-chatbot-native-roles'
  params: {
    solutionName: solutionName
    aiFoundryResourceId: foundry.outputs.resourceId
    aiProjectPrincipalId: foundry.outputs.projectIdentityPrincipalId
    aiSearchResourceId: search.outputs.resourceId
    aiSearchPrincipalId: search.outputs.identityPrincipalId
    cosmosDbAccountName: cosmos.outputs.name
    deployerPrincipalId: labPrincipalId
    appServicePrincipalIds: {
      chatBackendApp: ''
      chatFrontendApp: ''
      scenarioBackendApp: ''
      scenarioFrontendApp: ''
    }
  }
}

resource aiAccount 'Microsoft.CognitiveServices/accounts@2025-12-01' existing = {
  name: 'aif-${solutionName}'
}
resource localEmbeddingPermission 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiAccount.id, labPrincipalId, '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
  scope: aiAccount
  dependsOn: [foundry]
  properties: {
    principalId: labPrincipalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
  }
}

output configuration object = {
  AZURE_FOUNDRY_ENDPOINT: foundry.outputs.projectEndpoint
  AZURE_OPENAI_ENDPOINT: foundry.outputs.endpoint
  AZURE_OPENAI_DEPLOYMENT_NAME: 'gpt-5.4-mini'
  AZURE_AI_SEARCH_ENDPOINT: search.outputs.endpoint
  AZURE_SEARCH_ENDPOINT: search.outputs.endpoint
  COSMOS_DB_ENDPOINT: cosmos.outputs.endpoint
  COSMOS_DB_DATABASE_NAME: 'ecommerce_db'
}
output resourceIds object = {
  foundry: foundry.outputs.resourceId
  project: foundry.outputs.projectResourceId
  search: search.outputs.resourceId
  cosmos: cosmos.outputs.resourceId
}
