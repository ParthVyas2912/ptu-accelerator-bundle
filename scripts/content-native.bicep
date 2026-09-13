targetScope = 'resourceGroup'

@allowed(['eastus2'])
param location string = 'eastus2'
param principalId string = '87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed'
param clientIp string
var tags = {
  workload: 'accelerator-eval'
  owner: 'parth'
  environment: 'mcaps-nonprod'
  accelerator: 'content'
  protected: 'false'
}

resource storage 'Microsoft.Storage/storageAccounts@2025-01-01' = {
  name: 'stptuvcontent260911'
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'None'
      defaultAction: 'Deny'
      ipRules: [{ value: clientIp, action: 'Allow' }]
    }
  }
}
resource blobs 'Microsoft.Storage/storageAccounts/blobServices@2025-01-01' = {
  parent: storage
  name: 'default'
}
resource blobContainers 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-01-01' = [for name in ['ptu-content-configuration', 'ptu-content-processes', 'ptu-content-batches']: {
  parent: blobs
  name: name
  properties: { publicAccess: 'None' }
}]
resource queues 'Microsoft.Storage/storageAccounts/queueServices@2025-01-01' = {
  parent: storage
  name: 'default'
}
resource queueNames 'Microsoft.Storage/storageAccounts/queueServices/queues@2025-01-01' = [for name in ['content-pipeline-extract-queue', 'content-pipeline-map-queue', 'content-pipeline-evaluate-queue', 'content-pipeline-save-queue', 'ptu-content-claim-queue', 'ptu-content-dead-letter-queue']: {
  parent: queues
  name: name
}]

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2025-04-15' = {
  name: 'cosmos-ptuv-content-260911'
  location: location
  tags: tags
  kind: 'MongoDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    apiProperties: { serverVersion: '7.0' }
    capabilities: [{ name: 'EnableMongo' }]
    locations: [{ locationName: location, failoverPriority: 0, isZoneRedundant: false }]
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
    capacity: { totalThroughputLimit: 400 }
    publicNetworkAccess: 'Enabled'
    ipRules: [{ ipAddressOrRange: clientIp }]
    isVirtualNetworkFilterEnabled: false
    minimalTlsVersion: 'Tls12'
  }
}
resource database 'Microsoft.DocumentDB/databaseAccounts/mongodbDatabases@2025-04-15' = {
  parent: cosmos
  name: 'ptu-content-db'
  properties: {
    resource: { id: 'ptu-content-db' }
    options: { throughput: 400 }
  }
}

resource ai 'Microsoft.CognitiveServices/accounts@2025-12-01' = {
  name: 'aif-ptuv-content-260911'
  location: location
  tags: tags
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    allowProjectManagement: true
    customSubDomainName: 'aif-ptuv-content-260911'
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Deny'
      ipRules: [{ value: clientIp }]
      virtualNetworkRules: []
    }
  }
}
resource project 'Microsoft.CognitiveServices/accounts/projects@2025-12-01' = {
  parent: ai
  name: 'ptu-content-project'
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  properties: { displayName: 'ptu-content-project', description: 'Synthetic MCAPS Content Processing native evaluation' }
}
resource model 'Microsoft.CognitiveServices/accounts/deployments@2025-12-01' = {
  parent: ai
  name: 'gpt-5.1'
  sku: { name: 'GlobalStandard', capacity: 50 }
  properties: {
    model: { format: 'OpenAI', name: 'gpt-5.1', version: '2025-11-13' }
    raiPolicyName: 'Microsoft.Default'
    versionUpgradeOption: 'NoAutoUpgrade'
  }
}

