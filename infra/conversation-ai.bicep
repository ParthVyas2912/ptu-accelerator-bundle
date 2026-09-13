targetScope = 'resourceGroup'

var tags = {
  workload: 'accelerator-eval'
  owner: 'parth'
  environment: 'mcaps-nonprod'
  accelerator: 'conversation'
  protected: 'false'
}
var location = 'swedencentral'

resource account 'Microsoft.CognitiveServices/accounts@2025-12-01' = {
  name: 'aif-ptu-conversation-7d804f70'
  location: location
  kind: 'AIServices'
  tags: tags
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    allowProjectManagement: true
    customSubDomainName: 'aif-ptu-conversation-7d804f70'
    disableLocalAuth: true
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      virtualNetworkRules: []
      ipRules: []
    }
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-12-01' = {
  parent: account
  name: 'proj-ptu-conversation'
  location: location
  kind: 'AIServices'
  identity: { type: 'SystemAssigned' }
  properties: {}
}

var modelDefinitions = [
  { name: 'gpt-5.2', version: '2025-12-11' }
  { name: 'text-embedding-3-small', version: '1' }
]
@batchSize(1)
resource models 'Microsoft.CognitiveServices/accounts/deployments@2025-12-01' = [for model in modelDefinitions: {
  parent: account
  name: model.name
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: model.name
      version: model.version
    }
    versionUpgradeOption: 'NoAutoUpgrade'
    raiPolicyName: 'Microsoft.Default'
  }
}]

output accountId string = account.id
output projectId string = project.id
output accountEndpoint string = account.properties.endpoint
output serviceEndpoints object = account.properties.endpoints
output projectEndpoint string = project.properties.endpoints['AI Foundry API']
output modelDeployments array = [for (model, i) in modelDefinitions: {
  name: model.name
  version: model.version
  id: models[i].id
  sku: 'GlobalStandard'
  capacity: 10
}]