resource appconfig 'Microsoft.AppConfiguration/configurationStores@2024-05-01' = {
  name: 'appcs-ptuv-content-260911'
  location: location
  tags: tags
  sku: { name: 'Standard' }
  properties: {
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    enablePurgeProtection: false
    dataPlaneProxy: { authenticationMode: 'Pass-through' }
  }
}
var openAiEndpoint = 'https://${ai.name}.openai.azure.com/'
var settings = {
  APP_STORAGE_BLOB_URL: 'https://${storage.name}.blob.core.windows.net'
  APP_STORAGE_QUEUE_URL: 'https://${storage.name}.queue.core.windows.net'
  APP_STORAGE_ACCOUNT_NAME: storage.name
  APP_COSMOS_DATABASE: database.name
  APP_COSMOS_CONTAINER_PROCESS: 'ptu-content-processes'
  APP_COSMOS_CONTAINER_SCHEMA: 'Schemas'
  APP_COSMOS_CONTAINER_SCHEMASET: 'ptu-content-schemasets'
  APP_COSMOS_CONTAINER_BATCHES: 'ptu-content-batches'
  APP_COSMOS_CONTAINER_BATCH_PROCESS: 'claimprocesses'
  APP_CPS_CONFIGURATION: 'ptu-content-configuration'
  APP_CPS_PROCESSES: 'ptu-content-processes'
  APP_CPS_PROCESS_BATCH: 'ptu-content-batches'
  APP_CPS_MAX_FILESIZE_MB: '20'
  APP_MESSAGE_QUEUE_EXTRACT: 'content-pipeline-extract-queue'
  APP_MESSAGE_QUEUE_INTERVAL: '5'
  APP_MESSAGE_QUEUE_PROCESS_TIMEOUT: '300'
  APP_MESSAGE_QUEUE_VISIBILITY_TIMEOUT: '180'
  APP_PROCESS_STEPS: 'extract,map,evaluate,save'
  APP_CPS_CONTENT_PROCESS_ENDPOINT: 'http://127.0.0.1:8113/'
  APP_CPS_POLL_INTERVAL_SECONDS: '3'
  CLAIM_PROCESS_QUEUE_NAME: 'claim-process-queue'
  DEAD_LETTER_QUEUE_NAME: 'ptu-content-dead-letter-queue'
  APP_CONTENT_UNDERSTANDING_ENDPOINT: 'https://${ai.name}.cognitiveservices.azure.com'
  APP_AI_PROJECT_ENDPOINT: 'https://${ai.name}.services.ai.azure.com/api/projects/${project.name}'
  APP_AZURE_OPENAI_ENDPOINT: openAiEndpoint
  APP_AZURE_OPENAI_MODEL: 'gpt-5.1'
  AZURE_OPENAI_ENDPOINT: openAiEndpoint
  AZURE_OPENAI_ENDPOINT_BASE: openAiEndpoint
  AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: 'gpt-5.1'
  AZURE_OPENAI_API_VERSION: '2025-03-01-preview'
  GPT5_ENDPOINT: openAiEndpoint
  GPT5_CHAT_DEPLOYMENT_NAME: 'gpt-5.1'
  GPT5_API_VERSION: '2025-03-01-preview'
  GLOBAL_LLM_SERVICE: 'AzureOpenAI'
  APP_LOGGING_LEVEL: 'WARNING'
  AZURE_PACKAGE_LOGGING_LEVEL: 'ERROR'
  AZURE_LOGGING_PACKAGES: 'azure,urllib3,httpx,openai'
  APP_RAI_ENABLED: 'True'
  AZURE_TRACING_ENABLED: 'False'
  APPLICATIONINSIGHTS_CONNECTION_STRING: ''
}
resource keys 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = [for item in items(settings): {
  parent: appconfig
  name: item.key
  properties: { value: item.value, contentType: 'text/plain' }
  dependsOn: [configOwner]
}]

resource storageRoles 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for role in ['ba92f5b4-2d11-453d-a403-e96b0029c9fe', '974c5e8b-45b9-4653-ba55-5f855dd0fb88']: {
  scope: storage
  name: guid(storage.id, principalId, role)
  properties: { principalId: principalId, principalType: 'User', roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', role) }
}]
resource aiRoles 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for role in ['5e0bd9bd-7b93-4f28-af87-19fc36ad61bd', 'a97b65f3-24c7-4388-baec-2e87135dc908']: {
  scope: ai
  name: guid(ai.id, principalId, role)
  properties: { principalId: principalId, principalType: 'User', roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', role) }
}]
resource configReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: appconfig
  name: guid(appconfig.id, principalId, '516239f1-63e1-4d78-a4de-a74fb236a071')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '516239f1-63e1-4d78-a4de-a74fb236a071')
  }
}
resource configOwner 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: appconfig
  name: guid(appconfig.id, principalId, '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b')
  }
}
output appConfigEndpoint string = appconfig.properties.endpoint
output storageAccountName string = storage.name
output cosmosAccountName string = cosmos.name
output aiAccountName string = ai.name
output openAIEndpoint string = openAiEndpoint
output projectEndpoint string = 'https://${ai.name}.services.ai.azure.com/api/projects/${project.name}'
output modelDeploymentName string = model.name
